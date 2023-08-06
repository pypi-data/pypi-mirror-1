#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.core import Extension
from distutils.file_util import copy_file
from distutils.util import get_platform
from sys import version, exit
import os.path
import glob
from os import popen3, mkdir
from shutil import copy2

LIBIGRAPH_FALLBACK_INCLUDE_DIRS = ['/usr/include/igraph', '/usr/local/include/igraph']
LIBIGRAPH_FALLBACK_LIBRARIES = ['igraph']
LIBIGRAPH_FALLBACK_LIBRARY_DIRS = []

if version < '2.3':
    print "This module requires Python >= 2.3"
    exit(0)
    
def get_output(command):
    """Returns the output of a command returning a single line of output"""
    to_child, from_child, err_child = popen3(command)
    to_child.close()
    err_child.close()
    line=from_child.readline().strip()
    exit_code=from_child.close()
    return line, exit_code
    
def detect_igraph_include_dirs(default = LIBIGRAPH_FALLBACK_INCLUDE_DIRS):
    """Tries to detect the igraph include directory"""
    line, exit_code = get_output("pkg-config igraph --cflags")
    if exit_code>0 or len(line) == 0: return default
    opts=line.split()
    return [opt[2:] for opt in opts if opt[0:2]=="-I"]

def detect_igraph_libraries(default = LIBIGRAPH_FALLBACK_LIBRARIES):
    """Tries to detect the libraries that igraph uses"""
    line, exit_code = get_output("pkg-config igraph --libs")
    if exit_code>0 or len(line) == 0: return default
    opts=line.split()
    return [opt[2:] for opt in opts if opt[0:2]=="-l"]
    
def detect_igraph_library_dirs(default = LIBIGRAPH_FALLBACK_LIBRARY_DIRS):
    """Tries to detect the igraph library directory"""
    line, exit_code = get_output("pkg-config igraph --libs")
    if exit_code>0 or len(line) == 0: return default
    opts=line.split()
    return [opt[2:] for opt in opts if opt[0:2]=="-L"]

sources=glob.glob(os.path.join('src', '*.c'))
include_dirs=[]
library_dirs=[]
libraries=[]

line, exit_code = get_output("pkg-config igraph")
if exit_code>0:
    print "Using default include and library paths for compilation"
    print "If the compilation fails, please edit the LIBIGRAPH_FALLBACK_*"
    print "variables in setup.py to point to the correct directories"
    print "and libraries where the C core of igraph is installed"
    print
    
include_dirs.extend(detect_igraph_include_dirs())
library_dirs.extend(detect_igraph_library_dirs())
libraries.extend(detect_igraph_libraries())

print "Include path:", " ".join(include_dirs)
print "Library path:", " ".join(library_dirs)

igraph_extension = Extension('igraph.core', sources, \
  library_dirs=library_dirs, libraries=libraries, \
  include_dirs=include_dirs)
       
description = """Python interface to the igraph high performance graph
library, primarily aimed at complex network research and analysis.

Graph plotting functionality is provided by the Cairo library, so make
sure you install the Python bindings of Cairo if you want to generate
publication-quality graph plots.
See the `Cairo homepage <http://cairographics.org/pycairo>`_ for details.

From release 0.5, the C core of the igraph library is **not** included
in the Python distribution - you must compile and install the C core
separately. Windows installers already contain a compiled igraph DLL,
so they should work out of the box. Linux users should refer to the
`igraph homepage <http://cneurocvs.rmki.kfki.hu/igraph>`_ for
compilation instructions (but check your distribution first, maybe
there are pre-compiled packages available). OS X Leopard users may
benefit from the meta-package available on the igraph homepage.
"""

plat = get_platform()
data_files = []
if "macosx" in plat:
    data_files = [('/usr/lib', ['/usr/local/lib/libigraph.dylib', \
                                '/usr/local/lib/libigraph.0.dylib', \
                                '/usr/local/lib/libigraph.0.0.0.dylib'])]

setup(name = 'python-igraph',
      version = '0.5.1',
      description = 'High performance graph data structures and algorithms',
      long_description = description,
      license = 'GNU General Public License (GPL)',
      author = 'Tamas Nepusz',
      author_email = 'ntamas@rmki.kfki.hu',
      ext_modules = [igraph_extension],
      package_dir = {'igraph': 'package'},
      packages = ['igraph', 'igraph.test', 'igraph.app'],
      scripts = ['scripts/igraph'],
      data_files = data_files,
      platforms = 'ALL',
      keywords = ['graph', 'network', 'mathematics', 'math', 'graph theory', 'discrete mathematics'],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
