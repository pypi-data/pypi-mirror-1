'''``%prog [-T title][-U url] [--enable-htaccess] [OPTIONS] archive/dir``

Build a python package index based on the egg files in the directory specified
by the ``archive/dir argument``. This argument specifies the file
system root directory in which the distributions are stored and where the index
will be built.

Options-Summary:

    Don't write anything to disk: ``--dry-run, -N``

    Page generation::

        --index-url --index-pagename --downloads-path
        --master-template --project-template

    Logging (use ``-N --log-content=INFO`` to preview generated config files)::

        --log-level --log-content

    Config filename control::

        --project-uri-remap

'''
import re
import os, sys, types, textwrap, distutils
from posixpath import join as posix_joinpath
from urlparse import urlparse, urlunparse
from itertools import chain
from os.path import *
from glob import glob
from socket import gethostname
from md5 import md5
import optparse, logging

RE_STARTS_WITH_NON_DIGIT=re.compile(r'[^\d]+').match

log = logging.getLogger(
    __name__ != '__main__' and __name__
    or splitext(basename(__file__))[0]
    )

# Defer pkg_resources & setuptools import until we have the index_root.
pkg_resources=None
setuptools=None


DEFAULT_MASTER_INDEX_TEMPLATE_required_keys = (
        'index_title PACKAGE_INDEX_URLS'
        ).split()
DEFAULT_MASTER_INDEX_TEMPLATE_fmt=u'''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">

<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(index_title)s</title>
</head>
<body>

<h1>Using easy_install with this index</h1>

For general information on using setuptools and easyinstall look <a
href="http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install">here</a>.
Note that you will need to make use of the <code>--index-url</code>
and, possibly, the <code>--find-links</code> options in order to
refer easy_install to this package index.

<h1>List of Packages</h1>
%(PACKAGE_INDEX_URLS)s
</body>
</html>
'''

DEFAULT_PROJECTVERSION_PAGE_required_keys=(
        'index_name project_name latest_version DOWNLOAD_LINKS'
        ).split()
DEFAULT_PROJECTVERSION_PAGE_fmt=u'''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(index_name)s: %(project_name)s %(this_version)s</title>
</head>
<body>
<h1>%(project_name)s %(this_version)s</h1>

<p>This page lists every distribution of %(project_name)s at version
<strong>%(this_version)s</strong> that is available for download from
<strong>this</strong> index.</p>

<p>The most recent version available in this index is
<code>%(latest_version)s</code>. The <a
href="http://cheeseshop.python.org/pypi/"> official community index</a> may
have a more recent distribution for this project.</p>

%(DOWNLOAD_LINKS)s
</body>
</html>
'''


MASTER_IDX_HREF_fmt='''\
<a href="%(projects_path)s%(project_name)s/%(version)s">\
%(project_name)s %(version)s</a>\
'''

DISTDOWNLOAD_HREF_fmt='''\
<a href="%(downloads_server_url)s%(downloads_path)s%(distribution_basename)s\
#md5=%(md5_digest)s" rel="nofollow">%(distribution_basename)s</a>\
'''


def master_idx_href(dist, projects_path=''):
    return MASTER_IDX_HREF_fmt % dict(
            projects_path=projects_path,
            project_name=dist.project_name,
            version=dist.version
            )

def distdownload_href(downloads_server_url, distribution_basename, md5_digest,
        downloads_path=''):
    return DISTDOWNLOAD_HREF_fmt % locals()



def abs_normpath(path, *parts):
    if parts:
        return normpath(
                join(abspath(expanduser(path)), expanduser(join(*parts)))
                )
    else:
        return normpath(
            join(abspath(expanduser(path)))
            )




def import_setuptools(index_root):
    """import setuptools.

    Using the following heuristic:

    1. If a setuptools.pth file exists in the index root then extend the
    path, via ``site.addsitedir`` with the directories listed in that file.

    2. Attempt a normal import

    3. If we failed to import setuptools (either via setuptools.pth or via
    standard installation for the python executing this module) then look
    for the *lexically* highest setuptools egg in the index root. If there
    is one, add it to the path and try the import again.

    In all cases if the heuristic is unable to import setuptools, the normal
    ImportError will be raised.

    """

    global pkg_resources, setuptools
    setuptools_pth = join(index_root, 'setuptools.pth')
    if isfile(setuptools_pth):
        import site
        for ln in file(setuptools_pth):
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            log.info('Adding sitedir: %s' % ln)
            site.addsitedir(ln)
    try:
        setuptools = __import__('setuptools')
        __import__('setuptools.package_index')
        pkg_resources = __import__('pkg_resources')
    except ImportError:
        setuptools_eggs = glob(
            '%s/setuptools-*-py%s.egg' % (
                index_root, sys.version[:3]
                )
            )
        if not setuptools_eggs:
            raise
        setuptools_eggs.sort()
        sys.path.insert(0, setuptools_eggs[-1])
        setuptools = __import__('setuptools')
        __import__('setuptools.package_index')
        pkg_resources = __import__('pkg_resources')
        log.info('Using indexed setuptools: %s' % setuptools_eggs[-1])
        import setuptools.package_index



def update_egg_distributions(index_root, distributions, project_distributions):
    dist_added=[]
    dist_ext = '.egg'
    for abs_eggfn in glob('%s/*%s' % (index_root, dist_ext)):
        location, basefilename = split(abs_eggfn)
        dist = pkg_resources.Distribution.from_location(
                location, basefilename)
        egg_name = dist.egg_name()
        dist_name = egg_name + dist_ext
        if dist_name in distributions:
            continue
        distributions.add(dist_name)
        dist_added.append(dist)
        content = file(abs_eggfn).read()
        md5_digest = md5(content).hexdigest()
        project_distributions.setdefault(dist.project_name, []).append(
                (dist.parsed_version, dist, basefilename, md5_digest)
                )
    return dist_added

