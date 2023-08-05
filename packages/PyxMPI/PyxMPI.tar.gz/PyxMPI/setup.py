from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, Extension
from subprocess import Popen, PIPE

import sys, os, re

def shget(*args):
    return Popen(args, stdout=PIPE).communicate()[0]

# A new command for predist, ie: pyrexc but no compile.
import distutils.ccompiler
class NullCompiler(distutils.ccompiler.CCompiler):
    executables = ()
    def __init__(self, *args, **kw):
        pass
    def compile(self, *args, **kw):
        return []
    def link(self, *args, **kw):
        pass

# Pyrex makes some messy C code so limit some warnings when we know how.
import distutils.sysconfig
if (distutils.sysconfig.get_config_var('CC') or '').startswith("gcc"):
    pyrex_compile_options = ['-w']
else:
    pyrex_compile_options = []

# Will need to alter this on different systems:
if os.environ.has_key('LAMHOME'):
    LAMHOME = os.environ['LAMHOME']
    mpiargs = dict(
        include_dirs = [os.path.join(LAMHOME, 'include')],
        library_dirs = [os.path.join(LAMHOME, 'lib')],
        libraries = ['mpi'],
        )
else:
    try:
        mpiargs = dict(
            extra_compile_args = shget('mpicc', '--showme:compile').split(),
            extra_link_args = shget('mpicc', '--showme:link').split(),
            )
    except OSError:
        mpiargs = dict(
        include_dirs = [],
        library_dirs = [],
        libraries = ['mpi'],
        )

extra = "extra_compile_args"
mpiargs[extra] = mpiargs.get(extra, []) + pyrex_compile_options

setup(
    name = "PyxMPI",
    version = "1.0",
    download_url = "http://jcsmr.anu.edu.au/org/dmb/compgen/PyxMPI-1.0.tar.gz",
    author = "Peter Maxwell",
    author_email = "pm67nz@gmail.com",
    description = "Pyrex wrapper for MPI (Message Passing Interface) 1.1",
    platforms = ["any"],
    license = ["GPL"],
    keywords = ["MPI", "parallel"],
    classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Topic :: System :: Clustering",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Operating System :: OS Independent",
            ],    ext_modules=[
        Extension("mpi", ["mpi.pyx"], **mpiargs),
    ],
)
