import logging

from divimon.lib.base import *
import pickle

log = logging.getLogger(__name__)

class BaseController(BaseController):
    tables = (
            'User',
			'Item',
			'Inventory',
			'Agent',
			'Customer',
			'Cheque',
			'DeliveryReceipt',
			'Budget',
			'Expense',
        )

    def __after__(self):
        return
        env = dict(request.environ.items())
        wsgi = env['wsgiorg.routing_args'][1]
        if wsgi['action'] in ('login', 'logout', 'index', 'list') or wsgi['controller'] in ('index',):
            return
        #ht_session = self._get_cookie()
        history = model.History(
                #user = ht_session.user.id,
                user = None,
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
        #TODO: Authenticate by ip address using env['REMOTE_ADDR']
        #ht_session = self._get_cookie()
        #self._check_permission(ht_session)

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return 'Hello World'

    def _entry2dict(self, entry):
        d = dict()
        try:
            children = entry.children
        except AttributeError:
            children = dict()
        for child,tbl in children.iteritems():
            d[child] = self._get_child(entry, child, tbl)
        for k in self.tbl.c.keys():
            d[k] = getattr(entry, k)
        del d['id']
        return d

    def _dict2entry(self, row):
        entry = self.tbl(**row)
        return entry

    def _save_entries_from_dict(self, rows):
        entries = []
        for row in rows:
            print row
            entries.append(self._dict2entry(row))
        return entries


class Child(BaseController):
    def __init__(self, tbl):
        self.tbl = getattr(model, tbl)

    def get_entries(self, parent):
        model.list(self.tbl)


class Remote(BaseController):

    def _save_entry(self, entry):
        try:
            children = self.tbl.children
        except AttributeError:
            children = dict()
        child_rows = dict()
        for k,v in children.iteritems():
            child_rows[k] = entry[k]
            del entry[k]
        entry = self._dict2entry(entry)
        for k,v in children.iteritems():
            c = Child(v)
            setattr(entry, k, c._save_entries_from_dict(child_rows[k]))
        return entry


