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

__docformat__ = 'restructuredtext'


import os
import sys

from distutils.core import Command, setup
from glob import glob
from os.path import basename, walk, splitext
from os.path import join as pjoin
from os import path
from unittest import TextTestRunner, TestLoader

sys.path.insert(0, 'src')
sys.path.insert(1, 'tests')

from director import __version__, __license__, __author__


class SetupBuildCommand(Command):
    """
    Master setup build command to subclass from.
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
        """
        pass


class RPMBuildCommand(SetupBuildCommand):
    """
    Creates an RPM based off spec files.
    """

    description = "Build an rpm based off of the top level spec file(s)"

    def run(self):
        """
        Run the RPMBuildCommand.
        """
        try:
            if os.system('./setup.py sdist'):
                raise Exception("Couldn't call ./setup.py sdist!")
                sys.exit(1)
            if not os.access('dist/rpms/', os.F_OK):
                os.mkdir('dist/rpms/')
            dist_path = os.path.join(os.getcwd(), 'dist')
            rpm_cmd = 'rpmbuild -ba --define "_rpmdir %s/rpms/" \
                                    --define "_srcrpmdir %s/rpms/" \
                                    --define "_sourcedir %s" *spec' % (
                      dist_path, dist_path, dist_path)
            if os.system(rpm_cmd):
                raise Exception("Could not create the rpms!")
        except Exception, ex:
            print >> sys.stderr, str(ex)


class SphinxCommand(SetupBuildCommand):
    """
    Creates HTML documentation using Sphinx.
    """

    description = "Generate documentation via sphinx"

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

            # And build!
            app.builder.build_all()
            print "Your docs are now in %s" % outdir
        except ImportError, ie:
            print >> sys.stderr, "You don't seem to have the following which"
            print >> sys.stderr, "are required to make documentation:"
            print >> sys.stderr, "\tsphinx.application.Sphinx"
        except Exception, ex:
            print >> sys.stderr, "FAIL! exiting ... (%s)" % ex


class ViewDocCommand(SetupBuildCommand):
    """
    Quick command to view generated docs.
    """

    def run(self):
        """
        Opens a webbrowser on docs/html/index.html
        """
        import webbrowser

        print ("NOTE: If you have not created the docs first this will not be "
               "helpful. If you don't see any documentation in your browser "
               "run ./setup.py doc first.")
        if not webbrowser.open('docs/html/index.html'):
            print >> sys.stderr, "Could not open on your webbrowser."


class TestCommand(SetupBuildCommand):
    """
    Distutils testing command.
    """

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


class TODOCommand(SetupBuildCommand):
    """
    Quick command to show code TODO's.
    """

    description = "prints out TODO's in the code"

    def run(self):
        """
        Prints out TODO's in the code.
        """
        import re

        format_str = "%s (%i): %s"

        # If a TODO exists, read it out
        try:
            line_no = 0
            todo_obj = open('TODO', 'r')
            for line in todo_obj.readlines():
                print format_str % ("TODO", line_no, line[:-1])
                line_no += 1
            todo_obj.close()
        except:
            pass

        remove_front_whitespace = re.compile("^[ ]*(.*)$")
        for rootdir in ['src/', 'bin/']:

            for root, dirs, files in os.walk(rootdir):
                for afile in files:
                    if afile[-4:] != '.pyc':
                        full_path = os.path.join(root, afile)
                        fobj = open(full_path, 'r')
                        line_no = 0
                        for line in fobj.readlines():
                            if 'todo' in line.lower():
                                nice_line = remove_front_whitespace.match(
                                    line).group(1)
                                print format_str % (full_path,
                                                       line_no,
                                                       nice_line)
                            line_no += 1


setup(name = "director",
    version = __version__,
    description = "Command line plugin library",
    long_description = """\
director is a python library that allows developers to create command line
plugins for tools making it easy to add new functionality.""",
    author = __author__,
    author_email = 'smilner+director@redhat.com',
    url = "https://fedorahosted.org/director/",
    download_url = "https://fedorahosted.org/releases/d/i/director/",
    platforms = ['any'],

    license = __license__,

    package_dir = {'director': 'src/director'},
    packages = ['director', 'director.codes'],

    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python'],

    cmdclass = {'test': TestCommand,
                'doc': SphinxCommand,
                'viewdoc': ViewDocCommand,
                'rpm': RPMBuildCommand,
                'todo': TODOCommand})