def update_distributions(index_root, distributions, project_distributions):

    # list the files in the index_root, only ever does one iteration of
    # os.walk - using in preference to os.listdir because its more 
    # convenient.

    dist_added=[]
    log.info('archive formats:' + ', '.join(
        list(distutils.archive_util.ARCHIVE_FORMATS)
        ))
    for dirpath, dirnames, filenames in os.walk(index_root, topdown=True):

        if 0:
            # Err, no. If its not a file then don't index it. We only want
            # to generate md5 digests of properly archived distributions.
            # And not attempting any magic here means its safe to have a set
            # of development directories *under* the index directory.
            eggdirs=[dn for dn in dirnames
                    if dn.endswith('.egg') or dn.endswith('.egg.zip')
                    ]
        # del dirnames[:] redundant, we always break out after the first
        # iteration.

        for candidate in filenames:
            dists = list(setuptools.package_index.distros_for_location(
                    dirpath, candidate)
                    )
            if not dists:
                continue

            for_index = []
            for dist in dists:
                if not dist.version:
                    continue
                for_index.append(dist)
            if len(for_index) > 1:
                keep = []
                for d in for_index:
                    if RE_STARTS_WITH_NON_DIGIT(d.version):
                        log.warning((
                        'Discarding ambiguous project/version '
                        'interpretation: %s/%s\n\t'
                        'Becuase the version part starts with a non digit'
                        ) % (d.project_name, d.version))
                        continue
                    keep.append(d)
                if not keep:
                    log.warning('Completely ignoring candidate "%s"', candidate)
                    continue
                for_index[:] = keep[:]

            for dist in for_index:
                dist_added.append(dist)
                distributions.add(candidate)

                md5_digest = md5(
                        file(join(dirpath, candidate)).read()
                        ).hexdigest()
                project_distributions.setdefault(
                         dist.project_name, []
                         ).append(
                    (dist.parsed_version + (dist.precedence,), dist,
                    candidate, md5_digest)
                    )
        return dist_added


def unique_rewrites(name):
    unique = {}
    safe_name = pkg_resources.safe_name(name)
    return [n for n in [safe_name, safe_name.lower(), name, name.lower()]
            if n not in unique and not unique.__setitem__(n,None)]


def validate_page_template(required_keys, candidate_template):
    missing = []
    for k in required_keys:
        if k and '%(' + k + ')s' not in candidate_template:
            missing.append(k)
    if missing:
        raise KeyError((
            'The following keys were missing from the template:' +
            ', '.join(missing))
            )
    return True


def get_page_template_fromfile(required_keys, filename, default):
    """load and validate a %(key)s style page template."""

    if not isinstance(default, types.StringTypes):
        default_page_template = default()
    else:
        default_page_template = default
    if not filename:
        try:
            validate_page_template(required_keys, default_page_template)
            return default_page_template
        except KeyError, e:
            msg = ((
            'The supplied default template string was missing expansion keys '
            'that are considered critical to correct index page '
            'generation. ERROR DETAILS:\n%s') % str(e))
            log.error(msg)
            if isinstance(default, types.StringTypes):
                raise KeyError(msg)
            return default(KeyError(msg))
    try:
        page_template = file(filename).read()
    except IOError:
        msg = ('Supplied template filename "%s" does not exist' %
                filename)
        log.error(msg)
        if not isinstance(default, types.StringTypes):
            default(IOError(msg))
        return default_page_template
    try:
        validate_page_template(required_keys, page_template)
    except KeyError, e:
        msg = ((
        'The supplied template file "%s" was missing expansion keys '
        'that are considered critical to correct index page '
        'generation. ERROR DETAILS:\n%s'),
        filename, str(e))
        log.error(msg)
        if not isinstance(default, types.StringTypes):
            default(IOError(msg))
        return default_page_template
    return page_template


class ApacheConfig_Error(Exception):
    pass

class ApacheConfig_DirectiveDisallowed(ApacheConfig_Error):
    pass
class ApacheConfig_SectionDirectiveMissing(ApacheConfig_Error):
    pass

def format_apache_section(directives, leading_comment='',
        valid_directives=None, require_directives=None):
    """Turn a list of directives into an apache config section.

    :Parameters:
        directives
          The list of directives
        leading_comment
          The comment that should precede the section or the empty string
          if no leading comment is required.
        valid_directives
          A list of directives that are allowed in the section. If any
          directives appear that are not in this list an
          `ApacheConfig_DirectiveDisallowed`
          exception is raised. Set `valid_directives` to None to allow
          all directives
        require_directives
          A list of directives that must be present in order for the
          section to be considered complete. If any are missing
          an `ApacheConfig_SectionDirectiveMissing` exception is raised.

    """
    directive_map={}
    order=[]
    parts = []
    if leading_comment:
        parts.append(format_apache_directive('', comment=leading_comment)[1])

    for item in directives:
        if not item:
            continue
        k, content = item
        if (valid_directives is not None
                and k not in valid_directives):
            raise ApacheConfig_DirectiveDisallowed(k)
        order.append(k)
        parts.append(content)
        directive_map.setdefault(k, []).append(content)
    if require_directives is not None:
        missing_keys = set(require_directives) - set(order)
        if missing_keys:
            raise ApacheConfig_SectionDirectiveMissing(list(missing_keys))
    return parts, directive_map, order


