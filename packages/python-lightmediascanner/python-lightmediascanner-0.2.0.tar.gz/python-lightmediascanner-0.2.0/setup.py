import sys
import os

from ez_setup import use_setuptools
use_setuptools('0.6c3')

from setuptools import setup, find_packages, Extension
import commands

from Cython.Distutils import build_ext


def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    pkgs = ' '.join(packages)
    cmdline = 'pkg-config --libs --cflags %s' % pkgs

    status, output = commands.getstatusoutput(cmdline)
    if status != 0:
        raise ValueError("could not find pkg-config module: %s" % pkgs)

    for token in output.split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw


module = Extension('lightmediascanner.c_lightmediascanner',
                   sources=['lightmediascanner/lightmediascanner.c_lightmediascanner.pyx',
                            ],
                   depends=['include/lightmediascanner/c_lightmediascanner.pxd',
                            ],
                   **pkgconfig('"lightmediascanner >= 0.2.0"'))


trove_classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]


long_description = """\
Python bindings for Light Media Scanner.

Lightweight media scanner meant to be used in not-so-powerful devices,
like embedded systems or old machines.

Provides an optimized way to recursively scan directories, handling
the parser in a child process, avoiding breaks of the main process
when parsers break (quite common with such bad libs and tags). One can
opt to use the single process version, but be aware that if something
bad happens during parsing, your application will suffer.

Parsers are plugins in the form of shared objects, so it's easy to add
new without having to recompiling the scanner.

The scanner will use SQLite3 to store file-mtime association, avoiding
parsing files that are already up-to-date. This SQLite connection and
the file id within the master table 'files' are handled to plugins for
relationship with other tables.
"""


class lms_build_ext(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        self.include_dirs.insert(0, 'include')
        self.pyrex_include_dirs.extend(self.include_dirs)


setup(name='python-lightmediascanner',
      version='0.2.0',
      license='LGPL',
      author='Gustavo Sverzut Barbieri',
      author_email='barbieri@profusion.mobi',
      description='Python bindings for Light Media Scanner',
      long_description=long_description,
      keywords='wrapper binding media scanner',
      classifiers=trove_classifiers,
      packages=find_packages(),
      ext_modules=[module],
      zip_safe=False,
      cmdclass={'build_ext': lms_build_ext,},
      )
