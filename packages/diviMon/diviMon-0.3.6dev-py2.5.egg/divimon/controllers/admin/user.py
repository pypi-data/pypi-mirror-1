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
            'password',
            'details',
        ])


    def invalid(self):
        return 'Invalid!'

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


