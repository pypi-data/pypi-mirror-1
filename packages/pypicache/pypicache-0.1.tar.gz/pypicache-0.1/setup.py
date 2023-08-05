#!/usr/bin/env python
"""setuptools setup file"""
import sys, os
from setuptools import setup
from glob import glob


def generate_mantxt(pyfile):
    sys.stdout.flush() # We want any pending output first
    from subprocess import Popen, PIPE
    txt = Popen([sys.executable, pyfile, '--help'],
            stdout=PIPE, stderr=PIPE, env=dict(
                PYTHONPATH=os.pathsep.join(sys.path)
                )
            ).communicate()[0]
    name, ext = os.path.splitext(pyfile)
    assert name
    manfile = name + '-man.txt'
    file(manfile, 'w').write(txt)
    return manfile


def update_docs(glob_pattern, ignore=None, docutils_conf=None):
    ignore = set(ignore or [])
    try:
        from docutils.core import publish_cmdline
    except ImportError:
        print 'failed to update docs, docutils not installed'
        return
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

def get_info(data, fileobj=None):
    import re
    info={}
    for k,v,_ in re.findall(
        r'(?ims)^:?(?P<key>[a-z][\w\-_ ]*):\s*'
         '(?P<value>.*?'
         '(?=(\Z|\n^:?[a-z][\w\-_ ]*:)))',
         fileobj and fileobj.read() or data):
        info.setdefault(k,[]).append(v.strip())
    return info

def get_requires(info, printspecials=True):
    specialdists=[]
    distinfo=[]
    requires = info.get('Requires', [])
    for s in info.get('Special', []):
        s = s.split(':',1)
        if s[0].strip() == 'Distribution':
            di = s[1].split(':',1)
            d, i = len(di) and di or [di, '']
            d = d.strip()
            requires[:] = [r for r in requires if d not in r]
            specialdists.append(d)
            distinfo.append(di)
    if not printspecials:
        return requires
    if specialdists:
        print (
            'Requirements %s not compatible with setuptools, you will '
            'need to install them by hand before using this package.'
            ) % ', '.join(specialdists)
    for d,i in zip(specialdists, distinfo):
        if i:
            print '%s distribution hint: %s' % (d, i)
    return requires

PKG_INFO=get_info(file('pkg-info.txt').read())

generate_mantxt('indexpackages.py')
update_docs('*.txt', ['pkg-info.txt'])


setup(
    name=PKG_INFO['Name'][0],
    version=PKG_INFO['Version'][0],
    install_requires=get_requires(PKG_INFO),
    long_description=PKG_INFO['Abstract'][0],
    author=PKG_INFO['Author'][0],
    license = PKG_INFO['License'][0],
    author_email = PKG_INFO['Author-email'],
    url = "http://svn.wiretooth.com/svn/open/pypicache/trunk/pypicache.html",
    download_url = "http://svn.wiretooth.com/svn/open/pypicache/trunk",
    entry_points = {
        'console_scripts': [
        'pypicache-index = indexpackages:run'
        ]},
    py_modules=['indexpackages'],
    package_dir = {'':'.'},
    classifiers=PKG_INFO['Classifiers'],
    zip_safe=False,
)

