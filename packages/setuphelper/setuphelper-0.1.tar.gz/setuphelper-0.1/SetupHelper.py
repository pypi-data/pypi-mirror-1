#!/usr/bin/python
"""
SetupHelper -- helper module to automate setup boilerplate
Copyright (C) 2008 by Peter A. Donis

Released under the Python Software Foundation License.

This setup helper module automates much of the boilerplate.
The entry point is the setup_main function, which expects to be
called with a dictionary mapping variable names to values; the
variable names supported are as follows (most of them map in
the obvious way to setup keyword arguments):

__progname__           -- name of the program
__version__            -- program version
__description__        -- one-line description

__long_description__   -- triple-quoted string containing long
                          description (may be read from README
                          instead, if so use next two variables
                          and omit this one)
__start_line__         -- contents of the line in README where the
                          long description should start (i.e.,
                          this line and all after it until the
                          end line will be included)
__end_line__           -- contents of the line in README where the
                          long description should end (i.e., this
                          line and all after it will *not* be
                          included)

__download_url__       -- URL for downloading the program; should
                          not be needed, use __url_base__ and
                          __url_type__ or __url_ext__ instead
__url_base__           -- base URL for download; assumes that the
                          full download URL is of the form
                          <base>/<progname>-<version>.<ext>
__url_ext__            -- extension for the download file; can be
                          ('tar.gz', 'zip', 'exe', 'dmg'); defaults
                          to 'tar.gz'
__url_type__           -- type of file being downloaded; can be
                          a valid __url_ext__ value or a valid
                          value for os.name ('posix', 'nt', and
                          'mac' are currently supported); if omitted,
                          __url_ext__ (or its default) is used

__author__             -- author name
__author_email__       -- author e-mail address
__url__                -- home URL for the author or progra

__license__            -- the name of the distribution license (valid
                          values are listed in PEP 241)
__classifiers__        -- triple-quoted string containing Trove
                          classifiers, one per line (blank lines
                          at the start and end are ignored)

__requires__           -- list of names of packages that this one
                          depends on; SetupHelper will attempt to
                          download each one from PyPI and install it
                          (note that the support for this if setuptools
                          is not used is *very* basic)
__provides__           -- list of package names that this one provides
                          (if omitted, defaults to __progname__); this
                          variable doesn't actually do anything unless
                          setuptools is being used
__obsoletes__          -- list of package names that should be removed
                          when this one is installed; again, this
                          doesn't do anything unless setuptools is used

__rootfiles__          -- list of files from the project root (the
                          setup.py directory) that should be included
                          in MANIFEST.in (optional; if not included
                          no files from the project root other than
                          the standard ones, setup.py and README,
                          and this module, SetupHelper.py, if present,
                          will be included in distributions); note that
                          this and the next variable are for files that
                          should *not* be installed but need to be in
                          the source distribution--this means that these
                          files will *not* be included in the list of
                          automatically detected Python modules (see
                          below), even if they are .py files
__rootdirs__           -- list of subdirectories of the project root
                          that should be included in MANIFEST.in; if
                          not included, only the SetupHelper directory,
                          if present, will be included (this is for
                          projects that are using the svn:externals
                          version of this helper module); note
                          that these subdirectories will *not* be
                          included in the list of automatically
                          detected packages (see below), even if they
                          include __init__.py files

__py_modules__         -- list of pure Python modules not contained
                          in packages; if omitted, it is assumed that
                          any .py files in the setup directory other
                          than those listed in __non_modules__ are
                          pure Python modules to be installed (except
                          setup.py, which is never installed)
__non_modules__        -- list of .py files in setup directory that
                          should not be treated as modules if modules
                          are automatically detected; note that these
                          will *not* be included in source distributions
                          either (to do that, list them in __rootfiles__)

__packages__           -- list of package names to be included; this
                          should generally not be used, using the
                          __package_root__ variable is preferred (or
                          just letting the default package finding
                          algorithm work)
__package_dirs__       -- list of subdirectories of the setup.py
                          directory that contain packages; if this is
                          omitted __package_root__ will be used (or
                          the default if it is not defined)
__package_root__       -- subdir of the setup.py directory which is
                          the single 'root' for all packages; if
                          this is omitted any subdir which contains
                          an __init__.py file is treated as a package;
                          for most distributions this default should
                          be sufficient
__package_data__       -- mapping of package names to lists of data
                          files; this should generally not be needed
                          as the default package finding algorithm
                          treats any sub-directory of a package that
                          is not itself a package (i.e., doesn't have
                          an __init__.py) as being a data directory
                          (unless it's an extension module source
                          directory, see below)
__non_packages__       -- list of subdirectories of the setup directory
                          that should not be treated as packages if
                          packages are auto-detected; note that these
                          will *not* be included in source distributions
                          either (to do that, list them in __rootdirs__)

__ext_modules__        -- list of extension module objects; this should
                          not be needed, use __ext_names__
__ext_names__          -- list of path names to extension modules
                          (starting from the setup.py directory); the
                          source code for each module is found by using
                          the __ext_src__ variable
__ext_src__            -- pathname to extension source files, usually
                          relative (meaning relative to the extension
                          directory); defaults to 'src', meaning the
                          'src' subdirectory of the extension directory

__scripts__            -- list of scripts to be included; this should
                          generally not be used, use __script_root__
                          (or the default 'scripts' directory) instead
__script_root__        -- subdir of the setup.py directory which is
                          the 'root' containing all scripts; if this
                          is omitted it will be assumed to be 'scripts'

__data_files__         -- list of data files to be included; this should
                          generally not be used, use __data_dirs__
                          instead (or the defaults)
__data_dirs__          -- list of subdirs of the setup.py directory
                          which contain data files (other than package
                          data files); if this is omitted these
                          subdirs will be checked: <progname> (if
                          it's not a package), 'examples'; data dirs
                          are installed to 'share/<progname>/<datadir>'
                          except for <progname> if it's a data dir,
                          it goes to 'lib/<progname>'.

Note that this list of variables is for metadata version 1.0 (PEP 241);
this module does not (yet) support the additional metadata defined in
version 1.1 (PEP 314).

The recommended way to call setup_main is to first define all the
necessary variables as module globals in your setup.py file, and
then simply do:

from SetupHelper import setup_main
setup_main(globals())

This will pass your module globals to SetupHelper, which will then
do all the grunt work!

The setup_main function also allows you to override several of the
defaults for the SetupHelper class; the currently accepted overrides
(as keyword arguments) are:

distutils_pkg   -- package to be used in place of distutils (if omitted
                   or None, use the standard distutils; currently the
                   only other supported value is 'setuptools'); note
                   that the distutils package automatically defines
                   ext_class, requires_class, and setup_func, so these
                   are rarely needed
ext_class       -- the class to be used for extension module definitions
                   (defaults to distutils.core.Extension if using standard
                   distutils, or setuptools.extension.Extension if using
                   setuptools)
url_types       -- mapping of os.name values to download URL extensions
requires_class  -- class to be used to handle the requires keyword; defaults
                   to None if using setuptools (since setuptools.setup
                   already handles requires), or the custom RequiresHelper
                   class defined in this module for standard distutils
setup_func      -- the actual setup function to be called (defaults to
                   distutils.core.setup or setuptools.setup)

Note that each of these variables can also be defined (with two leading
and two trailing underscores) in your setup.py script; they are listed
here only because they are used internally by SetupHelper rather than to
determine the arguments passed to the actual setup function.

Any keyword arguments to setup_main besides the ones above will be treated
as keyword arguments to the actual setup function that does the work;
keyword arguments passed this way override variables set in your setup
script's globals as described above.
"""

