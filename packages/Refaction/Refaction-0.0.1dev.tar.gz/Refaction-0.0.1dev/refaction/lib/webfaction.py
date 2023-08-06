"""webfaction.py - Refaction API to webfaction API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.

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

import xmlrpclib
from pylons import config

default_ip = config['webfaction_ip']

class WebFaction(object):
    def __init__(self):
        '''
        '''
        self.server = xmlrpclib.Server('https://api.webfaction.com/')

    def login(self, user, password):
        '''
        '''
        self.session_id, self.account =  self.server.login(str(user), str(password))
        return (self.session_id, self.account)

    def create_app(self, name, app_type, autostart=False, extra_info=''):
        '''
        name - must only contain letters, digits, or '_'
        app_type - can be:
            * static
                - This will be a static/cgi/php website served in apache
            * symlink
                - This will be a symbolic link pointing to "extra_info" which should be an absolute path
                - Assign the absolute path to "extra_info"
            * subversion
                - This will create a subversion repository
                - Assign "anonymous_read" to "extra_info" if you want anonymous read access
            * webdav
                - This will be a web-exposed directory pointing to "extra_info", which should be an absolute path
                - Assign the absolute path to "extra_info"
        '''
        return self.server.create_app(self.session_id, name, app_type, autostart, extra_info)

    def create_domain(self, domain, *subdomains):
        '''
        domain - must be a valid domain
        '''
        return self.server.create_domain(self.session_id, domain, *subdomains)

    def create_website(self, website_name, ip=default_ip, https=False, subdomains=[], site_apps=[]):
        '''
        website_name - must only contain letters, digits, '-', or '_'
        '''
        return self.server.create_website(self.session_id, website_name, ip, https, subdomains, *site_apps)

    def delete_app(self, name):
        '''
        '''
        return self.server.delete_app(self.session_id, name)

    def delete_domain(self, name):
        '''
        '''
        return self.server.delete_domain(self.session_id, name)

    def delete_website(self, name):
        '''
        '''
        return self.server.delete_website(self.session_id, name)

    def modify_app(self, name, app_type, autostart=False, extra_info=''):
        '''
        '''
        self.delete_app(name)
        return self.create_app(name, app_type, autostart, extra_info)

    def modify_domain(self, domain, *subdomains):
        '''
        '''
        self.delete_domain(domain)
        return self.create_domain(domain, *subdomains)

    def modify_website(self, website_name, ip=default_ip, https=False, subdomains=[], *site_apps):
        '''
        '''
        self.delete_website(website_name)
        return self.create_website(website_name, ip, https, subdomains, *site_apps)


