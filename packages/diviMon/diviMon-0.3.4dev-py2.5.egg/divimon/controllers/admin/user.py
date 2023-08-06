import logging
import crypt
from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class UserController(ListController):
    table = model.User
    parent = dict(
        role = dict(
            table=model.Role,
            column='name',
        ),
    )
    columns_hidden = set([
            'id',
        ])


    def invalid(self):
        return 'Invalid!'

    def _save_custom(self, params):
        print params['password']
        if params['password'] != params['password2']:
            redirect_to('invalid')
        params['role'] = 1
        params['password'] = crypt.crypt(str(params['password']),"AA")
        print crypt.crypt(str(params['password']),"AA")
        return params

    def edit(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        return render('/member/edit.mako')

    def add(self):
        self._dbg('add')
        self._add()
        return render('/member/new.mako')

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


