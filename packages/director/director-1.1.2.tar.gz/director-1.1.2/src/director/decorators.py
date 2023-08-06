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
All decorators for director.
"""

__docformat__ = 'restructuredtext'


def simple_help(help_txt):
    """
    Adds a help variable to a class method as well as saving the original
    method as meth. This is best used for very simple help cases.

    :Parameters:
        - `help_txt`: the text to add as help text.
    """

    def decorator(meth):
        """
        Top level inner decorator which takes in a class method.

        :Parameters:
            - `meth`: the actual class method.
        """

        def wrapper(self, *args, **kwargs):
            """
            Internal wrapper that actually executes the method.

            :Parameters:
                - `self`: the class methods container object.
                - `*args`: any non keyword arguments.
                - `**kwargs`: all keyword arguments.
            """
            return meth(self, *args, **kwargs)

        # Add help variable and it's text
        wrapper.help = help_txt
        # Attach the original method as meth for inspection
        wrapper.meth = meth
        return wrapper

    return decorator


def general_help(desc, options={}, examples=[]):
    """
    Adds a help variable to a class method based on keyword arguments as well
    as saving the original method as meth. This can be used in more verbose
    help cases.

    :Parameters:
        - `desc`: the description.
        - `options`: a dictionary mapping options and their descriptions.
        - `examples`: a list of examples.
    """

    def decorator(meth):
        """
        Top level inner decorator which takes in a class method.

        :Parameters:
            - `meth`: the actual class method.
        """

        def wrapper(self, *args, **kwargs):
            """
            Internal wrapper that actually executes the method.

            :Parameters:
                - `self`: the class methods container object.
                - `*args`: any non keyword arguments.
                - `**kwargs`: all keyword arguments.
            """
            return meth(self, *args, **kwargs)

        # Put together the rendered help string
        rendered = "\n%s\n" % desc
        if options:
            rendered += "OPTIONS:"
            for key in options.keys():
                rendered += "\n\t%s\t%s" % (key, options[key])
        if examples:
            rendered += "\nEXAMPLES:"
            for example in examples:
                rendered += "\n\t%s" % example

        # Add help variable and it's text
        wrapper.help = rendered
        # Attach the original method as meth for inspection
        wrapper.meth = meth
        return wrapper

    return decorator
