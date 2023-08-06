"""bitarray: module for efficiently storing bits in a list-like object"""
import os
from distutils.core import setup, Extension

kwds = {}

# Read the long description from the README
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, 'README'))
kwds['long_description'] = f.read()
f.close()


setup(
    name = "bitarray",
    version = "0.2.2",
    author = "Ilan Schnell",
    author_email = "ilanschnell@gmail.com",
    url = "http://pypi.python.org/pypi/bitarray/",
    license = "PSF",
    classifiers = [
        "License :: OSI Approved :: Python Software Foundation License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    description = __doc__,
    
    packages = ["bitarray"],
    ext_modules = [Extension(name = "bitarray._bitarray",
                             sources=["bitarray/_bitarray.c"])],
    **kwds
    )