def format_apache_directive(directive, comment='', comment_before=True,
        directive_indent=1, directive_indent_istab=True):
    """Format an optionaly commented apache directive.

    Makes resonable efforts to retain comment indentation but its not
    perfect.

    Allows comments sections with an empty `directive`

    :Parameters:
        directive
          The directive and its value or an empty string.
        comment
          The comment that should accompany the directive
        comment_before
          If True, Provided that the `directive` is non empty, then
          the comment will preced the directive. Otherwise it goes
          afterwards.
        directive_indent
          Number of units to indent the directive, relative to the comment.
          If `directive_indent_istab` is true, the default, then the units
          specify the number of tabs. Otherwise, ' ' is used for indentation
          and this directive sets the number of spaces to insert.
        directive_indent_istab
          If True, tabs are used for indentation, otherwise a single ' ' is
          used.
    """
    directive_key = None
    if directive and not directive.split(None, 1)[1].strip():
        directive = (
            '# ' + directive + ' # -- no appropriate default' + '\n'
            )
    elif directive:
        directive_key = directive.split()[0].strip()
        if directive_key.startswith('#'):
            directive_key = directive_key.split('#', 1)[1].strip()
        ws = directive_indent_istab and '\t' or ' '
        directive = ws * directive_indent + directive + '\n'
    else:
        directive = '\n'
    if not comment:
        return directive_key, directive
    comment_paras = [[]]
    def is_indented_or_blank(ln):
        return (ln.startswith(' ') or ln.startswith('\t'))

    for ln in textwrap.dedent(comment).split('\n') + ['']:
        if not is_indented_or_blank(ln):
            if (comment_paras[-1] and is_indented_or_blank(
                comment_paras[-1][0])):
                comment_paras[-1] = textwrap.wrap('\n'.join(
                    comment_paras[-1])
                    )
                comment_paras.append([])
            comment_paras[-1].append(ln)
        else:
            if (comment_paras[-1] and not is_indented_or_blank(
                comment_paras[-1][0])):
                comment_paras[-1] = textwrap.wrap('\n'.join(
                    comment_paras[-1])
                    )
                comment_paras.append([])
            comment_paras[-1].append(ln)

    comment = '\n'.join(
        ln and '# ' + ln or '' for ln in chain(*comment_paras)
        if ln
        )
    if comment_before:
        return directive_key, comment + (directive and '\n' + directive or '')
    return directive_key, (directive and diretive + '\n' or '') + comment


class MasterIndex(object):
    def __init__(self, opts):
        self.opts = opts
        self.MASTER_INDEX_NAME=getattr(opts, 'index_title',
                self.MASTER_INDEX_NAME)
        self.MASTER_INDEX_URL=getattr(opts, 'index_url',
                self.MASTER_INDEX_URL)
        self.DOWNLOADS_SERVER_URL=getattr(opts, 'downloads_server_url',
                self.DOWNLOADS_SERVER_URL)
        self.PROJECTS_PATH=getattr(opts, 'projects_path',
                self.PROJECTS_PATH)
        self.DOWNLOADS_PATH=getattr(opts, 'downloads_path',
                self.DOWNLOADS_PATH)

    MASTER_INDEX_NAME='cheeseboard.localhost'
    MASTER_INDEX_URL='http://localhost/'
    DOWNLOADS_SERVER_URL='http://localhost/'
    PROJECTS_PATH='/'
    DOWNLOADS_PATH='/'

    page_template_required_keys = DEFAULT_MASTER_INDEX_TEMPLATE_required_keys
    page_template = DEFAULT_MASTER_INDEX_TEMPLATE_fmt


    def render_index(self):
        assert set(self.page_template_required_keys).issubset(
                'index_title PACKAGE_INDEX_URLS'.split()
                ), (
                'This method should be over-ridden to provide at least '
                'the following keys: %s'
                ) % ', '.join(list(self.page_template_required_keys)
                        )
        return self.page_template % dict(
                index_title=self.MASTER_INDEX_NAME,
                PACKAGE_INDEX_URLS='<br>\n'.join(self.master_idx_hrefs)
                )

    def ordered_rewrites(self):
        return ((k, self.rewrites[k]) for k in self.rewrites_order)



class ProjectListing(object):


    page_template_required_keys = DEFAULT_PROJECTVERSION_PAGE_required_keys
    page_template = DEFAULT_PROJECTVERSION_PAGE_fmt


    def __init__(self, opts):
        self.opts = opts
        templatefn = getattr(opts, 'project_template', False)

    def render_pages(self, index_name, variables=None):
        if variables is None:
            variables = {}
        variables.setdefault('index_name', index_name)

        genkeys = 'project_name DOWNLOAD_LINKS latest_version'.split()
        assert set(self.page_template_required_keys).issubset(
                variables.keys() + genkeys
                ), (
                'This method should be over-ridden to provide at least '
                'the following keys: %s'
                ) % ', '.join(k for k in self.page_template_required_keys
                        if k not in genkeys
                        )

        # Allow the caller to prefix the list of download links
        DOWNLOAD_LINKS=variables.pop('DOWNLOAD_LINKS', '')
        latest_version = self.pages[self.page_order[0]]['dists'][0].version
        # There is exactly one page per distinct project/version.
        # There may be many distributions, with distinct formats, at
        # each version. page_name *includes* the version. the distributions
        # and hrefs are assumed to be sorted according to distribution
        # precedence (setuptools defaults to egg as highest).
        for page_name in self.page_order:
            dists = self.pages[page_name]['dists']
            project_name=dists[0].project_name
            download_hrefs = self.pages[page_name]['download_hrefs']
            for i in xrange(0, len(dists)):
                assert project_name == dists[i].project_name, (
                '"%s" != "%s"' % (project_name, dists[i].project_name)
                )
            yield page_name, self.page_template % dict(
                variables,
                latest_version=latest_version,
                this_version=dists[i].version,
                project_name=project_name,
                DOWNLOAD_LINKS=DOWNLOAD_LINKS + '<br>\n'.join(
                    download_hrefs
                    )
                )



