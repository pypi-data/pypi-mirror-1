#!/usr/bin/env jython

"""
Really crappy distutils substitute for jython

by Michael Hoffman <hoffman@ebi.ac.uk>
"""

__version__ = "$Revision: 1.4 $"

from fnmatch import fnmatch
from glob import glob
import imp
import os
import shutil
import sys
import unittest

BUILD_DIR = "build/lib.java-%s" % sys.version[:3]
LIB_DIR = "javalib"
TEST_DIR = "javatest"
INSTALL_DIR = sys.path[2]

TEST_GLOB = os.path.join(TEST_DIR, "test_*.py")
PY_GLOB = "*.py"
PKG_NAME = "metascript"

def mkdict(**d): return d

def copytree_fnmatch(src, dst, globspec, symlinks=0):
    """
    from shutil.copytree
    """

    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                if name not in ["CVS", "RCS"]:
                    copytree_fnmatch(srcname, dstname, globspec, symlinks)
            else:
                if fnmatch(dstname, globspec):
                    shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))


def command_build():
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    copytree_fnmatch("javalib", os.path.join(BUILD_DIR, PKG_NAME), PY_GLOB)

def command_test():
    sys.path.insert(0, TEST_DIR)
    sys.path.insert(0, BUILD_DIR)

    for filename in glob(TEST_GLOB):
        modulename = os.path.splitext(os.path.basename(filename))[0]
        module = __import__(modulename)
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
        unittest.TextTestRunner().run(tests)

def command_install():
    # so it won't complain if the directory already exists
    copytree_fnmatch(os.path.join(BUILD_DIR, PKG_NAME),
                     os.path.join(INSTALL_DIR, PKG_NAME), "*")

COMMANDS = mkdict(build=command_build,
                  test=command_test,
                  install=command_install)

def main():
    COMMANDS[sys.argv[1]]()

if __name__ == "__main__":
    main()
