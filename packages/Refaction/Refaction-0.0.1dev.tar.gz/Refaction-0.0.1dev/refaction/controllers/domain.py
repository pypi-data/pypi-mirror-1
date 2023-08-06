"""domain.py Refaction domain controller

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

class DomainController(ListController):
    table = model.Domain
    children = dict(
            subdomain = dict(
                    table = model.Subdomain,
                    columns = ['name', ],
                ),
        )

    def delete(self):
        self._check_entry_permission()
        self.delete_domain()
        return super(DomainController, self).delete()

    def delete_domain(self):
        entry = self.table.get(request.params['id'])
        s = WebFaction()
        s.login(g.user, g.passwd)
        s.delete_domain(entry.name)

    def render_show_children(self):
        return render('/domain/show_children.mako')

    def save(self):
        """Override saving the process
        """
        self._check_entry_permission()
        self.save_domain()
        return super(DomainController, self).save()

    def save_domain(self):
        p = request.params
        s = WebFaction()
        s.login(g.user, g.passwd)
        try:
            subdomains = p.dict_of_lists()['subdomain.name']
        except KeyError:
            subdomains = ['', 'www']
        if '' not in subdomains:
            subdomains.append('')
        if 'www' not in subdomains:
            subdomains.append('www')
        if 'id' in p:
            s.modify_domain(p['name'], *subdomains)
        else:
            s.create_domain(p['name'], *subdomains)