import sys
import os

SETUPHELPER_VERSION = "0.1"

def pypi_base_url(progname):
    """ Return the 'standard' PyPI base URL for progname. """
    return "http://pypi.python.org/packages/source/%s/%s" % (progname[0], progname)

def distutils_default():
    """ Support function for Python-provided distutils. """
    
    from distutils.core import setup, Extension
    import urllib2
    import re
    
    # patch distutils keywords if Python version too old
    if sys.version < '2.2.3':
        from distutils.dist import DistributionMetadata
        DistributionMetadata.classifiers = None
        DistributionMetadata.download_url = None
    
    class RequiresHelper(object):
        """
        Helper class to handle requires keyword. Should be
        instantiated with a list of strings suitable for the
        # requires variable/keyword.
        """
        
        pypi_url = "http://pypi.python.org/simple/"
        user_agent = "Python-urllib/%s SetupHelper/%s" % (
            urllib2.__version__, SETUPHELPER_VERSION)
        
        def __init__(self, requires, debug=False):
            self._requires = requires
            self._debug = debug
            
            # Grab setup options from our sys.argv so we can use the same
            # ones when installing requirements
            self.setup_opts = " ".join([opt for opt in sys.argv
                if opt.startswith('--')])
            if self.setup_opts:
                self.setup_opts = " %s" % self.setup_opts
        
        # NOTE: this is *not* fully general URL detection and parsing; it only
        # does the minimum necessary to work with HTML pages like those on PyPI
        # that contain properly formatted URLs within relatively "clean" content
        
        p_scheme = r"(https?|ftp):\/\/"
        p_hostname = r"([a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*)"
        p_portspec = r"(:[0-9]+)?"
        p_pathname = r"(\/[a-zA-Z0-9._%/\-]*)?"
        p_params = r"(;[a-zA-Z0-9._%/=\-]*)?"
        p_query = r"(\?[a-zA-Z0-9._%/=\-]*)?"
        p_fragment = r"(#[a-zA-Z0-9._%/=\-]*)?"
        
        url_pattern = p_scheme + p_hostname + p_portspec + p_pathname \
            + p_params + p_query + p_fragment
        href_pattern = r"\<a href\=\'" + url_pattern + r"\'\>"
        
        class URLMatchObject(object):
            """ Wrapper object for convenience in handling URL matches. """
            
            def __init__(self, m):
                self.__m = m
                self.url = m.group()
                self.scheme, self.hostname, self.domain, self.portspec, self.pathname, \
                    self.params, self.query, self.fragment = m.groups()        
        
        try:
            allowed_extensions = {
                'darwin': [".dmg", ".tar.gz", ".tar"],
                'linux2': [".tar.gz", ".tar.bz2", ".zip", ".tar"],
                'win32': [".exe", ".zip", ".tar.gz", ".tar"] }[sys.platform]
        except KeyError:
            allowed_extensions = ["tar.gz", ".tar"] # reasonably safe choice
        
        def find_pattern(data, pattern, klass=None):
            r = re.compile(pattern)
            if klass is None:
                return r.finditer(data)
            else:
                def i():
                    for m in r.finditer(data):
                        yield klass(m)
                return i()
        find_pattern = staticmethod(find_pattern)
        
        def find_urls(self, data):
            """ Return an iterator that yields a URLMatchObject for each URL in data. """
            return self.find_pattern(data, self.url_pattern, self.URLMatchObject)
        
        def find_hrefs(self, data):
            return self.find_pattern(data, self.href_pattern, self.URLMatchObject)
        
        def archive_pattern(self, progname):
            """ Return regexp pattern for archive filenames for progname. """
            return progname + r"\-([0-9][a-zA-Z0-9._\-]*)(.tar(.gz|.bz2)?|.zip|.exe|.dmg)$"
        
        def version_tuple(verstr, length=4):
            """ Return tuple of version numbers, padded with -1 to length to make sorting easier. """
            t = verstr.split('.')
            return tuple(map(int, t) + [-1]*(length - len(t)))
        version_tuple = staticmethod(version_tuple)
        
        def find_archives(self, data, progname, hrefs=False):
            """
            Return a list of 6-tuples, one for each archive URL for progname found in data.
            Each tuple contains <version-tuple>, <index>, <url>, <extension>, <filename>, where:
            
            <version-tuple> is the tuple of version numbers for sorting;
            
            <index> is the (inverse) index of the extension in the list of allowed extensions
            (it's inverted so that when we reverse sort, the preferred extension is first);
            
            <url> is the download URL;
            
            <extension> is the archive extension (used to determine its type);
            
            <filename> is the filename to be used to save the archive locally;
            
            <version> is the version string.
            
            If the hrefs parameter is true, only find URLs embedded in href tags. This
            is usually not necessary, hence defaults to False.
            """
            
            result = []
            r = re.compile(self.archive_pattern(progname))
            elist = self.allowed_extensions
            e = len(elist)
            if hrefs:
                f = self.find_hrefs
            else:
                f = self.find_urls
            for m in f(data):
                if m.pathname is not None:
                    f = r.search(m.pathname)
                    if f is not None:
                        version, ext, subext = f.groups()
                        i = elist.index(ext)
                        if i > -1:
                            result.append((self.version_tuple(version), e - i,
                                m.url, ext, f.group(), version))
            return result
        
        def get_latest_version(self, data, progname, hrefs=False):
            """
            Return the tuple for the latest version of progname, with the most
            preferred archive type if more than one is available of that version.
            If no archive with an allowed extension is found, print an error
            message and return None.
            """
            
            f = self.find_archives(data, progname, hrefs)
            result = None
            if f:
                f.sort() # sorts by version tuple, then inverse index
                f.reverse() # puts the latest at the top
                result = f[0]
            if result is None:
                print >>sys.stderr, "Could not find a usable archive for %s." % progname
            return result
        
        def download_url(self, url):
            request = urllib2.Request(url)
            request.add_header('User-Agent', self.user_agent)
            data = None
            try:
                f = urllib2.urlopen(request)
                try:
                    data = f.read()
                finally:
                    f.close()
            except urllib2.URLError:
                pass
            return data
        
        def download_pypi(self, req, link_data):
            # Find latest version and url by looking in link_data
            ver_tuple, index, url, ext, filename, version = self.get_latest_version(link_data, req)
            
            # Get download archive extension and determine commands and options
            if ext.startswith(".tar"):
                try:
                    opts = {'.gz': 'z', '.bz2': 'j'}[ext[4:]]
                except KeyError:
                    opts = ""
                unpack_cmd = "tar -x%svf " % opts
            elif ext == ".zip":
                unpack_cmd = "unzip "
            else:
                unpack_cmd = ""
            
            # Download actual archive data and save it locally (but
            # note that we check to see if it was previously
            # downloaded so we don't do it again)
            depfilename = os.path.join("deps", filename)
            if os.path.isfile(depfilename):
                print filename, "was previously downloaded."
            else:
                print "Downloading", filename
                data = self.download_url(url)
                if not os.path.isdir("deps"):
                    os.mkdir("deps")
                depfile = open(depfilename, 'wb')
                try:
                    depfile.write(data)
                finally:
                    depfile.close()
            
            # Save current working directory so we can return when done
            setup_dir = os.getcwd()
            
            # Unpack the source archive in the deps directory
            os.chdir("deps")
            unpack_dir = "%s-%s" % (req, version)
            if os.path.isdir(unpack_dir):
                print unpack_dir, "was previously unpacked."
            else:
                unpack_cmdline = "%s%s" % (unpack_cmd, filename)
                print "Executing", unpack_cmdline
                os.system(unpack_cmdline)
            
            # Chdir to the source root and run setup
            os.chdir(unpack_dir)
            install_cmdline = "python setup.py install%s" % self.setup_opts
            print "Executing", install_cmdline
            os.system(install_cmdline)
            
            # All done!
            os.chdir(setup_dir)
            print "Installed requirement %s." % req
        
        def process_reqs(self):
            """
            Resolve each requirement in requires list. The debug
            flag, if True, saves the downloaded html data from
            PyPI and each requirement's download page, for use
            in analyzing what's going on.
            """
            
            # Grab the PyPI simple index data
            pypi_data = self.download_url(self.pypi_url)
            if self._debug:
                self._pypi_data = pypi_data
                self._req_data = {}
            if pypi_data is not None:
                # Now process the requirements
                for req in self._requires:
                    # TODO: Strip version specifier off end and store
                    
                    # First try to import it -- assumes req is an importable name
                    try:
                        __import__(req)
                        print "Requirement %s found, no install needed." % req
                        continue
                    except ImportError:
                        pass
                    
                    # Next look in PyPI for it -- assumes req is a PyPI name
                    findstr = "<a href='%s/'>" % req
                    if findstr in pypi_data:
                        # Found it, load its link page
                        link_data = self.download_url('%s%s/' %
                            (self.pypi_url, req))
                        if link_data is not None:
                            if self._debug:
                                self._req_data[req] = link_data
                            self.download_pypi(req, link_data)
                            continue
                    
                    # If we get here, requirement was not found
                    print >>sys.stderr, \
                        "Could not find requirement %s; program may not run." % req
    
    return (RequiresHelper, Extension, setup)

