"""app.py - Refaction app controller

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

import logging

from refaction.lib.base import *
from refaction.lib.webfaction import WebFaction

log = logging.getLogger(__name__)

class AppController(ListController):
    table = model.App
    hidden_columns = set(['id', 'autostart'])

    def delete(self):
        self._check_entry_permission()
        self.delete_app()
        return super(AppController, self).delete()

    def delete_app(self):
        entry = self.table.get(request.params['id'])
        s = WebFaction()
        s.login(g.user, g.passwd)
        s.delete_app(entry.name)

    def render_edit(self):
        return render('/app/edit.mako')

    def save(self):
        """Override saving the process
        """
        self._check_entry_permission()
        self.save_app()
        return super(AppController, self).save()

    def save_app(self):
        s = WebFaction()
        s.login(g.user, g.passwd)
        p = request.params
        if 'id' in p:
            s.modify_app(p['name'], p['type'], extra_info=p['extra_info'])
        else:
            s.create_app(p['name'], p['type'], extra_info=p['extra_info'])


