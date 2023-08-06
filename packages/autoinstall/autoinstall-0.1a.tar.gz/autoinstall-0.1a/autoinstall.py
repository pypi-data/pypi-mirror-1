"""\
package loader for auto installing Python packages.

A package loader in the spirit of Zero Install that can be used to
inject dependencies into the import process. Autoinstall can be
bootstraped with the nascent package loader bootstrap module. For
example::

    try:
        _version = "0.1a"
        import autoinstall
        if autoinstall.__version__ != _version:
            raise ImportError("A different version than exprected found.")
    except ImportError, e:
        # http://svn.python.org/projects/sandbox/trunk/bootstrap/bootstrap.py
        import bootstrap 
        pypi = "http://pypi.python.org"
        dir = "packages/source/a/autoinstall"
        url = "%s/%s/autoinstall-%s.tar.gz" % (pypi, dir, _version)
        bootstrap.main((url,))
        import autoinstall

    # once imported you can bind any top level package name to a URL
    # pointing to something that can be imported using the zipimporter

    autoinstall.bind("pymarc", "http://pypi.python.org/packages/2.5/p/pymarc/pymarc-2.1-py2.5.egg")

    import pymarc

    print pymarc.__version__, pymarc.__file__

    
References::

  http://0install.net/
  http://www.python.org/dev/peps/pep-0302/
  http://svn.python.org/projects/sandbox/trunk/import_in_py
  http://0install.net/injector-find.html
  http://roscidus.com/desktop/node/903

TODO::

optional interfaces...

    def get_data(pathname) -> string with file data.

    Return the data associated with 'pathname'. Raise IOError if
    the file wasn't found.");

    def is_package,
    "is_package(fullname) -> bool.

    Return True if the module specified by fullname is a package.
    Raise ZipImportError is the module couldn't be found.");

    def get_code,
    "get_code(fullname) -> code object.

    Return the code object for the specified module. Raise ZipImportError
    is the module couldn't be found.");

    def get_source,
    "get_source(fullname) -> source string.

    Return the source code for the specified module. Raise ZipImportError
    is the module couldn't be found, return None if the archive does
    contain the module, but has no source for it.");

"""

__version__ = "0.1a"
__docformat__ = "restructuredtext en"

import os
import new
import sys
import urllib
import logging
import tempfile
import zipimport

_logger = logging.getLogger(__name__)

_importer = None

def _getImporter():
    global _importer
    if _importer is None:
        _importer = Importer()
        sys.meta_path.append(_importer)
    return _importer

def bind(package_name, url):
    """bind a top level package name to a URL.

    The package name should be a package name and the url should be a
    url to something that can be imported using the zipimporter. 
    """
    _getImporter().bind(package_name, url)


class Cache(object):

    def __init__(self, directory=None):
        self.directory = directory or "./autoinstall.cache.d/"
        try:
            if not os.path.exists(self.directory):
                _logger.debug("Creating cache directory '%s'." % self.directory)
                os.mkdir(self.directory)
        except Exception, err:
            _logger.exception(err)
            self.cache_directry = tempfile.mkdtemp()
        _logger.info("Using cache directory '%s'." % self.directory)
    
    def get(self, url):
        _logger.info("Getting '%s' from cache." % url)
        filename = os.path.join(self.directory, "%s" % hash(url))
        if os.path.exists(filename):
            _logger.debug("... already cached in file '%s'." % filename)
        else:
            _logger.debug("... not in cache. Caching in '%s'." % filename)
            stream = file(filename, "wb")
            self.download(url, stream)
            stream.close()
        return filename

    def download(self, url, stream):
        _logger.info("Downloading: %s" % url)
        try:
            netstream = urllib.urlopen(url)
            code = 200
            if hasattr(netstream, "getcode"):
                code = netstream.getcode()
            if not 200 <= code < 300:
                raise ValueError("HTTP Error code %s" % code)
        except Exception, err:
            _logger.exception(err)

        BUFSIZE = 2**13  # 8KB
        size = 0
        while True:
            data = netstream.read(BUFSIZE)
            if not data:
                break
            stream.write(data)
            size += len(data)
        netstream.close()
        _logger.info("Downloaded %d bytes." % size)


class Importer(object):

    def __init__(self):
        self.packages = {}
        self.__cache = None

    def __get_store(self):
        return self.__store
    store = property(__get_store)

    def _get_cache(self):
        if self.__cache is None:
            self.__cache = Cache()
        return self.__cache
    def _set_cache(self, cache):
        self.__cache = cache
    cache = property(_get_cache, _set_cache)

    def find_module(self, fullname, path=None):
        """-> self or None.

        Search for a module specified by 'fullname'. 'fullname' must be
        the fully qualified (dotted) module name. It returns the
        zipimporter instance itself if the module was found, or None if
        it wasn't. The optional 'path' argument is ignored -- it's
        there for compatibility with the importer protocol.");
        """
        _logger.debug("find_module(%s, path=%s)" % (fullname, path))
        if path is None:
            top = fullname.split(".")[0]
            _logger.debug("%s, %s" % (top, top in self.packages))
            if top in self.packages:
                url = self.packages[top]
                filename = self.cache.get(url)
                _logger.debug("fullname: %s url: %s filename: %s", (fullname, url, path))
                try:
                    loader = zipimport.zipimporter(filename)
                    _logger.debug("returning: ", loader)
                except Exception, e:
                    _logger.exception(e)
                    return None
                return loader
        return None

    def bind(self, package_name, url):
        _logger.info("binding: %s -> %s" % (package_name, url))
        self.packages[package_name] = url
        

# class Loader(object):

#     def load_module(self, fullname):
#         """-> module.

#         Load the module specified by 'fullname'. 'fullname' must be
#         the fully qualified (dotted) module name. It returns the
#         imported module, or raises ZipImportError if it wasn't
#         found.");
#         """
#         _logger.debug("load_module(%s)" % fullname)
#         m = new.module(fullname)
#         m.__path__ = []
#         return m




if __name__=="__main__":
    import logging
    logging.basicConfig()

    bind("pymarc", "http://pypi.python.org/packages/2.5/p/pymarc/pymarc-2.1-py2.5.egg")

    import pymarc

    print pymarc.__version__, pymarc.__file__

    assert pymarc.__version__=="2.1"

    d = _getImporter().cache.directory
    assert d in pymarc.__file__, "'%s' not found in pymarc.__file__ (%s)" % (d, pymarc.__file__)