def distutils_setuptools():
    """ Support function for setuptools. """
    
    from ez_setup import use_setuptools
    use_setuptools()
    
    from setuptools import setup
    from setuptools.extension import Extension
    return (None, Extension, setup)

class SetupHelper(object):
    """ Helper class to manage setup process. """
    
    overrides = [
        'distutils_pkg',
        'ext_class',
        'non_modules',
        'requires_class',
        'setup_func',
        'url_types' ]
    
    def dir_to_pkg(self, dirname):
        """ Converts relative directory path into dotted package name. """
        return dirname.replace('/', '.')
    
    def __init__(self, vars, **kwargs):
        # Store list of internal variables so we don't merge them
        # into setup args later -- note that we include variable names
        # that will be imported by your setup.py script, so that you
        # can simply call setup_main(globals()) or SetupHelper.setup_main
        # without worrying about setup_main or SetupHelper being
        # misinterpreted as keyword arguments
        internal_vars = dir(self)
        internal_vars.extend(['setup_main', 'SetupHelper'])
        
        # Get the setup variables passed to us by the setup script
        for varname, value in vars.iteritems():
            # Don't change the Python-provided vars
            if varname not in ('__builtins__', '__doc__', '__file__', '__name__'):
                setattr(self, varname, value)
        
        # Process overrides passed in keyword arguments, and set to None
        # any variables not otherwise set
        for varname in self.overrides:
            attrname = '__%s__' % varname
            value = kwargs.pop(varname, None)
            if (value is not None) or not hasattr(self, attrname):
                setattr(self, attrname, value)
        
        # Set defaults by distutils package
        if self.__distutils_pkg__ is None:
            self.__distutils_pkg__ = 'default'
        requires_class, ext_class, setup_func = getattr(sys.modules[__name__],
            'distutils_%s' % self.__distutils_pkg__)()
        del self.__distutils_pkg__
        # We only set variables that weren't already set above
        for varname in ('requires_class', 'ext_class', 'setup_func'):
            attrname = '__%s__' % varname
            if getattr(self, attrname) is None:
                setattr(self, attrname, locals()[varname])
        
        # The keyword args left over are treated as keyword args for the
        # setup function below
        self.__setup_args__ = dict(kwargs)
        internal_vars.extend(['__setup_func__', '__setup_args__']) # don't merge these either!
        
        # Process requires keyword if not using setuptools (in setuptools calling
        # the setup_func takes care of this) -- last thing before calling setup!
        if self.__requires_class__ is not None:
            # The distutils we're using doesn't know about these variables, so don't merge them
            internal_vars.extend(['__requires__', '__provides__', '__obsoletes__'])
            if hasattr(self, '__requires__'):
                self.__requires_class__(self.__requires__).process_reqs()
        del self.__requires_class__
        
        # crib our long description from the opening section of
        # the README file
        if hasattr(self, '__start_line__') and hasattr(self, '__end_line__'):
            if not hasattr(self, '__long_description__'):
                readme = open("README", 'rU')
                lines = []
                lastline = ""
                started = False
                try:
                    for line in readme:
                        line = line.strip()
                        if started:
                            if line == self.__end_line__:
                                break
                            else:
                                lines.append(lastline)
                        else:
                            if line == self.__start_line__:
                                started = True
                        lastline = line
                finally:
                    readme.close()
                self.__long_description__ = '\n'.join(lines)
            del self.__start_line__
            del self.__end_line__
        
        # We'll store the lines that need to go into MANIFEST.in here (and add
        # more below if applicable)
        self.__manifest_in__ = []
        if not hasattr(self, '__rootfiles__'):
            if hasattr(self, '__py_modules__') and ('SetupHelper' in self.__py_modules__):
                self.__rootfiles__ = []
            else:
                self.__rootfiles__ = ["SetupHelper.py"]
        if not hasattr(self, '__rootdirs__'):
            if hasattr(self, '__packages__') and ('SetupHelper' in self.__packages__):
                self.__rootdirs__ = []
            else:
                self.__rootdirs__ = ["SetupHelper"]
        for rootfile in self.__rootfiles__:
            if os.path.isfile(rootfile):
                self.__manifest_in__.append("include %s\n" % rootfile)
        for rootdir in self.__rootdirs__:
            if os.path.isdir(rootdir):
                self.__manifest_in__.append("recursive-include %s *.*\n" % rootdir)
                if rootdir == "SetupHelper":
                    # Don't include the byte-compiled module in source distributions
                    # (it will always be there because it had to be imported for this
                    # code to run!)
                    self.__manifest_in__.append("recursive-exclude SetupHelper *.pyc\n")
        
        # Figure out the pure Python modules list
        if self.__non_modules__ is None:
            self.__non_modules__ = []
        if not hasattr(self, '__py_modules__'):
            self.__py_modules__ = [entry[:-3] for entry in os.listdir(".")
                if entry.endswith(".py") and (entry != "setup.py")
                    and (entry not in self.__non_modules__)
                    and (entry not in self.__rootfiles__)]
        del self.__non_modules__
        del self.__rootfiles__
        
        # Figure out the extension modules list (do this first so we can filter
        # out extension directories from the package data list below)
        self.__ext_modules__ = []
        self.__ext_sourcedirs__ = []
        if hasattr(self, '__ext_names__'):
            if not hasattr(self, '__ext_src__'):
                self.__ext_src__ = 'src'
            if os.path.isabs(self.__ext_src__):
                ext_src_func = lambda extdir: self.__ext_src__
            else:
                ext_src_func = lambda extdir: os.path.normpath(
                    os.path.join(extdir, self.__ext_src__))
            for extpath in self.__ext_names__:
                extdir, extname = os.path.split(extpath)
                srcdir = ext_src_func(extdir)
                if os.path.isdir(srcdir):
                    self.__ext_modules__.append(self.__ext_class__(extpath,
                        sources=[os.path.join(srcdir, filename)
                            for filename in os.listdir(srcdir) if filename.endswith(".c")]))
                    self.__ext_sourcedirs__.append(srcdir)
            del self.__ext_src__
            del self.__ext_names__
        del self.__ext_class__
        
        # Figure out the package and package_data lists
        if not hasattr(self, '__packages__'):
            self.__packages__ = []
            process_packages = True
        else:
            process_packages = False
        if not hasattr(self, '__package_data__'):
            self.__package_data__ = {}
            process_packagedata = True
        else:
            process_packagedata = False
        if not hasattr(self, '__package_dirs__'):
            if not process_packages:
                self.__package_dirs__ = [p for p in self.__packages__
                    if "." not in p]
            elif hasattr(self, '__package_root__'):
                self.__package_dirs__ = [self.__package_root__]
            else:
                self.__package_dirs__ = [entry for entry in os.listdir(".")
                    if os.path.isdir(entry) and ("__init__.py" in os.listdir(entry))
                        and (entry not in self.__rootdirs__)]
        del self.__rootdirs__
        if process_packages or process_packagedata:
            for pkgdir in self.__package_dirs__:
                for directory, subdirs, files in os.walk(pkgdir):
                    if process_packages and ("__init__.py" in files):
                        self.__packages__.append(self.dir_to_pkg(directory))
                    elif process_packagedata and ("." not in directory) \
                        and (directory not in self.__ext_sourcedirs__):
                            parentdir, thisdir = os.path.split(directory)
                            pkg = self.dir_to_pkg(parentdir)
                            if not pkg in self.__package_data__:
                                self.__package_data__[pkg] = []
                            self.__package_data__[pkg].append("%s/*.*" % thisdir)
                            self.__manifest_in__.append("recursive-include %s *.*\n" % directory)
        if hasattr(self, '__package_root__'):
            del self.__package_root__
        del self.__ext_sourcedirs__
        
        # Figure out the scripts and data_files lists
        # NOTE: The extra jugglery with not "." in dirname and filename.startswith(".") is to mask
        # out hidden files and directories -- without this running setup from an svn working copy
        # goes haywire because it thinks that all the svn hidden files are scripts or data files
        if not hasattr(self, '__scripts__'):
            self.__scripts__ = []
            if not hasattr(self, '__script_root__'):
                self.__script_root__ = "scripts"
            if os.path.isdir(self.__script_root__):
                self.__scripts__.extend("%s/%s" % (directory, filename)
                    for directory, subdirs, files in os.walk(self.__script_root__)
                        if not "." in directory
                    for filename in files if not filename.startswith("."))
        if hasattr(self, '__script_root__'):
            del self.__script_root__
        if not hasattr(self, '__data_files__'):
            self.__data_files__ = []
            if not hasattr(self, '__data_dirs__'):
                self.__data_dirs__ = ["examples"]
                if (self.__progname__ not in self.__package_dirs__):
                    self.__data_dirs__.append(self.__progname__)
            for datadir in self.__data_dirs__:
                if os.path.isdir(datadir):
                    if datadir == self.__progname__:
                        pathprefix = "lib"
                    else:
                        pathprefix = "share/%s" % self.__progname__
                    self.__data_files__.extend(("%s/%s" % (pathprefix, directory),
                        ["%s/%s" % (directory, filename) for filename in files
                            if not filename.startswith(".")])
                        for directory, subdirs, files in os.walk(datadir)
                            if files and not "." in directory)
                    self.__manifest_in__.append("recursive-include %s *.*\n" % datadir)
        if hasattr(self, '__data_dirs__'):
            del self.__data_dirs__
        del self.__package_dirs__
        
        # Write MANIFEST.in -- tmp file first so we don't clobber the current
        # one if there's a problem
        manifest_in = open("MANIFEST.in.tmp", 'w')
        try:
            manifest_in.writelines(self.__manifest_in__)
        finally:
            manifest_in.close()
        if os.path.isfile("MANIFEST.in"):
            os.rename("MANIFEST.in", "MANIFEST.in.old")
        os.rename("MANIFEST.in.tmp", "MANIFEST.in")
        if os.path.isfile("MANIFEST.in.old"):
            os.remove("MANIFEST.in.old")
        del self.__manifest_in__
        
        # Determine download URL -- assume the base is the PyPI base URL
        # if no base is given
        if not hasattr(self, '__url_base__'):
            self.__url_base__ = pypi_base_url(self.__progname__)
        if not hasattr(self, '__url_ext__'):
            if not hasattr(self, '__url_type__'):
                self.__url_ext__ = 'tar.gz'
            else:
                if self.__url_types__ is None:
                    self.__url_types__ = {'posix': "tar.gz", 'nt': "zip", 'mac': "dmg"}
                try:
                    self.__url_ext__ = self.__url_types__[self.__url_type__]
                except KeyError:
                    self.__url_ext__ = self.__url_type__
                del self.__url_type__
        self.__download_url__ = "%s/%s-%s.%s" % (
            self.__url_base__, self.__progname__, self.__version__, self.__url_ext__)
        del self.__url_types__
        del self.__url_base__
        del self.__url_ext__
        
        # Fill in default license text if none specified
        if not hasattr(self, '__license__'):
            self.__license__ = "unknown"
        
        # Convert classifiers from long string to list
        if hasattr(self, '__classifiers__'):
            self.__classifiers__ = self.__classifiers__.strip().splitlines()
        else:
            self.__classifiers__ = []
        
        # Now merge the rest of the variables into the setup args; note
        # that we merge instead of updating so that keyword arguments
        # passed to the setup script override variables set in its globals
        for varname in dir(self):
            if varname not in internal_vars:
                if varname == '__progname__':
                    # Special case this one, we can't use __name__ because it is
                    # a special Python variable for modules already
                    setup_arg = 'name'
                elif varname != '__post_install__':
                    # Strip the leading and trailing underscores
                    setup_arg = varname.strip('_')
                if setup_arg not in self.__setup_args__:
                    self.__setup_args__[setup_arg] = getattr(self, varname)
    
    def do_setup(self):
        """
        This does the actual work; we separate it out to allow hooking into
        the process after the setup args are parsed above but before the
        function call.
        """
        
        self.__setup_func__(**self.__setup_args__)
    
    def do_post_install(self):
        """
        This runs any post-install scripts that are defined; again, we
        separate this out to allow hooking after the install but before
        the post-install scripts run.
        """
        
        if hasattr(self, '__post_install__') and self.__post_install__:
            print "Running post-install scripts..."
            for scriptname in self.__post_install__:
                os.system(scriptname)

# TODO: convert long option of the form --<option-name>=<value> to keyword argument option_name=value

def setup_main(vars, **kwargs):
    helper = SetupHelper(vars, **kwargs)
    helper.do_setup()
    if 'install' in sys.argv:
        helper.do_post_install()
