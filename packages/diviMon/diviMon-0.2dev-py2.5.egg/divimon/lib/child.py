import divimon.model as model

class ChildList(object):
    def __init__(self, parent, field, details):
        self.parent = parent
        self.field = field
        self.details = details
        self.table = details['table']
        self.columns = details['columns']
        self.children = getattr(parent, field)

    def clean_kws(self, **okw):
        nkw = {}
        for k,v in okw.iteritems():
            key = k.replace('%s.' % self.field, '')
            nkw[key] = v
        return nkw

    def save(self, id=None, **kw):
        if id is None:
            entry = self.table(**kw)
            self.children.append(entry)
            model.Session.save_or_update(self.parent)
        else:
            entry = model.get(self.table, id)
            for k,v in kw.iteritems():
                setattr(entry, k, v)
            model.Session.save_or_update(entry)
        return

    def multi_save(self, **kw):
        kw = self.clean_kws(**kw)
        args = {}
        for k in kw.keys():
            if k in self.columns:
                cnt = 0
                for v in kw[k]:
                    if cnt not in args.keys():
                        args[cnt] = {}
                    args[cnt][k] = v
                    cnt += 1
            elif k.find(self.field) > -1:
                cnt = 0
                for v in kw[k]:
                    if cnt not in args.keys():
                        args[cnt] = {}
                    args[cnt]['id'] = v
                    cnt += 1
        for arg in args.values():
            self.save(**arg)
        return