def build_index(opts, distributions, project_distributions,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing):
    """Collect the `distributions` together indexed by project"""


    MasterIndex.page_template = get_page_template_fromfile(
            MasterIndex.page_template_required_keys,
            getattr(opts, 'master_template', False),
            MasterIndex.page_template)
    ProjectListing.page_template = get_page_template_fromfile(
            ProjectListing.page_template_required_keys,
            getattr(opts, 'project_template', False),
            ProjectListing.page_template)
    mi = MasterIndex(opts)
    mi.rewrites_order=[]
    mi.rewrites={}
    mi.master_idx_page_names={}
    mi.master_idx_hrefs=[]
    mi.master_rewrites={}
    mi.projects_order=[]
    mi.projects={}
    for k in sorted(project_distributions):
        for distinfo in sorted(project_distributions[k], reverse=True):
            pver_precedence, dist, basefn, digest = distinfo

            pn = dist.project_name
            if pn not in mi.projects:
                pl = mi.projects[pn] = ProjectListing(opts)
                # Project renames across versions are effectively
                # different projects as far as this index is concerned.
                pl.project_name = pn
                mi.projects_order.append(pn)
                pl.page_order=[]
                pl.pages={}
            else:
                pl = mi.projects[pn]
            pn_safe = pkg_resources.safe_name(pn)
            pn_variants = unique_rewrites(pn)
            pv = dist.version.lower()
            page_name = ('%s-%s.html' % (pn_safe, pv)).lower()
            if page_name not in pl.pages:
                pl.page_order.append(page_name)
                pl.pages[page_name] = dict(
                    version=pv,
                    dists=[],
                    download_hrefs=[],
                    basefilenames=[],
                    digests=[]
                    )
            page = pl.pages[page_name]

            # mixed case version strings are an abomination and should not be
            # tolerated. However, distribution archives with ambiguous
            # project-name-VER, splits would trip an assertion here
            assert True or dist.version == page['version'], (
                    'dist.version:"%s", page.version:"%s"' % (
                        dist.version, page['version']
                        )
                    )

            page['dists'].append(dist)
            page['basefilenames'].append(basefn)
            page['digests'].append(digest)
            page['download_hrefs'].append(distdownload_href(
                mi.DOWNLOADS_SERVER_URL, basefn, digest,
                downloads_path=mi.DOWNLOADS_PATH[1:])
                )

            if page_name not in mi.master_idx_page_names:

                mi.master_idx_page_names[page_name]=True

                mi.master_idx_hrefs.append(
                        master_idx_href(dist, projects_path = mi.PROJECTS_PATH)
                        )

                # re-direct unversioned requests to the most recent page
                if pn not in mi.rewrites:
                    # we sort newest to oldest above so if its not in yet,
                    # this page_name is the one we want.
                    for k in pn_variants:
                        k = k + '/'
                        if k not in mi.rewrites:
                            mi.rewrites[k] = page_name
                            mi.rewrites_order.append(k)
                for k in pn_variants:
                    k = '%s/%s' % (k, pv)
                    mi.rewrites[k] = page_name
                    mi.rewrites_order.append(k)

    return mi


def write_full_index(contentwriter, opts,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing):

    distributions=set([])
    project_distributions={}

    update_distributions(opts.index_root,
            distributions, project_distributions)

    mi = build_index(opts, distributions, project_distributions,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing
        )
    for pn in mi.projects_order:
        pl = mi.projects[pn]
        contentwriter.write_project_items(mi, pl)
    contentwriter.write_master_index(mi)
    contentwriter.write_apache_directives(mi)



