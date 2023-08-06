import logging

from base import *

log = logging.getLogger(__name__)

class ClientController(Remote):

    def _check_for_commit(self):
        latest, server_latest = self._get_latest()
        self.latest = latest
        self.server_latest = server_latest
        if server_latest is None:
            return True
        if latest is None or latest <= server_latest:
            return False
        return True

    def _check_for_update(self):
        latest, server_latest = self._get_latest()
        self.latest = latest
        self.server_latest = server_latest
        if latest is None:
            return True
        if server_latest is None or latest >= server_latest:
            return False
        return True

    def _commit_to_server(self, table, s):
        data = 'table=%s&data=%s' % (table, s)
        server = 'localhost:5002'
        from urllib import FancyURLopener
        opener = FancyURLopener()
        h = opener.open('http://%s/remote/server/%s' % (
                server,
                'commit',
            ),
            data=data)
        print 'http://%s/remote/server/%s' % (server, 'commit')
        print data
        content = h.read()
        return content

    def _get_child(self, entry, child, tbl):
        children = []
        c = Child(tbl)
        for row in getattr(entry, child):
            children.append(c._entry2dict(row))
        return children

    def _get_entries_for_commit(self):
        entries = model.list(self.tbl)
        if self.server_latest is not None:
            entries = entries.filter(self.tbl.c.created>self.server_latest)
        return entries

    def _get_latest(self):
        entries = model.list(self.tbl).order_by(self.tbl.c.created.desc())
        try:
            latest = entries[0].created
        except IndexError:
            latest = None
        server_latest = self._get_server_latest()
        return latest, server_latest

    def _get_from_server(self, path, data=''):
        from urllib import FancyURLopener
        opener = FancyURLopener()
        server = 'localhost:5002'
        #content = opener.open('http://%s/%s' % (server, path), data='user=admin&password=admin')
        print 'http://%s/remote/server/%s' % (server, path)
        #h = opener.open('http://%s/remote/server/%s' % (server, path))
        h = opener.open('http://%s/remote/server/%s' % (
                server,
                path,
            ),
            data=data)
        content = h.read()
        #print content
        data = pickle.loads(content)
        return data

    def _get_server_latest(self):
        latest = self._get_from_server('get_latest?table=%s' % (request.params['table']))
        return latest
    
    def _get_server_update(self, table, latest):
        data = self._get_from_server('update', 'table=%s&latest=%s' % (
                table,
                pickle.dumps(latest),
                #pickle.dumps(latest).replace('\n', '\\n')
                #'latest',
            ))
        return data

    def commit(self):
        '''Commit changes to the server
        '''
        table = request.params['table']
        self.tbl = getattr(model, table)
        if not self._check_for_commit():
            print 'Update first'
            return False
        for entry in self._get_entries_for_commit():
            d = self._entry2dict(entry)
            s = pickle.dumps(d)
            result = self._commit_to_server(table, s)
        return True

    def update(self):
        '''Get updates from the server
        '''
        table = request.params['table']
        self.tbl = getattr(model, table)
        if not self._check_for_update():
            print 'Already up to date'
            return False
        #return True
        rows = self._get_server_update(table, self.latest)
        print rows
        for row in rows:
            entry = self._save_entry(row)
            model.Session.save(entry)
        model.Session.commit()
        return True

    def index(self):
        c.tables = self.tables
        return render('/update.mako')


