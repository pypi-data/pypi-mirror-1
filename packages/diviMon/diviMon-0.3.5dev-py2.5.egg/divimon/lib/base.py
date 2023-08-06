"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.

AUTHOR: Emanuel Gardaya Calso

"""

from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
#from pylons.templating import render, render_response
from pylons import templating

import divimon.lib.helpers as h
import divimon.model as model
from child import ChildList

def render(*args, **kw):
    return templating.render(*args, **kw)


class PropertyList(object):
    def __init__(self, parent, field, table):
        self.parent = parent
        self.entries = getattr(parent, field)
        self.table = table
        # Remove all entries first
        for entry in list(self.entries):
            self.entries.remove(entry)

    def save(self, c_id):
        entry = model.get(self.table, c_id)
        if entry not in self.entries:
            self.entries.append(entry)
        return


class BaseController(WSGIController):

    def __after__(self):
        env = dict(request.environ.items())
        wsgi = env['wsgiorg.routing_args'][1]
        if wsgi['action'] in ('login', 'logout', 'index', 'list') or wsgi['controller'] in ('index',):
            return
        ht_session = self._get_cookie()
        history = model.History(
                user = ht_session.user.id,
                controller = unicode(wsgi['controller']),
                action = unicode(wsgi['action']),
                arguments = unicode(env['QUERY_STRING']),
                #c = str(c.__dict__),
            )
        model.Session.save(history)
        model.Session.commit()
        return
        #print request.path_info
        #print env['REMOTE_ADDR']
        #print request.params
        #print g.session

    def __before__(self, action, **kw):
        env = {}
        for k,v in request.environ.items():
            env[k]=v
        env['SCRIPT_NAME'] = ''
        import routes
        config = routes.request_config()
        config.environ = env
        ht_session = self._get_cookie()
        self._check_permission(ht_session)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def _check_permission(self, session):
        '''Check permission'''
        env = dict(request.environ.items())
        wsgi = env['wsgiorg.routing_args'][1]
        controller = wsgi['controller']
        action = wsgi['action']
        if action in ('error', 'login', 'logout') or controller in ('index', ):
            return
        user = session.user
        permission = g.permissions[user.role]
        #print user.role
        #print permission
        if '*' in permission.keys() or '*' in permission.get(controller, ()):
            return
        if action not in permission.get(controller, ()):
            return redirect_to('/error?msg=Cannot view %s.' % (request.path_info))

    def _dbg(self, function=None, msg=None):
        _ = '%s.%s' % (__name__, self.__class__.__name__)
        if function is not None:
            _ += '.' + str(function)
        if msg is not None:
            _ += ': ' + str(msg)
        return _

    def _get_cookie(self):
        if request.cookies.get('id', None) in g.session:
            return g.session[request.cookies.get('id')]
        else:
            if not request.path_info.endswith('error') and not request.path_info.endswith('login'):
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

    def error(self, msg=None):
        if msg is not None:
            c.msg = msg
        else:
            c.msg = request.params['msg']
        return render('/error.mako')

    def login(self):
        self._dbg('login', request.cookies)
        c_id = request.cookies.get('id', None)
        if 'user' in request.params.keys():
            # Get User
            username = request.params['user']
            password = request.params['password']
            try:
                user = model.Session.query(model.User).filter_by(name=username)[0]
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
        redirect_to('index')

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


class TableController(BaseController):
    table = None


class ListController(TableController):
    parent = dict()
    children = dict()
    properties = ()
    list_functions = (
            'delete',
            'add',
        )
    entry_functions = (
            'delete',
            'edit',
            'details',
        )
    columns_shown = set([
        ])
    columns_hidden = set([
            #'id',
        ])
    column_descriptions = dict()

    def __init__(self):
        c.title = self.__class__.__name__.replace('Controller', '')
        c.table = self.table
        c.columns = c.table.c.keys()
        c.parent = self.parent
        c.children = self.children
        c.properties = self.properties
        c.db_sess = model.Session
        c.page = 1
        c.max_entries = 20
        c.list_functions = self.list_functions
        c.entry_functions = self.entry_functions
        c.columns_shown = self.columns_shown
        c.columns_hidden = self.columns_hidden
        c.column_descriptions = self.column_descriptions
        self._init_custom()

    def _init_custom(self):
        pass

    def _add(self):
        c.id = None
        c.entry = self.table()

    def _details(self, id):
        c.id = id
        c.entry = model.Session.query(c.table).get(id)

    def _delete(self, id):
        entry = model.Session.query(c.table).get(id)
        model.Session.delete(entry)
        model.Session.flush()
        model.Session.commit()
        self._dbg('_delete', '%s Successfully deleted' % entry)

    def _list(self):
        c.entries = self.query

    def _list_params(self):
        if 'page' in request.params.keys():
            c.page = int(request.params['page'])

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())

    def _multi(self):
        self._dbg('_multi', request.params.dict_of_lists())
        ids = self._multi_get_ids()
        function=request.params['function']
        if function == g.function_delete:
            self._multi_delete(ids)
        return

    def _multi_delete(self, ids):
        map(self._delete, ids)

    def _multi_get_ids(self):
        try:
            ids = request.params.dict_of_lists()['select']
        except KeyError:
            args = []
            for k,v in request.params.iteritems():
                args.append('%s=%s' % (k,v))
            redirect_to(str('list?%s' % '&'.join(args)))
        return ids

    def _save(self, id=None, params=request.params):
        all_args = self._save_custom(params)
        entry_args = {}
        child_args = {}
        # Sorting of fields for parent and children
        for k in all_args.keys():
            if k in self.table.c.keys():
                entry_args[k] = all_args[k]
            else:
                child_args[k] = all_args.dict_of_lists()[k]
        entry = self._save_entry(id, entry_args)
        self._dbg('_save', '%s Successfully saved' % entry)
        self._save_children(entry, **child_args)
        self._save_properties(entry, **child_args)
        model.Session.save_or_update(entry)
        model.Session.commit()
        return entry

    def _save_children(self, entry, **kw):
        for field, children in self.children.iteritems():
            child_list = ChildList(entry, field, children)
            child_list.multi_save(**kw)
        return entry

    def _save_custom(self, params):
        return params

    def _save_entry(self, id, entry_args):
        # Saving of entry
        if id is not None:
            entry = model.get(self.table, id)
            for k,v in entry_args.iteritems():
                setattr(entry, k, v)
        else:
            entry = self.table(**entry_args)
        return entry

    def _save_properties(self, entry, **kw):
        for field,col,tbl in self.properties:
            prop = PropertyList(entry, field, tbl)
            try:
                c_ids = request.params.dict_of_lists()[field]
            except KeyError:
                continue
            self._dbg('add_properties', (field, c_ids))
            map(prop.save, c_ids)
        return

    def add(self):
        self._dbg('add')
        self._add()
        return self.render_edit()

    def blank_out(self):
        return ''

    def details(self, id):
        self._dbg('details', request.params)
        self._details(request.params['id'])
        return self.render_details()

    def delete(self):
        self._dbg('delete', request.params)
        self._delete(request.params['id'])
        redirect_to('index')

    def edit(self, id):
        self._dbg('edit', request.params)
        self._details(request.params['id'])
        return self.render_edit()

    def list(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return self.render_list()

    index = list

    def multi(self):
        self._dbg('delete')
        self._multi()
        return self.list()

    def save(self):
        self._dbg('save')
        try:
            id = request.params['id']
        except KeyError:
            id = None
        entry = self._save(id, request.params)
        self._dbg('save', entry.id)
        redirect_to('list')
        return 'Saved'

    # Children and Properties methods

    def _edit_child(self):
        c.cnt = request.params['cnt']
        c.child = request.params['child']
        c.columns = self.children[c.child]['columns']
        c.child_details = self.children[c.child]
        c.table = self.children[c.child]['table']

    def add_child(self):
        self._edit_child()
        return self.render_add_child()

    def add_children(self, parent, **kw):
        for child in self.children.keys():
            try:
                self._dbg('add_children', 'Save Child:\n%s' % request.params.dict_of_lists()[child])
            except KeyError:
                break
        return

    def add_properties(self, parent, **kw):
        for field,col,db_tbl in self.properties:
            prop = Property(parent, field, db_tbl)
            try:
                c_ids = request.params.dict_of_lists()[field]
            except KeyError:
                break
            self._dbg('add_properties', (field, c_ids))
            map(prop.add, c_ids)
        model.Session.save_or_update(parent)
        model.Session.commit()
        return

    def edit_child(self):
        self._edit_child()
        c.entry = model.get(c.table, request.params['c_id'])
        c.p_id = request.params['p_id']
        return self.render_edit_child()

    def rem_child(self, id):
        child = request.params['child']
        p_id = request.params['p_id']
        table = self.children[child]['table']
        parent = model.get(self.table, p_id)
        entry = model.get(table, id)
        children = getattr(parent, child)
        children.remove(entry)
        model.Session.update(parent)
        model.Session.commit()
        return ''

    def render_add_child(self):
        return render('/add_child.mako')

    def render_details(self):
        return render('/details.mako')

    def render_edit(self):
        return render('/edit.mako')

    def render_edit_child(self):
        return render('/edit_child.mako')

    def render_list(self):
        return render('/list.mako')

    def show_children(self, id):
        c.id = id
        try:
            c.parent = model.get(self.table, id)
        except TypeError:
            c.parent = self.table()
        c.child = request.params['child']
        c.children = getattr(c.parent, c.child)
        c.child_details = self.children[c.child]
        return render('/show_children.mako')


class AJAXController(TableController):

    def __init__(self):
        self._init_custom()

    def _init_custom(self):
        pass


# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']

