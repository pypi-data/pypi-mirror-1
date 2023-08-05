'''\
``%prog [-TU] [OPTIONS] index/package/archive``

Build a python package index based on the egg files in the directory specified
by the ``index/package/archive argument``. This argument specifies the file
system root directory in which the distributions are stored and where the index
will be built.

Options-Summary::

    --projects-path --downloads-path --index-pagename --project-uri-remap
    --log-level --log-content --master-template --project-template
    --dry-run

'''

import os, sys, types, urlparse, textwrap
from itertools import chain
from os.path import *
from glob import glob
from socket import gethostname
from md5 import md5
import optparse, logging

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
<title>%(index_name)s: %(project_name)s %(latest_version)s</title>
</head>
<body>
<h1>%(project_name)s %(latest_version)s</h1>
%(DOWNLOAD_LINKS)s
</body>
</html>
'''


MASTER_IDX_HREF_fmt='''\
<a href="%(projects_path)s/%(project_name)s/%(version)s">\
%(project_name)s %(version)s</a>\
'''

DISTDOWNLOAD_HREF_fmt='''\
<a href="%(master_index_url)s%(downloads_path)s/%(distribution_basename)s\
#md5=%(md5_digest)s" rel="nofollow">%(distribution_basename)s</a>\
'''


def master_idx_href(dist, projects_path=''):
    return MASTER_IDX_HREF_fmt % dict(
            projects_path=projects_path,
            project_name=dist.project_name,
            version=dist.version
            )

def distdownload_href(master_index_url, distribution_basename, md5_digest,
        downloads_path=''):
    return DISTDOWNLOAD_HREF_fmt % locals()



def abs_normpath(path, *parts):
    if parts:
        return normpath(
                join(abspath(expanduser(path)), expanduser(join(parts)))
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
        pkg_resources = __import__('pkg_resources')
        log.info('Using indexed setuptools: %s' % setuptools_eggs[-1])



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



class MasterIndex(object):
    def __init__(self, opts):
        self.opts = opts
        self.MASTER_INDEX_NAME=getattr(opts, 'index_title',
                self.MASTER_INDEX_NAME)
        self.MASTER_INDEX_URL=getattr(opts, 'index_url',
                self.MASTER_INDEX_URL)
        self.PROJECTS_PATH=getattr(opts, 'projects_path',
                self.PROJECTS_PATH)
        self.DOWNLOADS_PATH=getattr(opts, 'downloads_path',
                self.DOWNLOADS_PATH)

    MASTER_INDEX_NAME='cheeseboard.localhost'
    MASTER_INDEX_URL='http://localhost'
    PROJECTS_PATH=''
    DOWNLOADS_PATH=''

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
        for k, v in dict(
                index_name=index_name,
                ).iteritems():
            variables.setdefault(k,v)

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
        # Allow the caller to force the latest version link on each page
        # For example, to make it the latest *stable* version.
        latest_version=variables.pop('latest_version',
                self.dists[0].version
                )
        for i in xrange(0, len(self.dists)):
            yield self.page_names[i], self.page_template % dict(
                    variables,
                    latest_version=latest_version,
                    project_name=self.dists[i].project_name,
                    DOWNLOAD_LINKS=DOWNLOAD_LINKS + '<br>\n'.join(
                        self.project_download_hrefs[i:]
                        )
                    )


def build_index(opts, distributions, project_distributions,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing):

    if not opts.index_url:
        opts.index_url = 'http://cheeseboard.%s' % gethostname()
    if not opts.index_title:
        opts.index_title = 'cheeseboard.' + gethostname()

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
    mi.master_idx_hrefs=[]
    mi.master_rewrites={}
    mi.projects=[]
    for k in sorted(project_distributions):
        mi.projects.append(ProjectListing(opts))
        pl = mi.projects[-1]
        pl.page_names = []
        pl.dists = []
        pl.basefilenames = []
        pl.versions = []
        pl.digests = []
        pl.project_download_hrefs = []
        for distinfo in sorted(project_distributions[k], reverse=True):
            pver, dist, basefn, digest = distinfo
            #print dist.project_name, dist.version, dist.egg_name(), digest
            pl.dists.append(dist)
            pl.basefilenames.append(basefn)
            pl.versions.append(dist.version)
            pl.digests.append(digest)

            pl.project_download_hrefs.append(distdownload_href(
                mi.MASTER_INDEX_URL, basefn, digest,
                downloads_path=mi.DOWNLOADS_PATH)
                )

            mi.master_idx_hrefs.append(
                    master_idx_href(dist, projects_path = mi.PROJECTS_PATH)
                    )

            pn = dist.project_name
            pn_safe = pkg_resources.safe_name(pn)
            pn_variants = unique_rewrites(pn)
            pv = dist.version.lower()
            pl.page_names.append(('%s-%s.html' % (pn_safe, pv)).lower())
            # re-direct unversioned requests to the most recent page
            if pn not in mi.rewrites:
                # we sort newest to oldest above so if its not in yet,
                # this page_name is the one we want.
                for k in pn_variants:
                    k = k + '/'
                    if k not in mi.rewrites:
                        mi.rewrites[k] = pl.page_names[-1]
                        mi.rewrites_order.append(k)
            for k in pn_variants:
                k = '%s/%s' % (k, pv)
                mi.rewrites[k] = pl.page_names[-1]
                mi.rewrites_order.append(k)

    return mi


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
        log.info('%s: %s', pl.dists[0].project_name, ', '.join(pl.versions))
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
        vhostfn = getattr(self.opts, 'apache_vhost_file',
                'apache-vhost.directives.conf'
                )
        dirdirectfn = getattr(self.opts, 'apache_dirdirect_file',
                'apache-dir.directives.conf')
        htaccessfn = getattr(self.opts, 'apache_htaccess_file',
                'apache.htaccess')


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
        to manage an index that is for personal use.

        Your package index was built under:
            "%s"

        The re-write map that deals with safe project naming and adhering to
        the PyPI requirements on the URI space is:
            "%s"

        If you set the RewriteLogLevel to 3 or more (default 0 means off) 
        mod_rewrite will put usefull information in this file:
           "%s"


        ''' % (document_root, project_index_filename, rewrite_log_filename)

        server_name = urlparse.urlparse(
                    mi.MASTER_INDEX_URL)[1].rsplit(':', 1)[0]
        server_name_comment = '''\
        The server name is taken from the master index url - (Note that
        the index-url is baked into all the download links).'''
        server_alias = '.'.join([sp for ip, sp in
                    zip(server_name.split('.'),
                        mi.MASTER_INDEX_NAME.split('.'))
                    if ip and ip == sp])
        if server_alias == server_name:
            server_alias = ''
        server_alias_comment = '''\
                If the dot seperated fields of the master index name form a non
                empty prefix of the ServerName then it is sugested as a
                ServerAlias. "-- no suitable default" means the index name is
                not related to the server name in a (trivialy) DNS compatible
                way OR that the FQDN of the server and it index name are
                the same.'''

        def format_directive(directive, comment='', comment_before=True,
                directive_indent=1, directive_indent_istab=True):
            if directive and not directive.split(None, 1)[1]:
                directive = (
                    '# ' + directive + ' # -- no appropriate default' + '\n'
                    )
            elif directive:
                ws = directive_indent_istab and '\t' or ' '
                directive = ws * directive_indent + directive + '\n'
            else:
                directive = '\n'
            if not comment:
                return directive
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
                return comment + (directive and '\n' + directive or '')
            return (directive and diretive + '\n' or '') + comment

        vhost_directives_order=(
            'ServerName ServerAlias DocumentRoot '
            'RewriteEngine RewriteLog RewriteMap'
            ).split()

        vhost_directives = dict(

            ServerName = format_directive(
                'ServerName ' + server_name,
                comment=server_name_comment
                ),

            ServerAlias = format_directive(
                server_alias and 'ServerAlias ' + server_alias,
                comment=server_alias_comment
                ),

            DocumentRoot = format_directive(
                'DocumentRoot ' + document_root,
                comment='''\
                The DocumentRoot path is the filesystem root in which the
                index was built.'''),
            RewriteEngine = format_directive(
                'RewriteEngine on', comment='''\
                It is necessary to enable the rewrite engine in both the
                host or server context AND in directory context of the
                index root (usualy the DocumentRoot) in order to enable
                htaccess support.'''),
            RewriteLogLevel = format_directive('RewriteLogLevel 0'),
            RewriteLog = format_directive(
                'RewriteLog ' + rewrite_log_filename),
            RewriteMap = format_directive(
                'RewriteMap ' + project_index + ' txt:' +
                project_index_filename, comment='''\
                Note that it is not possible to set the RewriteMap
                directive in a directory or a .htaccess context.''')
            )
        self.write_output_file(vhostfn,
                '\n'.join(chain(
                    [format_directive('', comment=vhost_comment)],
                    [vhost_directives[k] for k in vhost_directives_order]
                    )),
                log_level = log_level
                )
        htaccess_enable = getattr(self.opts, 'config_for_htaccess',
                True)


        dirdirect_order = (
            'AddType RewriteEngine Options AllowOverride '
            'Order allow RewriteCond RewriteRule').split()

        dirdirect = dict(

            AddType = format_directive(
                    (htaccess_enable and '#' or '') +
            'AddType application/zip .egg', comment='''\
            Arrange for .egg files to be served as the appropriate content
            type. If commented out then it is assumed to be configured via the
            .htaccess file in effect for this directory context.'''),

            RewriteEngine = vhost_directives['RewriteEngine'],

            Options = format_directive(
                    (not htaccess_enable and '#' or '') +
            'Options +FollowSymLinks', comment='''\
            FollowSymLinks MUST be enabled if you want to manage the
            index re-writes mostly in .htacess. The apache documentation (v
            2.0.xx) contains further information on this issue.'''),

            AllowOverride = format_directive(
                (not htaccess_enable and '#' or '') +
            'AllowOverride All', comment='''\
            Allow all directives to be overriden in .htaccess files in this
            directory context (Note: `FollowSymLinks` must also be enabled to
            get htaccess working with mod_rewrite).'''),

            Order = format_directive('Order allow,deny'),
            allow = format_directive('allow from all'),

            RewriteCond = format_directive(
                (htaccess_enable and '#' or '') + (
            'RewriteCond ${%s:$1|NOT_FOUND} !=NOT_FOUND'
                    ) % project_index,
            comment='''\
            Re-write anything explicitly listed in the index to the key target,
            which should be appropriate project page for the request (versioned
            or otherwise). This assumes that "%s" is the name of the package
            project mod_rewrite txt:map configured in the server/host context
            that owns this directory. The actual map file was writen to this
            file: "%s" Note that if this directive is commented out it
            indicates that the .htaccess means of configuring the index may
            have been enabled when the server config was generated, in which
            case, the RewriteCond & RewriteRule are assumed to be present in a
            .htaccess file living in the package index file system root.
            ''' % (project_index, project_index_filename)
            ),
            RewriteRule=format_directive((htaccess_enable and '#' or '') + (
            'RewriteRule ^(.*)$ ${%s:$1} [L]' % project_index
                ))
            )
        self.write_output_file(dirdirectfn,
                '\n'.join(chain(
                    ['<Directory %s>' % document_root],
                    [dirdirect[k] for k in dirdirect_order],
                    ['</Directory>']
                    )),
                log_level=log_level
                )

        htaccess_comment='''\
        This .htaccess file assumes the server (or vhost) config has:

         1. loaded the an appropriate mod_rewrite txt map and configured it
         with the name "%(project_index)s".

         2. Turned on the FollowSymlinks option for the directory context
         that owns the directory in which this .htaccess file lives.

         3. Set RewriteEngine on in *both* the server/host context AND
         the directory context in which this .htaccess file lives.

        When this  config was generated the re-write map named
        "%(project_index)s" was written to the file:
            "%(project_index_filename)s"
        ''' % dict(
                project_index=project_index,
                project_index_filename=project_index_filename
                )
        htaccess_order=(
            'AddType RewriteEngine RewriteCond RewriteRule'
            ).split()

        htaccess = dict(

            AddType = format_directive(
            'AddType application/zip .egg', comment='''\
            Arrange for .egg files to be served as the appropriate content
            type.'''),

            RewriteEngine = vhost_directives['RewriteEngine'],

            RewriteCond = format_directive(
            'RewriteCond ${%s:$1|NOT_FOUND} !=NOT_FOUND' % project_index,
            comment='''\
            Re-write anything explicitly listed in the index to the key target,
            which should be appropriate project page for the request (versioned
            or otherwise). This assumes that "%s" is the name of the package
            project mod_rewrite txt:map configured in the server/host context
            that owns this directory. The actual map file was writen to this
            file:
                "%s"
            ''' % (project_index, project_index_filename)),

            RewriteRule=format_directive(
            'RewriteRule ^(.*)$ ${%s:$1} [L]' % project_index)
        )

        self.write_output_file(htaccessfn,
                '\n'.join(chain(
                    [format_directive('', comment=htaccess_comment)],
                    [htaccess[k] for k in htaccess_order]
                    )),
                log_level = log_level
                )



