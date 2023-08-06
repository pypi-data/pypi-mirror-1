"""website.py - Refaction website controller

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

class WebsiteController(ListController):
    table = model.Site
    children = dict(
            application = dict(
                    table = model.SiteApp,
                    columns = ['app', 'path', ],
                    parent = dict(
                            app = dict(
                                    table = model.App,
                                    column = 'name',
                                ),
                        ),
                ),
            subdomain = dict(
                    table = model.SiteDomain,
                    columns = ['subdomain', ],
                    parent = dict(
                            subdomain = dict(
                                    table = model.Subdomain,
                                    column = 'name',
                                ),
                        ),
                ),
        )

    def _get_applications(self, p):
        apps = map(model.App.get_name, p.dict_of_lists()['application.app'])
        paths = p.dict_of_lists()['application.path']
        return zip(apps, paths)

    def _get_subdomains(self, p):
        entries = map(model.Subdomain.get, p.dict_of_lists()['subdomain.subdomain'])
        subdomains = []
        for entry in entries:
            subdomains.append('.'.join([
                    entry.name,
                    model.Domain.get(entry.domain).name
                ]).lstrip('.'))
        return subdomains

    def delete(self):
        self._check_entry_permission()
        self.delete_website()
        return super(WebsiteController, self).delete()

    def delete_website(self):
        entry = self.table.get(request.params['id'])
        s = WebFaction()
        s.login(g.user, g.passwd)
        s.delete_website(entry.name)


    def render_add_child(self):
        return render('/website/add_child.mako')

    def render_edit_child(self):
        return render('/website/edit_child.mako')

    def render_show_children(self):
        return render('/website/show_children.mako')

    def save(self):
        """Override saving the process
        """
        self._check_entry_permission()
        self.save_website()
        return super(WebsiteController, self).save()

    def save_website(self):
        s = WebFaction()
        s.login(g.user, g.passwd)
        p = request.params
        subdomains = self._get_subdomains(p)
        apps = self._get_applications(p)
        if 'id' in p:
            s.modify_website(p['name'], subdomains=subdomains, site_apps=apps)
        else:
            s.create_website(p['name'], subdomains=subdomains, site_apps=apps)


