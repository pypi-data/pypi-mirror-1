import logging

from divimon.lib.base import *
import os

log = logging.getLogger(__name__)

class ItemController(BaseController):
    table = model.Item
    columns = ['name', 'code', 'description', 'unit', 'price', 'qty']
    permanent_store = '/tmp/divimon-item/'
    permanent_filename = os.path.join(permanent_store, 'item.csv')

    def _save(self):
        import csv
        c.columns = request.params.dict_of_lists()['column']
        yield '<table>'
        yield '<thead>'
        for col in c.columns:
            yield '<th>%s</th>' % col
        yield '<th>%s</th>' % ''
        yield '</thead>'
        yield '<tbody>'
        for row in csv.reader(open(self.permanent_filename)):
            yield self._save_row(row)
        yield '</tbody>'
        yield '</table>'

    def _save_entry(self, **all):
        kw_item = {}
        kw_inv = {}
        for k,v in all.iteritems():
            if k in model.Item.c.keys():
                kw_item[k] = v
            elif k in model.Inventory.c.keys():
                kw_inv[k] = v
        item_entry = model.Item(**kw_item)
        model.Session.save(item_entry)
        model.Session.commit()
        kw_inv['item'] = item_entry.id
        inv_entry = model.Inventory(**kw_inv)
        model.Session.save(inv_entry)
        model.Session.commit()

    def _save_row(self, row):
        from time import sleep
        from sqlalchemy.exceptions import IntegrityError
        print 'Saving %s' % row
        s_entry = ''
        kw = {}
        for cnt in range(0, len(c.columns)):
            s_entry += '<td>%s</td>\n' % (row[cnt])
            print c.columns[cnt], row[cnt]
            kw[str(c.columns[cnt])] = row[cnt]
        try:
            self._save_entry(**kw)
        except IntegrityError, e:
            err = str(e)
            if err.find('not unique') != -1:
                err = '(DUPLICATE code)'
            return '<tr>%s<th>Failed <small>%s</small></th></tr>' % (s_entry, err)
        return '<tr>%s<th>Saved</th></tr>' % s_entry

    def _upload_csv(self):
        import csv
        rows = []
        for row in csv.reader(open(self.permanent_filename)):
            rows.append(row)
        c.rows = rows
        c.columns = self.columns
        return render('/upload_confirm.mako')

    def save(self):
        return self._save()

    def upload(self):
        import shutil
        try:
            os.mkdir(self.permanent_store)
        except OSError:
            pass
        myfile = request.POST['file']
        self.permanent_filename = os.path.join(self.permanent_store,
            myfile.filename.lstrip(os.sep))
        permanent_file = open(self.permanent_filename, 'w')
        shutil.copyfileobj(myfile.file, permanent_file)
        #myfile.file.close()
        permanent_file.close()
        return self._upload_csv()
        return 'Successfully uploaded: %s, content: %s' % \
            (myfile.filename, myfile.value)

    def index(self):
        return render('/upload.mako')