def write_full_index(contentwriter, opts,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing):

    distributions=set([])
    project_distributions={}

    update_egg_distributions(opts.index_root,
            distributions, project_distributions)
    mi = build_index(opts, distributions, project_distributions,
        MasterIndex=MasterIndex,
        ProjectListing=ProjectListing
        )
    for pl in mi.projects:
        contentwriter.write_project_items(mi, pl)
    contentwriter.write_master_index(mi)
    contentwriter.write_apache_directives(mi)




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
            [default:%default] Sets the logging level for messages issued by
            this package. It can be a number, or any one of the standard
            logging level strings "CRITICAL ERROR WARNING INFO DEBUG NOTSET".
            The level strings correspond, respectively, to the numbers [50, 40,
            30, 20, 10, 0].  NOTE: Set this options to 50 for *most quiet* or
            10 for *most verbose*.  Note that NOTSET will cause the logging
            level to be taken from the first parent handler that *does* set a
            level - usualy this will be the root logger '''))),
    ('--log-content', dict(default='DEBUG', help=fmthelp('''\
            [default:%default] Sets the logging level at which the content of
            generated pages and files will be logged. Valid values are exactly
            as per the --log-level option, except that value of NOTSET or 0 
            will have no effect'''))),
    ('--log-config', dict(default='DEBUG', help=fmthelp('''\
            [default:%default] Exactly as per --log-content. But applies,
            exclusively, to content that represents site/host configuration
            necessary for the full functionality of the index.
            (apache, etc)'''))),
    ('--print-log-conf', dict(default=False, action='store_true',
        help=fmthelp('''\
            [default:%default] Set this flag to print out information
            reflecting the application of the --log options. Use if you are
            not seeing the messages you expect.'''))),

    ('-T', '--index-title', dict(default='',
        help=fmthelp('''\
        [default:generated via gethostname] The title of the package index.
        This will be used as the <title>CONTENT</title> for the master index
        page.  By default this option value is generated using ``gethostname``
        like this ``'cheeseboard.%s' % gethostname()``
        '''))),
    ('-U', '--index-url', dict(
         default='',
         help=fmthelp('''\
        [default:generated via gethostname] The public url of the package index
        main page. The download url hrefs will all explicitly include this url
        (because easy_install requires it to be so). By default this option
        value is generated using ``gethostname`` like this
        ``'http://cheeseboard.%s' % gethostname()``.'''))),
    ('--projects-path', dict(default='', help=fmthelp('''\
            [default:%default] Every project link on the master index page will
            be prefixed with this path.'''))),
    ('--downloads-path', dict(default='', help=fmthelp('''\
        [default:%default] Every download href - on every project page - will
        be prefixed with this path.'''))),
    ('--index-pagename', dict(default='index.html', help=fmthelp('''\
        [default:%default] Sets the name of the master index page.'''))),
    ('--project-uri-remap', dict(default='project-index.txt', 
        help=fmthelp('''\
        [default:%default] Sets the name of the mod_rewrite RewriteMap
        compatible text file that will contain the necessary *safe_name*
        remapings from project uris to the appropriate project page for the
        version implied in the uri. If there is no version information in
        the uri then the remap directs to the BEST VERSION as defined by
        setuptools semantics for version string interpretation.'''))),
    ('--master-template', dict(default='', help=fmthelp('''\
        [default:%%default] Use this option to set the file from which the
        master index page template will be read. If a relative path is provided
        it must be relative to --index-root. The file should be a plain text
        file providing standard %%(key)s substitutions for the following
        keys: %s. Note that the keys indicated in this help text may be
        incorrect if you are running a version of this program that customise
        the replacement keys. The template file is checked for the presence of
        the actual keys needed at runtime by the class that generates the
        page.''' % ', '.join( MasterIndex.page_template_required_keys)
        ))),
    ('--project-template', dict(default='', help=fmthelp('''\
        [default:%%default] Use this option to set the file from which the
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
        [default:%default] Set this option to prevent this program from
        writing anything to disc. This option can be combined with
        logging options to re-direct most content production
        to standard out.''')))
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