class IndexWriter(object):
    def __init__(self, opts):
        self.opts = opts

    def write_output_file(self, outfilename, content,
            log_level=None):

        if not self.opts.dry_run:
            file(outfilename, 'w').write(content)
            log.info('wrote:' + outfilename)
        else:
            log.info('dry-wrote:' + outfilename)
        if log_level is None:
            log_level = self.opts.log_content
        log.log(log_level,
                'BEGIN-FILE:%s:\n%s\nEND-FILE:%s',
                outfilename, content, outfilename)

    def write_project_items(self, masterindex, projectlisting, path='.'):
        """Write all items for each version of the project in `projectlisting`

        """

        mi = masterindex
        pl = projectlisting
        log.info('%s: %s [%s]', pl.project_name, ', '.join(
            [pl.pages[pn]['version'] for pn in pl.page_order]),
            ', '.join([', '.join(pl.pages[pn]['basefilenames'])
                for pn in pl.page_order])
            )

        for page_name, content in pl.render_pages(mi.MASTER_INDEX_NAME):
            outfn = normpath(join(self.opts.index_root, path, page_name))
            self.write_output_file(outfn, content)

    def write_master_index(self, masterindex, path='.'):
        """Write all items associated with the master index page."""

        mi = masterindex
        index_content = mi.render_index()
        index_pagename = getattr(self.opts, 'index_pagename',
                'index.html')
        project_uri_remap = getattr(self.opts, 'project_uri_remap',
                'project-index.txt'
                )
        outfn = normpath(join(self.opts.index_root, path, index_pagename))
        self.write_output_file(outfn, index_content)

        outfn = normpath(join(self.opts.index_root, path, project_uri_remap))
        self.write_output_file(outfn,
            '\n'.join('%s %s' % (s, t) for s,t in mi.ordered_rewrites())
            )


    def write_apache_directives(self, masterindex, path='.'):
        vhostfn = abs_normpath(
                self.opts.index_root, self.opts.apache_vhost_file
                )
        dirdirectfn = abs_normpath(
                self.opts.index_root,
                self.opts.apache_dirdirect_file
                )

        htaccess_enable = self.opts.enable_htaccess

        if not htaccess_enable:
            dn = dirname(self.opts.htaccess_file)
            if not dn:
                htaccessfn = abs_normpath(
                    self.opts.index_root,
                    'NOTENABLED' + self.opts.htaccess_file
                    )
            else:
                htaccessfn = abs_normpath(self.opts.index_root,
                        'NOTENABLED'+bn
                        )
        else:
            htaccessfn = abs_normpath(self.opts.index_root,
                    self.opts.htaccess_file
                    )

        log_level = getattr(self.opts, 'log_config',
                    getattr(self.opts, 'log_content', logging.INFO)
                    )

        opts = self.opts
        mi = masterindex

        document_root = opts.index_root
        project_index = splitext(opts.project_uri_remap)[0]
        project_index_filename = join(
                opts.index_root, opts.project_uri_remap
                )

        rewrite_log_filename = join(
                document_root, '%s.rewrite.log' % (
                mi.MASTER_INDEX_NAME)
                )

        vhost_comment='''\
        The follwing directives represent the minimum that are neccessary at
        the server or vhost level in order to get the package index uri
        re-writes to functioning. Pay particular attention to the placement of
        RewriteEngine - it must be set in both the host/server context and the
        index root directory context in order for the re-writing to function.
        Further note that `Options FollowSymLinks` MUST be enabled for the
        index root directory if you are making use of .htaccess. Despite the
        usual admonitions about security it is by far the most convenient means
        to manage an index that is for personal use. By default the directives
        necessary to enable .htaccess at the vhost level are generated but
        commented out and an appropriate .htaccess file is written to
        `%(htaccess_filename)s'. If the index was built with htaccess support
        explicitly enabled then the vhost directives to turn it on are
        uncommented and the htaccess file is written to the file `.htaccess'

        Your package index was built under:
            "%(document_root)s"

        The re-write map that deals with safe project naming and adhering to
        the PyPI requirements on the URI space is:
            "%(project_index_filename)s"

        If you set the RewriteLogLevel to 3 or more (default 0 means off) 
        mod_rewrite will put usefull information in this file:
           "%(rewrite_log_filename)s"


        ''' % dict(
                document_root=document_root,
                project_index_filename=project_index_filename,
                rewrite_log_filename=rewrite_log_filename,
                htaccess_filename=htaccessfn
                )
        server_name = opts.server_name
        server_name_comment = '''\
        The server name is taken from the master index url - (Note that
        the index-url is baked into all the download links).'''

        server_alias = opts.server_alias

        server_alias_comment = '''\
                If the dot seperated fields of the master index name form a non
                empty prefix of the ServerName then it is sugested as a
                ServerAlias. "-- no suitable default" means the index name is
                not related to the server name in a (trivialy) DNS compatible
                way OR that the FQDN of the server and it index name are
                the same.'''

        vhost_directives_require=(
            'ServerName DocumentRoot '
            'RewriteEngine RewriteLog RewriteMap'
            ).split()

        vhost_directives_allow=vhost_directives_require[:]
        vhost_directives_allow.append('ServerAlias')

        vhost_directives = [

            format_apache_directive(
            'ServerName ' + server_name,
            comment=server_name_comment
            ),

            format_apache_directive(
            server_alias and 'ServerAlias ' + server_alias,
            comment=server_alias_comment
            ),

            format_apache_directive(
            'DocumentRoot ' + document_root,
            comment='''\
            The DocumentRoot path is the filesystem root in which the
            index was built.'''),

            format_apache_directive(
            'RewriteEngine on', comment='''\
            It is necessary to enable the rewrite engine in both the
            host or server context AND in directory context of the
            index root (usualy the DocumentRoot) in order to enable
            htaccess support.'''),

            format_apache_directive(
            'RewriteLogLevel 0'),

            format_apache_directive(
            'RewriteLog ' + rewrite_log_filename),

            format_apache_directive(
            'RewriteMap ' + project_index + ' txt:' +
            project_index_filename, comment='''\
            Note that it is not possible to set the RewriteMap
            directive in a directory or a .htaccess context.''')

            ]

        (vhost_content, vhost_directive_map, vhost_directive_order
                ) = format_apache_section(
                vhost_directives, leading_comment=vhost_comment,
                    require_directives=vhost_directives_require
                    )
        self.write_output_file(vhostfn,
            '\n'.join(vhost_content),
                log_level = log_level
                )

        dirdirect_comment = '''
        The directory context directives neccessary for the package index
        built under this directory.

        If the index was built with the expectation that .htaccess support
        would be enabled then some of the directives are commented out. Those
        directives are the *only* directives necessary in the .htaccess file.
        Simply uncommenting these directives is enough to make the index work
        if .htaccess support is disabled.

        Using mod_rewrite we re-write anything explicitly listed in the index
        to the key target, which should be appropriate project page for the
        request (versioned or otherwise). This assumes that "%(project_index)s"
        is the name of the package project mod_rewrite txt:map configured in
        the server/host context that owns this directory. At the time this
        file was generated, the map file was writen to:
            "%(project_index_filename)s"

        If the index is built to be hosted under a non root uri then we enable
        a RewriteBase option to normalise the re-written uris for further
        processing.

        Note that we also fix the trailing slash via a redirect when we see
        `uri/Project` on its own, provided that `Project/` can be found in the
        index. We do NOT do this for the version uris as they refer to the
        actual resources, ie Foo/1.0 *is* a page.''' % dict(
                project_index=project_index,
                project_index_filename=project_index_filename
                )


        dirdirect_directives_require = (
            'AddType RewriteEngine Options AllowOverride '
            'Order allow RewriteCond RewriteRule').split()
        dirdirect_directives_allow = dirdirect_directives_require[:
                ] + ['RewriteBase']

        dirdirect_directives = [

            format_apache_directive(
                    (htaccess_enable and '#' or '') +
            'AddType application/zip .egg', comment='''\
            Arrange for .egg files to be served as the appropriate content
            type. If commented out then it is assumed to be configured via the
            .htaccess file in effect for this directory context.'''),

            ('RewriteEngine', vhost_directive_map['RewriteEngine'][0]),

            format_apache_directive(
                    (not htaccess_enable and '#' or '') +
            'Options +FollowSymLinks', comment='''\
            FollowSymLinks MUST be enabled if you want to manage the
            index re-writes mostly in .htacess. The apache documentation (v
            2.0.xx) contains further information on this issue.'''),

            format_apache_directive(
                (not htaccess_enable and '#' or '') +
            'AllowOverride All', comment='''\
            Allow all directives to be overriden in .htaccess files in this
            directory context (Note: `FollowSymLinks` must also be enabled to
            get htaccess working with mod_rewrite).'''),

            format_apache_directive(
            'Order allow,deny'),
            format_apache_directive(
            'allow from all'),

            self.opts.projects_path != '/' and format_apache_directive(
                    (htaccess_enable and '#' or '') + (
                        'RewriteBase %s' % self.opts.projects_path[:-1]),
                comment='''\
                The pages in this index expect to be hosted under this uri:
                '''),

            format_apache_directive((htaccess_enable and '#' or '') + (
            'RewriteCond ${%s:$1|NOT_FOUND} =NOT_FOUND' % project_index),
            comment='''\
            This set of conditions and subsequent redirect fixes the
            trailing slash problem for project pages that are available
            in the index.'''),
            format_apache_directive((htaccess_enable and '#' or '') + (
            'RewriteCond ${%s:$1/|NOT_FOUND} !=NOT_FOUND' % project_index)),
            format_apache_directive((htaccess_enable and '#' or '') + (
            'RewriteRule ^(.*)$ $1/ [R]')),

            format_apache_directive(
                (htaccess_enable and '#' or '') + (
            'RewriteCond ${%s:$1|NOT_FOUND} !=NOT_FOUND'
                    ) % project_index,
                comment='''
                This condition and subsequent rule maps project/version
                and project/ uris to the appropriate html file in the
                index directory.'''),

            format_apache_directive((htaccess_enable and '#' or '') + (
            'RewriteRule ^(.*)$ ${%s:$1} [L]' % project_index
                ))
            ]

        (dirdirect_content, dirdirect_map, dirdirect_order
                ) = format_apache_section(dirdirect_directives,
                        leading_comment=dirdirect_comment,
                        valid_directives = dirdirect_directives_allow,
                        require_directives = dirdirect_directives_require
                        )

        self.write_output_file(dirdirectfn,
            '\n'.join(chain(
                ['<Directory %s>' % document_root],
                dirdirect_content,
                ['</Directory>'])),
                log_level = log_level
                )

        htaccess_comment='''\
        This .htaccess file assumes the server (or vhost) config has:

         1. loaded the an appropriate mod_rewrite txt map and configured it
         with the name "%(project_index)s".

         2. Turned on the FollowSymlinks option for the directory context
         that owns the directory in which this .htaccess file lives.

         3. Set RewriteEngine on in *both* the server/host context AND
         the directory context in which this .htaccess file lives.

        Using mod_rewrite we re-write anything explicitly listed in the index
        to the key target, which should be appropriate project page for the
        request (versioned or otherwise). This assumes that "%(project_index)s"
        is the name of the package project mod_rewrite txt:map configured in
        the server/host context that owns this directory. At the time this
        .htaccess file was generated, the map file was writen to:
            "%(project_index_filename)s"


        If the index is built to be hosted under a non root uri then we enable
        a RewriteBase option to normalise the re-written uris for further
        processing.

        Note that we also fix the trailing slash via a redirect when we see
        `uri/Project` on its own, provided that `Project/` can be found in the
        index. We do NOT do this for the version uris as they refer to the
        actual resources, ie Foo/1.0 *is* a page.
        ''' % dict(
                project_index=project_index,
                project_index_filename=project_index_filename
                )
        htaccess_require_directives=(
            'AddType RewriteEngine RewriteCond RewriteRule'
            ).split()
        htaccess_allow_directives=htaccess_require_directives[:]
        htaccess_allow_directives.append('RewriteBase')

        htaccess_directives = [

            format_apache_directive(
            'AddType application/zip .egg', comment='''\
            Arrange for .egg files to be served as the appropriate content
            type.'''),

            ('RewriteEngine', vhost_directive_map['RewriteEngine'][0]),

            self.opts.projects_path != '/' and format_apache_directive(
                'RewriteBase %s' % self.opts.projects_path[:-1],
                comment='''\
                The pages in this index expect to be hosted under this uri:
                '''),
            format_apache_directive(
            'RewriteCond ${%s:$1|NOT_FOUND} =NOT_FOUND' % project_index,
            comment='''\
            This set of conditions and subsequent redirect fixes the
            trailing slash problem for project pages that are available
            in the index.'''),
            format_apache_directive(
            'RewriteCond ${%s:$1/|NOT_FOUND} !=NOT_FOUND' % project_index),
            format_apache_directive(
            'RewriteRule ^(.*)$ $1/ [R]'),

            format_apache_directive(
            'RewriteCond ${%s:$1|NOT_FOUND} !=NOT_FOUND' % project_index,
            comment='''
            This condition and subsequent rule maps project/version
            and project/ uris to the appropriate html file in the
            index directory.'''),

            format_apache_directive(
            'RewriteRule ^(.*)$ ${%s:$1} [L]' % project_index
            )
        ]
        (htaccess_content, htaccess_map, htaccess_order
                ) = format_apache_section(htaccess_directives,
                        leading_comment=htaccess_comment,
                        valid_directives=htaccess_allow_directives,
                        require_directives=htaccess_require_directives
                        )

        self.write_output_file(htaccessfn,
            '\n'.join(htaccess_content),
                log_level = log_level
                )



