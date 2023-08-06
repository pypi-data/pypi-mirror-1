import logging

from divimon.lib.base import *
from divimon import model
from pylons.decorators import jsonify

log = logging.getLogger(__name__)

def get_id(entry):
    return getattr(entry, 'id')

class CommitController(BaseController):

    def __after__(self):
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

    #@jsonify
    def test(self):
        data = dict(
                one = 1,
                two = 2,
                three = 3
            )
        entries = map(get_id, model.list(model.Agent))
        data['entries'] = entries
        data['request'] = request.params
        response.content_type = 'text/plain'
        return data

    def open_remote(self):
        from urllib import FancyURLopener
        opener = FancyURLopener()
        server = '10.0.2.2:5001'
        #url = request.params['url']
        #content = opener.open('http://%s/login' % (server), data='user:admin\npassword:admin')
        content = opener.open('http://%s/commit/test' % (server), data='user=admin&password=admin')
        #print content
        print dir(content)
        print content.headers
        #print content.readlines()
        #response.content_type = 'text/plain'
        return '\n'.join(content.readlines())

    def _get_last_commit(self):
        query = model.list(model.History)
        query = query.filter_by(controller='commit').order_by(model.History.c.created.desc())
        return query[0]

    def items(self):
        last_commit = self._get_last_commit().created
        response.content_type = 'text/plain'
        response.cache = 'no'
        return last_commit


