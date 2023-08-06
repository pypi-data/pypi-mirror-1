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
Main classes for director.
"""

__docformat__ = 'restructuredtext'
__version__ = '1.2.0'
__license__ = 'GPLv3+'
__author__ = "Steve 'Ashcrow' Milner"


import inspect
import os
import sys
import types
import warnings

import director.error

from optparse import OptionParser

from director import codes
from director.decorators import general_help


class Action(object):
    """
    Base class for command line actions.
    """

    description_txt = "Base action class"

    def __init__(self):
        """
        Create the Action object. Do not override.
        """
        self._startup_hook()

    def __del__(self):
        """
        Work to do when the object is deleted. Do not override.
        """
        self._shutdown_hook()

    def __repr__(self):
        """
        String representation of the object.
        """
        return "<%s Action>" % self.__class__.__name__

    def _startup_hook(self):
        """
        Hook for doing work on creation of the object. It's not in
        __init__ just so that we keep __init__ clean.
        """
        pass

    def _shutdown_hook(self):
        """
        Hook for doing work on deletion of the object. It's not in
        __del__ just so that we keep __del__ clean.
        """
        pass

    def _list_verbs(self):
        """
        Lists all available verbs.
        """
        verbs = []
        for item in dir(self):
            if item[0] != '_':
                if type(self.__getattribute__(item)) == types.MethodType:
                    verbs.append(item)
        return verbs

    def _action_help(self):
        """
        Formats and shows help for all available verbs in an action.
        """
        print >> sys.stderr, "Usage: myapp [verb] [--opt=val]..."
        print >> sys.stderr, "%s\n" % self.description_txt
        for verb in self._list_verbs():
            print >> sys.stderr, "%s -" % verb,
            self.help(verb)
            print >> sys.stderr, "\n"

    @general_help("Detailed help information about the action.",
                  {'verb': 'verb to get help on'},
                  ['myapp list help --verb=help'])
    def help(self, verb=None):
        """
        Detailed help information about the action.

        :Parameters:
            - `verb`: what to get help on.

        Do not override.
        """
        # If we have no verb then give available verbs and a usage message
        if not verb:
            print self.description()
            return

        try:
            print >> sys.stderr, self.__getattribute__(verb).help
        except:
            raise director.error.UnsuportedHelpStyleError(
                'Unsupported help style being used.')

    @general_help("Quick blurb about the action.",
                  examples=['myapp list description'])
    def description(self):
        """
        Quick blurb about the action.

        Do not override. See description_txt
        """
        verbs = ", ".join(self._list_verbs())
        print >> sys.stderr, "%s.\nAvailable verbs: %s" % (
                                      self.description_txt, verbs)
        print >> sys.stderr, "For more detailed usage use myapp \
noun help add --verb=verb."


class ActionRunner(object):
    """
    In charge of running plugins based on information passed in via arguments.
    """

    def __init__(self, args, plugin_package):
        """
        Creates the ActionRunner object.

        :Parameters:
            - `args`: all args passed from command line.
            - `plugin_package`: the name of the package where plugins live.
        """
        self.plugin_package = plugin_package
        self.args = args

        if not len(self.args[1:]) >= 2:
            self.__list_nouns()
            print >> sys.stderr, "Please give at least a noun and a verb."
            raise SystemExit(codes.system.NOT_ENOUGH_PARAMETERS)
        # Get all the options passed in
        self.noun, self.verb = args[1:3]

        # Generate the code based from the input
        action = __import__("%s.%s" % (self.plugin_package, self.noun),
                            globals(),
                            locals(),
                            [self.noun])
        self.action_to_run = action.__getattribute__(self.noun.capitalize())()
        self.options = self.parse_options()

    def __list_nouns(self):
        """
        Lists all available nouns.
        """
        action_mod = __import__(self.plugin_package)
        print >> sys.stderr, "Available nouns:",
        # Get the module path from __path__ of action_mod and plugin_package
        mod_path = os.path.join(action_mod.__path__[0],
                                self.plugin_package.split('.')[-1])
        # Go over each and print out the ones that are actions
        for noun in os.listdir(mod_path):
            if "__" not in noun and '.pyc' not in noun:
                print >> sys.stderr, "%s " % noun.replace('.py', ''),
        print >> sys.stderr, ""

    def parse_options(self):
        """
        Parse the options into something that can be passed to a method.

        Returns a usable dictionary to pass to a method.
        """
        parser = OptionParser()
        a_verb = self.action_to_run.__getattribute__(self.verb)
        # Since decorators change what inspect sees we try to use the original
        # method directly which gets attached as a_verb.meth. If it doesn't
        # exist then we try the method directly as it is either old style,
        # using direct method variables or has no help at all.
        try:
            inspection_data = [x for x in inspect.getargspec(a_verb.meth)]
        except:
            inspection_data = [x for x in inspect.getargspec(a_verb)]

        if inspection_data[0] == None:
            inspection_data[0] = []
        iargs = [x for x in reversed(inspection_data[0][1:])]
        if inspection_data[3] == None:
            inspection_data[3] = []
        iargs_defaults = [x for x in reversed(inspection_data[3])]

        defaults = {}
        for iarg_x in range(len(iargs)):
            # Default action is to store
            action = 'store'
            try:
                # Make sure we set up defaults
                def_item = iargs_defaults[iarg_x]
                if type(def_item) == types.TupleType:
                    def_item = def_item[0]
                defaults[iargs[iarg_x]] = def_item

                # Setup the action if it is a bool
                if defaults[iargs[iarg_x]] == True:
                    action = 'store_true'
                elif defaults[iargs[iarg_x]] == False:
                    action = 'store_false'
            except IndexError, ie:
                # Not everything has a default
                pass

            # Add it to optparse
            parser.add_option("--%s" % iargs[iarg_x],
                              dest=iargs[iarg_x],
                              action=action)

        # Bind the defaults
        parser.set_defaults(**defaults)
        options, largs = parser.parse_args(self.args[3:])
        return options.__dict__

    def run_code(self):
        """
        Takes care of running the code created.

        code is the code to execute.
        """
        self.action_to_run.__getattribute__(
            self.verb).__call__(**self.options)

    def run(self, filter_obj=None):
        """
        Runs the generated code.

        :Parameters:
            - `filter_obj`: the filter object.
        """
        try:
            self.run_code()
        except Exception, ex:
            # If we have a filters then use them ...
            if filter_obj:
                filter_obj.execute_filters(ex)
            else:
                # If we have no filters then raise the exception
                raise ex
            raise SystemExit(codes.system.EXCEPTION_RAISED)
