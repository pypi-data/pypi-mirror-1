
"""

pypi.py
=======

Desc: Library for getting information about Python packages by querying
      The CheeseShop (PYPI a.k.a. Python Package Index).


Author: Rob Cakebread <gentoodev@gmail.com>

License  : GNU General Public License Version 2

"""

__docformat__ = 'restructuredtext'

import xmlrpclib
import cPickle
import os
import time
import logging

from yolk.utils import get_yolk_dir


XML_RPC_SERVER = 'http://cheeseshop.python.org/pypi'


class CheeseShop:

    """Interface to Python Package Index"""

    def __init__(self, debug=False, no_cache=False):
        """init"""
        self.no_cache = no_cache
        self.debug = debug
        self.yolk_dir = get_yolk_dir()
        self.xmlrpc = self.get_xmlrpc_server()
        self.pkg_cache_file = self.get_pkg_cache_file()
        self.last_sync_file = self.get_last_sync_file()
        self.pkg_list = None
        self.logger = logging.getLogger("yolk")
        self.get_cache()

    def get_cache(self): 
        """
        Get a package name list from disk cache or PyPI
        """
        #This is used by external programs that import `CheeseShop` and don't
        #want a cache file written to ~/.pypi and query PyPI every time.
        if self.no_cache:
            self.pkg_list = self.list_packages()
            return

        if not os.path.exists(self.yolk_dir):
            os.mkdir(self.yolk_dir)
        if os.path.exists(self.pkg_cache_file):
            self.pkg_list = self.query_cached_package_list()
        else:
            self.logger.debug("DEBUG: Fetching package list cache from PyPi...")
            self.fetch_pkg_list()

    def get_last_sync_file(self):
        """
        Get the last time in seconds since The Epoc snce the last pkg list sync
        """
        return os.path.abspath(self.yolk_dir + "/last_sync")

    def get_xmlrpc_server(self):
        """
        Returns PyPI's XML-RPC server instance
        """
        try:
            return xmlrpclib.Server(XML_RPC_SERVER)
        except IOError:
            self.logger("ERROR: Can't connect to XML-RPC server: %s" \
                    % XML_RPC_SERVER)

    def get_pkg_cache_file(self):
        """
        Returns filename of pkg cache
        """
        return os.path.abspath('%s/pkg_list.pkl' % self.yolk_dir)

    def query_versions_pypi(self, package_name):
        """Fetch list of available versions for a package from The CheeseShop"""
        if not package_name in self.pkg_list:
            self.logger.debug("DEBUG: package %s not in cache, querying PyPI..." \
                    % package_name)
            self.fetch_pkg_list()
        #I have to set version=[] for edge cases like "Magic file extensions" 
        #but I'm not sure why this happens. It's included with Python or
        #because it has a space in it's name?
        versions = []
        for pypi_pkg in self.pkg_list:
            if pypi_pkg.lower() == package_name.lower():
                if self.debug:
                    self.logger.debug("DEBUG: %s" % package_name)
                versions = self.package_releases(pypi_pkg)
                package_name = pypi_pkg
                break
        return (package_name, versions)

    def query_cached_package_list(self):
        """Return list of pickled package names from PYPI"""
        if self.debug:
            self.logger.debug("DEBUG: reading pickled cache file")
        return cPickle.load(open(self.pkg_cache_file, "r"))

    def fetch_pkg_list(self):
        """Fetch and cache master list of package names from PYPI"""
        self.logger.debug("DEBUG: Fetching package name list from PyPI")
        package_list = self.list_packages()
        cPickle.dump(package_list, open(self.pkg_cache_file, "w"))
        self.pkg_list = package_list

    def search(self, spec, operator):
        '''Query PYPI via XMLRPC interface using search spec'''
        return self.xmlrpc.search(spec, operator.lower())
    
    def changelog(self, hours):
        '''Query PYPI via XMLRPC interface using search spec'''
        return self.xmlrpc.changelog(get_seconds(hours))

    def updated_releases(self, hours):
        '''Query PYPI via XMLRPC interface using search spec'''
        return self.xmlrpc.updated_releases(get_seconds(hours))

    def list_packages(self):
        """Query PYPI via XMLRPC interface for a a list of all package names"""
        return self.xmlrpc.list_packages()

    def release_urls(self, package_name, version):
        """Query PYPI via XMLRPC interface for a pkg's available versions"""

        return self.xmlrpc.release_urls(package_name, version)

    def release_data(self, package_name, version):
        """Query PYPI via XMLRPC interface for a pkg's metadata"""
        try:
            return self.xmlrpc.release_data(package_name, version)
        except xmlrpclib.Fault:
            #XXX Raises xmlrpclib.Fault if you give non-existant version
            #Could this be server bug?
            return

    def package_releases(self, package_name):
        """Query PYPI via XMLRPC interface for a pkg's available versions"""
        if self.debug:
            self.logger.debug("DEBUG: querying PyPI for versions of " \
                    + package_name)
        return self.xmlrpc.package_releases(package_name)

    def get_download_urls(self, package_name, version="", pkg_type="all"):
        """Query PyPI for pkg download URI for a packge"""

        if version:
            versions = [version]
        else:

            #If they don't specify version, show em all.

            (package_name, versions) = self.query_versions_pypi(package_name)

        all_urls = []
        for ver in versions:
            metadata = self.release_data(package_name, ver)
            for urls in self.release_urls(package_name, ver):
                if pkg_type == "source" and urls['packagetype'] == "sdist":
                    all_urls.append(urls['url'])
                elif pkg_type == "egg" and \
                        urls['packagetype'].startswith("bdist"):
                    all_urls.append(urls['url'])
                elif pkg_type == "all":
                    #All
                    all_urls.append(urls['url'])

            #Try the package's metadata directly in case there's nothing
            #returned by XML-RPC's release_urls()
            if metadata and metadata.has_key('download_url') and \
                        metadata['download_url'] != "UNKNOWN" and \
                        metadata['download_url'] != None:
                if metadata['download_url'] not in all_urls:
                    if pkg_type != "all":
                        url = filter_url(pkg_type, metadata['download_url'])
                        if url:
                            all_urls.append(url)
        return all_urls
        
def filter_url(pkg_type, url):
    """
    Returns URL of specified file type
    'source', 'egg', or 'all'
    """
    bad_stuff = ["?modtime", "#md5="]
    for junk in bad_stuff:
        if junk in url:
            url = url.split(junk)[0]
            break

    #pkg_spec==dev (svn)
    if url.endswith("-dev"):
        url = url.split("#egg=")[0]

    if pkg_type == "all":
        return url

    elif pkg_type == "source":
        valid_source_types = [".tgz", ".tar.gz", ".zip", ".tbz2", ".tar.bz2"]
        for extension in valid_source_types:
            if url.lower().endswith(extension):
                return url

    elif pkg_type == "egg":
        if url.lower().endswith(".egg"):
            return url

def get_seconds(hours):
    """
    Get number of seconds since epoch from now minus `hours`

    @param hours: Number of `hours` back in time we are checking
    @type hours: int

    Return integer for number of seconds for now minus hours

    """
    return int(time.time() - (60 * 60) * hours)

