"""The application's Globals object"""
from pylons import config

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        self.base_url = ''
        self.debug = True
        self.show_pages = 10
        self.function_delete = 'Delete'
        self.session = {}
        self.permissions = {
                1 : {
                        '*': ('*', ),
                    },
                2 : dict(
                        delivery_receipt = ('*', ),
                    ),
                3 : dict(
                        inventory = ('list', 'add', ),
                    ),
            }

    def new_session(self, id, user=None):
        class Session(object):
            def __init__(self, id, user):
                from datetime import datetime
                self.id = id
                self.login = datetime.now()
                self.user = user
        self.session[id] = Session(id, user)
        return self.session[id]

