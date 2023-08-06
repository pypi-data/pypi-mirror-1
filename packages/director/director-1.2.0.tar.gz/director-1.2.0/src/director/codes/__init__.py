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
Code symbols package.
"""

__docformat__ = 'restructuredtext'
__all__ = ['system']


# Import all items in __all__ in the current context
for item in __all__:
    exec('from director.codes import %s' % item)
