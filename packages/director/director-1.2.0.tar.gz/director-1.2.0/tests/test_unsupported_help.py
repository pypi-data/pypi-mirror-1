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
Test of unsupported help styles.
"""

__docformat__ = 'restructuredtext'


import unittest

import director.error

from director import Action


class Fake(Action):

    def method(self, input):
        """
        Doc string.

        == help ==
        this is the help message.
        == end help ==
        """
        return input


class UnsupportedHelpTests(unittest.TestCase):
    """
    Tests to verify that unsupported help doesn't pass through.
    """

    def setUp(self):
        """
        Sets up stuff for the test.
        """
        self.fake_obj = Fake()

    def test_simple_help(self):
        """
        Make sure we get a proper exception.
        """
        #self.assertEqual(self.fake_obj.method.help, "Test of help")
        self.assertRaises(director.error.UnsuportedHelpStyleError,
            self.fake_obj.help, ('method', ))