def build_parser(optparsekwopts=None, *optlists):
    """build an optparse.OptionParser from the argument option *lists*."""
    if optparsekwopts is None:
        optparsekwopts = {}
    parser=optparse.OptionParser(**optparsekwopts)
    if len(optlists)==1:
        add_options(parser, optlists[0])
        return parser
    add_options(parser, reduce(update_options, optlists))
    return parser


def add_options(parser, options):
    """add a list of options to an optparse.OptionParser compatible thing."""
    if not options:
        return
    for opt in options:
        if not isinstance(opt[-1], dict):
            opt.append({})
        try:
            parser.add_option(*opt[:-1], **opt[-1])
        except TypeError:
            print opt[:1]

def fmthelp(S):
    return '\n'.join(s.strip() for s in S.split('\n'))

OPTIONS_build=[
    ('--log-level', dict(default='INFO', help=fmthelp('''\
            `[default:%default]` Sets the logging level for messages issued by
            this package. It can be a number, or any one of the standard
            logging level strings "CRITICAL ERROR WARNING INFO DEBUG NOTSET".
            The level strings correspond, respectively, to the numbers [50, 40,
            30, 20, 10, 0].  NOTE: Set this options to 50 for *most quiet* or
            10 for *most verbose*.  Note that NOTSET will cause the logging
            level to be taken from the first parent handler that *does* set a
            level - usualy this will be the root logger '''))),
    ('--log-content', dict(default='DEBUG', help=fmthelp('''\
            `[default:%default]` Sets the logging level at which the content of
            generated pages and files will be logged. Valid values are exactly
            as per the --log-level option, except that value of NOTSET or 0 
            will have no effect'''))),
    ('--log-config', dict(default='DEBUG', help=fmthelp('''\
            `[default:%default]` Exactly as per --log-content. But applies,
            exclusively, to content that represents site/host configuration
            necessary for the full functionality of the index.
            (apache, etc)'''))),
    ('--print-log-conf', dict(default=False, action='store_true',
        help=fmthelp('''\
            `[default:%default]` Set this flag to print out information
            reflecting the application of the --log options. Use if you are
            not seeing the messages you expect.'''))),

    ('-T', '--index-title', dict(default='',
        help=fmthelp('''\
        `[default:generated via gethostname]` The title of the package index.
        This will be used as the ``<title>CONTENT</title>`` for the master
        index page.  By default this option value is generated using
        ``gethostname`` like this ``'cheeseboard.%s' % gethostname()``
        '''))),
    ('-U', '--index-url', dict(
         default='',
         help=fmthelp('''\
        `[default:generated via gethostname]` The public url of the package
        index main page. By default this option value is generated using
        ``gethostname`` like this ``'http://cheeseboard.%s/' % gethostname()``.
        The supplied url must end with ``/`` (trailing slash).'''))),
    ('--downloads-path', dict(default='', help=fmthelp('''\
        `[default:%default]` Generate download uris with a path that is
        distinct from the project-path implied by the ``--index-url`` option.
        If a non empty download-path is supplied then it is joined to the
        `path` component of the `index-url`.  For a definition of `path`
        component see `uriparse
        <http://docs.python.org/lib/module-urlparse.html>`_
        '''))),
    ('--index-pagename', dict(default='index.html', help=fmthelp('''\
        `[default:%default]` Sets the name of the master index page.'''))),
    ('--project-uri-remap', dict(default='project-index.txt',
        help=fmthelp('''\
        `[default:%default]` Sets the name of the mod_rewrite RewriteMap
        compatible text file that will contain the necessary *safe_name*
        re-mappings from project uris to the appropriate project page for the
        version implied in the uri. If there is no version information in
        the uri then the remap directs to the BEST VERSION as defined by
        setuptools semantics for version string interpretation.'''))),
    ('--master-template', dict(default='', help=fmthelp('''\
        `[default:%%default]` Use this option to set the file from which the
        master index page template will be read. If a relative path is provided
        it must be relative to ``--index-root``. The file should be a plain
        text file providing standard %%(key)s substitutions for the following
        keys: %s. Note that the keys indicated in this help text may be
        incorrect if you are running a version of this program that customise
        the replacement keys. The template file is checked for the presence of
        the actual keys needed at runtime by the class that generates the
        page.''' % ', '.join( MasterIndex.page_template_required_keys)
        ))),
    ('--project-template', dict(default='', help=fmthelp('''\
        `[default:%%default]` Use this option to set the file from which the
        project-version page template will be read. If a relative path is
        provided it must be relative to --index-root. The file should be a
        plain text file providing standard %%(key)s substitutions for the
        following keys: %s. Note that the keys indicated in this help text
        may be incorrect if you are running a version of this program that
        customise the replacement keys. The template file is checked for the
        presence of the actual keys needed at runtime by the class that
        generates the page.''' % ', '.join(
            ProjectListing.page_template_required_keys)
        ))),
    ('-N', '--dry-run', dict(default=False, action='store_true',
        help=fmthelp('''\
        `[default:%default]` Set this option to prevent this program from
        writing anything to disc. This option can be combined with
        logging options to re-direct most content production
        to standard out.'''))),

   ('--apache-vhost-file', dict(default='apache2-vhost.directives.conf',
        help=fmthelp('''\
        `[default:%default]` The name of the file to which all server/host
        level directives are written. These represent the minimum necessary
        server/host level directives needed in order for the index to work.
        **NOTE**: If the path is relative then it is relative to the directory
        specified as the index/root by the first non option argument.'''))),

    ('--apache-dirdirect-file', dict(
        default='apache2-dir.directives.conf',
        help=fmthelp('''\
        `[default:%default]` The name of the file to which all <Directory>
        context directives are written. These represent the minimum necessary
        ``</Directory>`` directives required in order for the index to work.
        **NOTE** This program always generates both a directory context config
        and the equivelent .haccess file. If .htaccess support is enabled
        (``--enable-htaccess``) then directives that duplicate the .htaccess
        functionality are commented out. To disable .htaccess at any time,
        simply make the usual arrangements at the server config level and
        uncomment the directory context directives.'''))),

    ('--htaccess-file', dict(default='.htaccess',
        help=fmthelp('''\
        `[default:%default]` The name of the file to which the .htaccess
        configuration directives are written. If `--enable-htaccess` is NOT
        also specified then the given file name will be decorated with the
        prefix ``NOTENABLED``.  '''))),
    ('--enable-htaccess', dict(default=False, action='store_true',
        help=fmthelp('''\
        `[default:%default]` Set this flag to make .htaccess on by default.
        This script allways generates configuration directives appropriate for
        use with or without htaccess support enabled. If htaccess support is
        disabled (this is the default) then all server/host and
        ``<Directory>`` directives pertaining to htaccess support are commented
        out and the generated htaccess file is prefixed with
        ``NOTENABLED``.''')))
    ]

