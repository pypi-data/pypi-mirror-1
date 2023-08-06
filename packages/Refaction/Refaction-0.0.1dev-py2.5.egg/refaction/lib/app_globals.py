"""app_globals.py - Refaction Globals object

Copyright (C) 2008 Emanuel Calso <egcalso [at] gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
from pylons import config
from pycrud.lib.app_globals import Globals as GlobalBase


class Globals(GlobalBase):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        super(Globals, self).__init__()
        self.session = {}
        self.permissions = {
                1 : {
                        '*': ('*', ),
                    },
                2 : dict(
                    ),
                3 : dict(
                    ),
            }
        self.user = config['webfaction_user']
        self.passwd = config['webfaction_passwd']

    def new_session(self, id, user=None):
        class Session(object):
            def __init__(self, id, user):
                from datetime import datetime
                self.id = id
                self.login = datetime.now()
                self.user = user
        self.session[id] = Session(id, user)
        return self.session[id]

