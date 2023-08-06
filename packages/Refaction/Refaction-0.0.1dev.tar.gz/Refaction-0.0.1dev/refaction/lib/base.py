"""base.py - Refaction base Controller API

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

from pycrud.lib.base import *
from pycrud.lib.base import ListController as ListBaseController, BaseController as BaseBaseController
import refaction.lib.helpers as h
import refaction.model as model

pycrud.lib.base.model = model

class OwnedController(BaseBaseController):

    def __after__(self):
        return

    def __before__(self, action, **kw):
        env = dict(request.environ.items())
        env['SCRIPT_NAME'] = ''
        import routes
        config = routes.request_config()
        config.environ = env
        wsgi = env['wsgiorg.routing_args'][1]
        if wsgi['action'] in ('login', 'logout', 'restricted') or  wsgi['controller'] in ('index', 'template',):
            return
        ht_session = self._get_cookie()
        self._check_permission(ht_session)
        return

    def _check_permission(self, session):
        '''Check permission'''
        self._dbg('_check_permission')
        return

    def _get_cookie(self):
        self._dbg('_get_cookie')
        if request.cookies.get('id', None) in g.session:
            return g.session[request.cookies.get('id')]
        else:
            if not request.path_info.endswith('restricted') and not request.path_info.endswith('login'):
                redirect_to('%s/login' % g.base_url)

    def _new_session(self, user):
        '''Create new session
        _new_session(self, user) -> ht_session
        Create a unique ID from request.GET to create a new ht_session entry
        Then save the session id in the cookies
        '''
        ht_session = g.new_session(
                id = str(id(request.GET)),
                user = user,
            )
        response.cookies['id'] = ht_session.id
        return ht_session


class RestrictedController(OwnedController):

    def _check_permission(self, session):
        '''Check permission'''
        self._dbg('_check_permission')
        env = dict(request.environ.items())
        wsgi = env['wsgiorg.routing_args'][1]
        controller = wsgi['controller']
        action = wsgi['action']
        if action in ('restricted', 'login', 'logout') or controller in ('index', ):
            return
        user = session.user
        permission = g.permissions[user.role]
        if '*' in permission.keys() or '*' in permission.get(controller, ()):
            return
        if action not in permission.get(controller, ()):
            return redirect_to('/restricted?msg=Cannot view %s.' % (request.path_info))
        return

class BaseController(OwnedController):

    def _get_session(self):
        c.session = g.session.get(request.cookies.get('id'), None)
        try:
            c.session_user = c.session.user
        except:
            c.session_user = None

    def _verify_user(self, user, password):
        '''Verify if username and password are correct
        _verify_user(user, password) -> bool
        '''
        try:
            from crypt import crypt
            salt = user.password[:2]
            if user.password != crypt(password, salt):
                return False
        except ImportError:
            if user.password != password:
                return False
        return True

    def login(self):
        self._dbg('login', request.cookies)
        c_id = request.cookies.get('id', None)
        if 'user' in request.params.keys():
            # Get User
            username = request.params['user']
            password = request.params['password']
            try:
                user = model.User.list().filter_by(name=username)[0]
            except IndexError:
                c.msg = 'Invalid username or password'
                return render('/login.mako')
            if self._verify_user(user, password):
                ht_session = self._new_session(user)
            else:
                c.msg = 'Invalid username or password'
                return render('/login.mako')
        else:
            return render('/login.mako')
        self._dbg('logged in as %s' % ht_session.user)
        redirect_to('/')

    def logout(self):
        self._dbg('logout', request.cookies)
        c.msg = ''
        c_id = request.cookies.get('id', None)
        ht_session = g.session.get(c_id, None)
        try:
            del response.cookies['id']
            del request.cookies['id']
        except KeyError:
            response.cookies['id'] = None
            request.cookies['id'] = None
        try:
            c.msg += '<p>Good bye %s.</p>' % ht_session.user
        except AttributeError:
            pass
        c.msg +=  '<p>Successfully logged out.</p>'
        redirect_to('login')

    def restricted(self, msg=None):
        if msg is not None:
            c.msg = msg
        else:
            c.msg = request.params['msg']
        return render('/restricted.mako')


class ListController(ListBaseController, BaseController):
    columns_hidden = set(['id', 'owner', ])

    def _check_entry_permission(self):
        self._get_session()
        if c.session_user.role == 1:
            return
        try:
            e_id = request.params['id']
        except KeyError:
            return
        entry = self.table.get(e_id)
        if entry.owner != c.session_user.id:
            return redirect_to('/restricted?msg=%s Not allowed for this entry.' % (request.path_info))
        return

    def _get_permission(self):
        self._get_session()
        self._check_entry_permission()
        if c.session_user.role == 1:
            try:
                c.columns_hidden.remove('owner')
            except KeyError:
                pass
        else:
            c.columns_hidden.add('owner')
        owner_info = dict(
                table = model.User,
                column = 'name',
            )
        if not hasattr(self, 'parent'):
            self.parent = {}
        self.parent['owner'] = owner_info

    def _save_custom(self, params):
        if 'owner' not in params:
            params['owner'] = c.session_user.id
        return params

    def add(self):
        self._get_permission()
        return super(ListController, self).add()

    def delete(self):
        self._get_permission()
        return super(ListController, self).delete()

    def details(self, id):
        self._get_permission()
        return super(ListController, self).details(id)

    def edit(self, id):
        self._get_permission()
        return super(ListController, self).edit(id)

    def _list_query(self):
        super(ListController, self)._list_query()
        if c.session_user.role != 1:
            self.query = self.query.filter_by(owner=c.session_user.id)

    def list(self, *args, **kw):
        self._get_permission()
        return super(ListController, self).list()
    index = list

    def multi(self):
        self._get_permission()
        return super(ListController, self).multi()

    def save(self):
        self._get_permission()
        return super(ListController, self).save()


# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']