def run(argv=None):
    parser = build_parser(dict(prog=basename(__file__), usage=__doc__),
            OPTIONS_build)
    opts, args = parser.parse_args(
            argv and argv[1:] or sys.argv[1:])

    # Allow numeric or semantic log level values but internally allways work
    # with numbers.
    for log_level_attr in 'log_level log_content log_config'.split():
        log_level=getattr(opts, log_level_attr, 'INFO')
        try:
            setattr(opts, log_level_attr, int(log_level))
            if opts.print_log_conf:
                print '%s to int("%s")' % (log_level_attr, log_level)
        except ValueError:
            try:
                setattr(opts, log_level_attr, logging._levelNames[log_level])
                if opts.print_log_conf:
                    print '%s to "%s", type %s' % (log_level_attr, log_level,
                            type(getattr(opts, log_level_attr))
                            )
            except KeyError:
                raise ValueError((
                    'The log_level string "%s" is not a registered '
                    'channel name. ') % str(log_level)
                    )

    log_format = getattr(opts, 'log_format', '%(message)s')
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(logging.Formatter(log_format))
    log.propogate = False
    log.addHandler(log_handler)
    log.setLevel(opts.log_level)
    if opts.print_log_conf:
        print 'Effective log level:', log.getEffectiveLevel()

    if not args:
        log.critical(
        'A single non option argument MUST be supplied. See --help'
        )
        sys.exit(-1)
    if not isdir(args[0]):
        log.critical(
        'The specified index root directory, "%s", does not exist.',
        args[0]
        )
        sys.exit(-1)

    if not opts.index_url:
        opts.index_url = 'http://cheeseboard.%s/' % gethostname()

    indexurl_parts = urlparse(opts.index_url)
    if not indexurl_parts[1]:
        log.error((
        'You provided a custom index-url that did not contain a ' +
        'network location (dns host name), see ' +
        'http://docs.python.org/lib/module-urlparse.html '
        'You provided: "%s"'), opts.index_url
        )
        sys.exit(-1)
    if not indexurl_parts[2].endswith('/'):
        log.error((
        'You must explicitly include a trailing slash when you supply a ' +
        'custom index url. You provided: "%s"'), opts.index_url
        )
        sys.exit(-1)
    if not indexurl_parts[0]:
        log.warning((
        'You provided a custom index-url that did not contain a URL ' +
        'scheme specifier, see ' +
        'http://docs.python.org/lib/module-urlparse.html ' +
        'You provided: "%s"'), opts.index_url
        )
    opts.index_url=urlunparse(indexurl_parts[:3]+('','',''))

    # Not adding the option for this just yet, but I want the defaults
    # exercised in the next release.
    if not getattr(opts, 'downloads_server_url', ''):
        opts.downloads_server_url=urlunparse(
                indexurl_parts[:2]+('','','', '')) + '/'
    downloadsurl_parts = urlparse(opts.downloads_server_url)
    if not downloadsurl_parts[1]:
        log.error((
        'You provided a custom downloads-server-url that did not contain a ' +
        'network location (dns host name), see ' +
        'http://docs.python.org/lib/module-urlparse.html '
        'You provided: "%s"'), opts.downloads_server_url
        )
        sys.exit(-1)
    if not downloadsurl_parts[2].endswith('/'):
        log.error((
        'You must explicitly include a trailing slash when you supply a ' +
        'custom downloads server url. You provided: "%s"'),
        opts.downloads_server_url
        )
        sys.exit(-1)
    if not downloadsurl_parts[0]:
        log.warning((
        'You provided a custom downloads-server-url that did not contain a ' +
        'URL scheme specifier, see ' +
        'http://docs.python.org/lib/module-urlparse.html ' +
        'You provided: "%s"'), opts.downloads_server_url
        )
    opts.downloads_server_url=urlunparse(downloadsurl_parts[:3]+('','',''))

    opts.projects_path=indexurl_parts[2]
    if opts.downloads_path:
        if not opts.downloads_path.endswith('/'):
            log.error((
            'You must explicitly include a trailing slash when you supply a ' +
            'custom downloads path. You provided: "%s"'), opts.downloads_path
            )
            sys.exit(-1)
        opts.downloads_path = posix_joinpath(opts.projects_path,
                opts.downloads_path)
    else:
        opts.downloads_path = opts.projects_path

    log.info('downloads-server-url: "%s"' % opts.downloads_server_url)
    log.info('downloads-path: "%s"' % opts.downloads_path)
    log.info('index-url: "%s"' % opts.index_url)


    server_name = opts.server_name = indexurl_parts[1]
    if not opts.index_title:
        opts.index_title = server_name

    server_alias = opts.server_alias = '.'.join([sp for ip, sp in
                zip(server_name.split('.'),
                    opts.index_title.split('.'))
                if ip and ip == sp]
                )
    if server_alias == server_name:
        server_alias = opts.server_alias = ''

    opts.index_root = abs_normpath(args[0])
    assert isdir(opts.index_root), (
        'indexpackages.abs_normpath failed to translate your, legitemate, '
        'index directory argument. It produced: "%s", you specified "%s"',
        opts.index_root, args[0]
        )
    args.pop(0)

    cwd = os.getcwd()
    os.chdir(opts.index_root)
    try:
        import_setuptools(opts.index_root)
        write_full_index(IndexWriter(opts), opts)
    finally:
        os.chdir(cwd)


if __name__=='__main__':
    run()


