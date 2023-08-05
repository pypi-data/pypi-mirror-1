#!/usr/bin/env python
import sys, os
from os.path import join, dirname, abspath
from glob import glob
try:
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools = False
try:
    from distinfo import get_info, get_requires
except ImportError:
    RE_HEADER_KEY=(
        r'(?ims)^:?(?P<key>[a-z][\w\-_ ]*):\s*'
             '(?P<value>.*?'
             '(?=(\Z|\n^:?[a-z][\w\-_ ]*:)))'
             )
    def get_info(data):
        import re
        info={}
        for k,v,_ in re.findall(RE_HEADER_KEY, data):
            info.setdefault(k,[]).append(v.strip())
        return info 

def abs_setupfile(*rname):
    return join(dirname(abspath(__file__)), *rname)

def read(*rnames):
    return open(abs_setupfile(*rnames)).read()


def update_docs(glob_pattern, ignore=None, docutils_conf=None):
    ignore = ignore or {}
    try:
        from docutils.core import publish_cmdline
    except ImportError:
        print ('Documentation not re-built. Ignore this message if you '
                'are installing this package')
        return
    from glob import glob
    if docutils_conf:
        base_argv = ['--config=%s' % docutils_conf]
    else:
        base_argv = []
    for source in glob(glob_pattern):
        if source in ignore:
            continue
        dest = os.path.splitext(source)[0] + '.html'
        if not os.path.exists(dest) or \
               os.path.getmtime(dest) < os.path.getmtime(source):
            print 'building documentation file %s' % dest
            publish_cmdline(writer_name='html',
                            argv=base_argv + [source, dest])



def generate_mantxt(pyfile):
    try:
        from subprocess import Popen, PIPE
    except ImportError:
        return
    sys.stdout.flush() # We want any pending output first
    p = Popen([sys.executable, pyfile, '--help'],
            stdout=PIPE, stderr=PIPE, env=dict(
                PYTHONPATH=os.pathsep.join(sys.path)
                )
            )
    txt = p.communicate()[0]
    usage, content = [], txt.split('\n')
    usage.append(content.pop(0))
    usage.append('~' * len(usage[0]))
    content[0:0]=usage
    txt='\n'.join(content)

    if not p.returncode:
        name, ext = os.path.splitext(pyfile)
        assert name
        manfile = name + '-man.txt'
        file(manfile, 'w').write(txt)
        return manfile


def get_long_description():
    long_description = (
        '.. contents::' + '\n' +
        read('README.txt') + '\n' +
        '.. _indexpackages-man:' + '\n' +
        read('indexpackages-man.txt') + '\n' +
        'Changes:' + '\n' +
        '~~~~~~~~' + '\n' +
        read('ChangeLog') + '\n' +
        '-----' * 7
        )
    print long_description

if None is not generate_mantxt(abs_setupfile('indexpackages.py')):
    update_docs(abs_setupfile('*.txt'), [abs_setupfile('pkg-info.txt')])

PKG_INFO=get_info(read('pkg-info.txt'))

name=PKG_INFO['Name'][0]
version=PKG_INFO['Version'][0]


#provides=name+'-'+version
provides=name
setupkw=dict(
    name=PKG_INFO['Name'][0],
    version=PKG_INFO['Version'][0],
    description = PKG_INFO['Abstract'][0],
    long_description = get_long_description(),
    author = PKG_INFO['Author'][0],
    license = PKG_INFO['License'][0],
    author_email = PKG_INFO['Author-email'],
    url = "http://trac.wiretooth.com/public/wiki/pypicache",
    download_url = "http://svn.wiretooth.com/pypi/pypicache/"+version,
    py_modules=['indexpackages'],
    package_dir = {'':'.'},
    classifiers = PKG_INFO['Classifiers'],
)
if using_setuptools:
    # You do not have to have setuptools installed in order to run module
    # code that is installed in a ziped egg, try this (substiting
    # appropriate values for VER & PYER):
    # PYTHONPATH=pypicache-VER-$PYVER.egg python-$PYVER -m indexpackages --help
    setupkw['provides'] = provides
    setupkw['zip_safe'] =True
    setupkw['entry_points'] = """\
[console_scripts]
pypicache-index = indexpackages:run
"""

setup(**setupkw)

