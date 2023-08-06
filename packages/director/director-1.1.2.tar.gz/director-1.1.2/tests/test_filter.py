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
Tests for filter.
"""

__docformat__ = 'restructuredtext'


import exceptions
import unittest

from director.filter import Filter
from director.filter import ExceptionFilter


class FilterTests(unittest.TestCase):
    """
    Tests the Filter object.
    """

    def setUp(self):
        """
        Sets up stuff for the test.
        """
        self.filter = Filter()

    def tearDown(self):
        """
        Tears down after each test.
        """
        del self.filter

    def test_register_filter(self):
        """
        Tests the register_filter method.
        """
        self.filter.register_filter(ExceptionFilter(exceptions.IOError, 'ERR'))
        self.assertEqual(len(self.filter), 1)

    def test_execute_filters(self):
        """
        Tests the execute_filters method.
        """
        self.filter.execute_filters(exceptions.Exception(''))


class ExceptionFilterTests(unittest.TestCase):
    """
    Tests the code for ExceptionFilters.
    """

    def setUp(self):
        """
        Sets up stuff for the test.
        """
        self.exception_filter = ExceptionFilter(exceptions.IOError)

    def tearDown(self):
        """
        Tears down after each test.
        """
        del self.exception_filter

    def test_filter(self):
        """
        Tests the filter functionality.
        """
        self.exception_filter.filter(exceptions.IOError(''))
        self.exception_filter.filter(exceptions.TypeError(''))
