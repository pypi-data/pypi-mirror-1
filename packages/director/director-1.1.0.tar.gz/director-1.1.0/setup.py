#!/usr/bin/env python
#
# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Standard build script.
"""

import sys
import os
from glob import glob
from distutils.core import Command, setup
from unittest import TextTestRunner, TestLoader
from os.path import basename, walk, splitext
from os.path import join as pjoin
from os import path


sys.path.insert(0, 'src')
sys.path.insert(1, 'tests')

from director import __version__, __license__, __author__


class SphinxCommand(Command):
    """
    Creates HTML documentation using Sphinx.
    """

    user_options = []
    description = "Generate documentation via sphinx"

    def initialize_options(self):
        """
        Setup the current dir.
        """
        self._dir = os.getcwd()

    def finalize_options(self):
        """
        No clue ... but it's required.
        """
        pass

    def run(self):
        """
        Run the DocCommand.
        """
        print "Creating html documentation ..."

        try:
            from sphinx.application import Sphinx

            if not os.access(path.join('docs', 'html'), os.F_OK):
                os.mkdir(path.join('docs', 'html'))
            buildername = 'html'
            outdir = path.abspath(path.join('docs', 'html'))
            doctreedir = os.path.join(outdir, '.doctrees')

            confdir = path.abspath('docs')
            srcdir = path.abspath('docs')
            freshenv = False

            # Create the builder
            app = Sphinx(srcdir, confdir, outdir, doctreedir, buildername,
                         {}, sys.stdout, sys.stderr, freshenv)

            #os.chdir('..')
            # And build!
            app.builder.build_all()
            print "Your docs are now in %s" % outdir
        except ImportError, ie:
            print >> sys.stderr, "You don't seem to have the following which"
            print >> sys.stderr, "are required to make documentation:"
            print >> sys.stderr, "\tsphinx.application.Sphinx"
        except Exception, ex:
            print >> sys.stderr, "FAIL! exiting ... (%s)" % ex


class TestCommand(Command):
    """
    Distutils testing command.
    """
    user_options = []

    def initialize_options(self):
        """
        Setup the current dir.
        """
        self._dir = os.getcwd()

    def finalize_options(self):
        """
        No clue ... but it's required.

        @param self: Internal Command object.
        @type self: Command
        """
        pass

    def run(self):
        """
        Finds all the tests modules in tests/, and runs them.
        """
        testfiles = []
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]]))

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 2)
        t.run(tests)


setup(name = "director",
    version = __version__,
    description = "Command line plugin library",
    long_description = """\
director is a python library that allows developers to create command line \
plugins for tools making it easy to add new functionality.
""",
    author = __author__,
    author_email = 'smilner+director@redhat.com',
    url = "https://fedorahosted.org/director/",
    download_url = "https://fedorahosted.org/releases/d/i/director/",
    platforms = ['any'],

    license = __license__,

    package_dir = {'director': 'src/director'},
    packages = ['director'],

    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python'],

    cmdclass = {'test': TestCommand,
                'doc': SphinxCommand})
