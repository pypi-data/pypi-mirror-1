"""users.py Refaction users controller

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
import crypt

log = logging.getLogger(__name__)

class UsersController(ListController, RestrictedController):
    table = model.User
    parent = dict(
            role = dict(
                    table = model.Role,
                    column = 'name',
                ),
        )
    columns_hidden = set([
            'id',
            'password',
            'details',
        ])

    def _generate_salt(self):
        import string
        import random
        chars = string.digits + string.letters
        return random.choice(chars) + random.choice(chars)

    def _save_custom(self, params):
        if params['password'] != params['password2']:
            redirect_to('invalid')
        salt = self._generate_salt()
        params['password'] = crypt.crypt(str(params['password']), salt)
        return params

    def edit(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        super(UsersController, self).edit(id)
        return render('/user/edit.mako')

    def add(self):
        self._dbg('add')
        self._add()
        return render('/user/new.mako')

    def submit(self):
        self._dbg('save')
        try:
            id = request.params['id']
        except KeyError:
            id = None
        entry = self._save(id, request.params)
        self._dbg('save', entry.id)
        redirect_to('list')
        return 'Saved'



