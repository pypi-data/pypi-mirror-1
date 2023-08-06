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
Exception filters for director.
"""

__docformat__ = 'restructuredtext'


import exceptions
import sys


class Filter(list):
    """
    Holds all filters to execute on exception.
    """

    def execute_filters(self, exception):
        """
        Executes all filters with an exception.

        :Parameters:
            - `exception`: the exception that is going to be filtered.

        """
        for filter in self:
            filter.filter(exception)

    def register_filter(self, exception_filter):
        """
        Registers an ExceptionFilter.

        :Parameters:
            - `exception_filter`: the ExceptionFilter to add.
        """
        for filter in self:
            if type(exception_filter.exception('')) == \
                    type(filter.exception('')):
                txt = 'You can only have one filter for one exception: %s' % (
                       exception_filter.exception)
                raise Exception(txt)
        self.append(exception_filter)


class ExceptionFilter(object):
    """
    Parent class for all filters.
    """

    def __init__(self, exception, error_text="%s"):
        """
        Creates the ExceptionFilter object.

        :Parameters:
            - `exception`: the exception to filter.
            - `error_text`: the error text to show,
        """
        self.exception = exception
        self.error_text = error_text

    def filter(self, exception):
        """
        Filters an exception. True on filter, False otherwise.

        :Parameters:
            - `exception`: the exception being filtered.
        """
        if type(exception) == type(self.exception('')):
            if "%s" in self.error_text:
                print >> sys.stderr, self.error_text % exception
            else:
                print >> sys.stderr, self.error_text
            return True
        return False
