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
Code symbols for system related items.

- *SYSTEM_OK*: Exit to shell if everything was OK.
- *NOT_ENOUGH_PARAMETERS*: Exit to shell if not enough parameters are passed.
- *EXCEPTION_RAISED*: Exit to the shell if an exception is raised.
"""

__docformat__ = 'restructuredtext'


SYSTEM_OK = 0
NOT_ENOUGH_PARAMETERS = 1
EXCEPTION_RAISED = 2
