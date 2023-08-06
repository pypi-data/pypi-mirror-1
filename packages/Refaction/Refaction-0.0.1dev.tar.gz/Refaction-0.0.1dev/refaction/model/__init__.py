'''model/__init__.py - Refaction model

Refaction model

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

'''

from pycrud.model import *


app = Table('app', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('type', Unicode(128), default=u''),
        Column('autostart', Boolean, default=False),
        Column('extra_info', Unicode(128), default=u''),
        Column('owner', Integer, ForeignKey('user.id')),
    )

cron = Table('cron', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('owner', Integer, ForeignKey('user.id')),
    )

db = Table('db', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('db_type', Unicode(128), default=u''),
        Column('password', Unicode(128), default=u''),
        Column('owner', Integer, ForeignKey('user.id')),
    )

domain = Table('domain', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('owner', Integer, ForeignKey('user.id')),
    )

dns = Table('dns', meta,
        Column('id', Integer, primary_key=True),
        Column('domain', Unicode(128), default=u''),
        Column('a_ip', Unicode(128), default=u''),
        Column('cname', Unicode(128), default=u''),
        Column('mx_name', Unicode(128), default=u''),
        Column('mx_priority', Unicode(128), default=u''),
        Column('spf_record', Unicode(128), default=u''),
        Column('owner', Integer, ForeignKey('user.id')),
    )

email = Table('email', meta,
        Column('id', Integer, primary_key=True),
        Column('email_address', Unicode(128), default=u'', unique=True),
        Column('targets', Unicode(128), default=u''),
        Column('autoresponder_on', Boolean, default=False),
        Column('autoresponder_subject', Unicode(128), default=u''),
        Column('autoresponder_message', UnicodeText, default=u''),
        Column('autoresponder_from', Unicode(128), default=u''),
        Column('owner', Integer, ForeignKey('user.id')),
    )

mailbox = Table('mailbox', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('enable_spam_protection', Boolean, default=True),
        Column('share', Boolean, default=False),
        Column('owner', Integer, ForeignKey('user.id')),
    )

role = Table('role', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(256), nullable=False, default=u''),
    )

site = Table('site', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        Column('owner', Integer, ForeignKey('user.id')),
    )

site_app = Table('site_app', meta,
        Column('id', Integer, primary_key=True),
        Column('app', Integer, ForeignKey('app.id')),
        Column('path', Unicode(128), default=u'/'),
        Column('site', Integer, ForeignKey('site.id')),
    )

site_domain = Table('site_domain', meta,
        Column('id', Integer, primary_key=True),
        Column('subdomain', Integer, ForeignKey('subdomain.id')),
        Column('site', Integer, ForeignKey('site.id')),
    )

subdomain = Table('subdomain', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u''),
        Column('domain', Integer, ForeignKey('domain.id')),
    )

user = Table('user', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(256), nullable=False, default=u''),
        Column('password', Unicode(256), nullable=False, default=u''),
        Column('role', Integer, ForeignKey('role.id')),
        Column('email_address', Unicode(256), nullable=False, default=u''),
        Column('details', Unicode(1024), default=u''),
    )


App = map_table(app)
Cron = map_table(cron)
DB = map_table(db)
DNS = map_table(dns)
Email = map_table(email)
MailBox = map_table(mailbox)
SiteApp = map_table(site_app)
SiteDomain = map_table(site_domain)
Site = map_table(site, properties=dict(
        application = relation(SiteApp),
        subdomain = relation(SiteDomain),
    ))
Subdomain = map_table(subdomain)
Domain = map_table(domain, properties=dict(
        subdomain = relation(Subdomain),
    ))
User = map_table(user)
Role = map_table(role, properties=dict(
        user = relation(User),
    ))


def get_name(cls, id):
    return cls.get(id).name

App.get_name = classmethod(get_name)
Subdomain.get_name = classmethod(get_name)


