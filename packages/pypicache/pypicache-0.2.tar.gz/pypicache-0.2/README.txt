pypicache: roll your own python package index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main script provides a relatively painless way to convert a single
directory of python packages into an easy_install compatible package archive.
A typical use would be to expose the contents of your PYTHON_EGG_CACHE
directory, or your zc.buildout download_cache, to other people or computers
on your local area network.

The tool does the following:

* Generates a minimal html page for each (normative) project/version
  combination.
* Generates a minimal master index page.
* Generates a mod_rewrite compatible txt: map file which maps project URIs
  to the appropriate page. The map contains as many variants as it needs,
  in order to deal with case sensitivity, safe_name() or published name.
  The version is forced to lower case when the project pages (above) are
  generated. For references that don't include a version path, the map
  refers to the most recent distribution that is available in the archive
  directory.
* Generates a fully functional set of apache configuration files that can
  be directly included into the server configuration (server/vhost,
  per-directory) and a .htaccess file that repeats the per-directory
  config. Depending on whether or not htaccess support is enabled at the
  time the index is built the necessary directives *in ALL* configuration
  contexts are either enabled or present but commented out.

There is limited - simple %()s - string template support for the index and
project page generation.

See `indexpackages-man`_

NOTICE:

* The indexpackages.py python module can be run independently, without
  being *installed* and without setuptools installed. When the module is
  run directly, eg as ``python indexpackages.py``, if it cant import
  setuptools in the normal manner it will look for a setuptools egg in the
  archive root directory. If multiple setuptools eggs are present it sorts
  the filenames lexicaly and chooses the highest. If you need to pin the
  setuptools version place a setuptools.pth file in the archive root.

  If there is a setuptools.pth in the index root then *all* directories
  listed in that file are added to the path, via ``site.addsitedir``,
  before attempting to import setuptools.


* In order to make index generation quick, the long_description meta
  information in packages is NOT consulted or included in the generated
  project pages. This means any author provided links get missed. A feature
  to allow deeper package introspection will follow shortly. However, the
  *primary* use case this tool is written for is:

    I want to maintain a local python package archive - for when other
    sources are either unavailable or in-appropriate - and I want that
    archive to be a valid easy_install package index.
