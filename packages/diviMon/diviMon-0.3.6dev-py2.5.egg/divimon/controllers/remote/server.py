import logging

from base import *
from base import Remote

log = logging.getLogger(__name__)

class ServerController(Remote):

    def _get_child(self, entry, child, tbl):
        children = []
        c = Child(tbl)
        for row in getattr(entry, child):
            children.append(c._entry2dict(row))
        return children

    def _get_entries_for_update(self, client_latest):
        entries = model.list(self.tbl)
        if client_latest is not None:
            entries = entries.filter(self.tbl.c.created>client_latest)
        return entries

    def _get_latest(self):
        entries = model.list(self.tbl).order_by(self.tbl.c.created.desc())
        try:
            return entries[0].created
        except IndexError:
            return None

    def get_latest(self):
        self.tbl = getattr(model, request.params['table'])
        latest = self._get_latest()
        return pickle.dumps(latest)

    def commit(self):
        '''Accept commits from the client
        '''
        self.tbl = getattr(model, request.params['table'])
        data = pickle.loads(str(request.params['data']))
        #entry = self.tbl(**data)
        entry = self._save_entry(data)
        model.Session.save(entry)
        model.Session.commit()
        return True

    def update(self):
        '''Send updates to the client
        '''
        latest = str(request.params['latest'])
        self.tbl = getattr(model, request.params['table'])
        client_latest = pickle.loads(latest)
        entries = []
        for entry in self._get_entries_for_update(client_latest):
            entry = self._entry2dict(entry)
            entries.append(entry)
        return pickle.dumps(entries)

    def index(self):
        c.tables = self.tables
        return render('/update.mako')


