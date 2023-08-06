"""bitarray: module for efficiently storing bits in a list-like object"""
from distutils.core import setup, Extension
import os

kwds = {}

# Read the long description from the README.txt
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, 'README.txt'))
kwds['long_description'] = f.read()
f.close()


setup(
    name = "bitarray",
    version = "0.1.0",
    author = "Ilan Schnell",
    author_email = "ilanschnell@gmail.com",
    download_url = "http://www.enthought.com/~ischnell/bitarray-0.1.0.tar.gz",
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
    
    py_modules = ["bitarray"],
    ext_modules = [Extension("_bitarray",
                             sources=["_bitarray.c"])],
    **kwds
    )
