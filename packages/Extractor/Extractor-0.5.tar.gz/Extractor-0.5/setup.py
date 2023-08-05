#!/bin/env/python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "Extractor",
    version = "0.5",

    py_modules = ['extractor'],
    scripts = ['extract.py'],

    #install_requires = ['ctypes >= 0.9'],

    # metadata for upload to PyPI
    author = "Bader Ladjemi, Christian Grothoff",
    author_email = "libextractor@gnu.org",
    description = "Python bindings for GNU libextractor",
    license = "GNU GPL",
    keywords = "libextractor binding tag metadata",
    url = "http://gnunet.org/libextractor/",  

    dependency_links=['http://starship.python.net/crew/theller/ctypes/',],

    long_description="""libextractor is a simple library for keyword extraction.  libextractor
does not support all formats but supports a simple plugging mechanism
such that you can quickly add extractors for additional formats, even
without recompiling libextractor. libextractor typically ships with a
dozen helper-libraries that can be used to obtain keywords from common
file-types.  

libextractor is a part of the GNU project (http://www.gnu.org/).""",
    
    classifiers=['Development Status :: 3 - Alpha',
		 'Intended Audience :: Developers',
		 'License :: OSI Approved :: GNU General Public License (GPL)',
		 'Operating System :: OS Independent',
		 'Operating System :: MacOS :: MacOS X',
		 'Operating System :: Microsoft :: Windows',
		 'Operating System :: POSIX',
		 'Topic :: System :: Filesystems',
		 'Topic :: Text Processing :: Filters'],
    
    platforms=['windows', 'Linux', 'MacOS X', 'Solaris', 'FreeBSD'],
    
)
