from base import *

log = logging.getLogger(__name__)


class ItemController(UploadController):
    table = model.Item
    columns = ['name', 'description', 'unit', 'price', 'purchase_price', 'qty']
    permanent_store = '/tmp/divimon-upload/'
    permanent_filename = os.path.join(permanent_store, 'item.csv')

    def _check_existing(self, name):
        entries = model.list(model.Item).filter_by(name=name)
        if entries.count() > 0:
            return entries
        else:
            return None

    def _save_entry(self, **all):
        kw_item = {}
        kw_inv = {}
        for k,v in all.iteritems():
            if k in model.Item.c.keys():
                kw_item[k] = v
            elif k in model.Inventory.c.keys():
                kw_inv[k] = v
        existing = self._check_existing(all['name'])
        #response.content_type = 'text/csv'
        #print response.__dict__
        if existing is None:
            return self._save_entry_new(kw_item, kw_inv)
        else:
            return self._save_entry_old(existing[0], kw_item, kw_inv)

    def _save_entry_new(self, kw_item, kw_inv):
        item_entry = model.Item(**kw_item)
        model.Session.save(item_entry)
        try:
            model.Session.commit()
            #print 'Successfully saved'
        except ValueError, e:
            model.Session.rollback()
            model.Session.clear()
            err = str(e)
            err = 'Invalid price: %s' % (err.split(' ')[-1])
            return 'Failed <small>(%s)</small>' % (err)
        except IntegrityError, e:
            model.Session.rollback()
            model.Session.clear()
            #print 'Failed'
            err = str(e)
            if err.find('not unique') != -1:
                err = 'DUPLICATE name'
            return 'Failed <small>(%s)</small>' % (err)
        kw_inv['item'] = item_entry.id
        inv_entry = model.Inventory(**kw_inv)
        model.Session.save(inv_entry)
        try:
            model.Session.commit()
        except ValueError, e:
            model.Session.rollback()
            model.Session.clear()
            model.Session.delete(item_entry)
            model.Session.commit()
            err = str(e)
            err = 'Invalid qty: %s' % (err.split(' ')[-1])
            return 'Failed <small>(%s)</small>' % (err)
        return 'Saved new entry'

    def _save_entry_old(self, item_entry, kw_item, kw_inv):
        entries = model.list(model.Inventory).filter_by(item=item_entry.id)
        inv_entry = entries[0]
        inv_entry.qty += int(kw_inv['qty'])
        model.Session.save_or_update(inv_entry)
        model.Session.commit()
        return 'Added to inventory'

    def _save_row(self, row):
        #print 'Saving %s' % row
        s_entry = ''
        kw = {}
        for cnt in range(0, len(c.columns)):
            s_entry += '<td>%s</td>\n' % (row[cnt])
            #print c.columns[cnt], row[cnt]
            kw[str(c.columns[cnt])] = unicode(row[cnt])
        status = self._save_entry(**kw)
        return '<tr>%s<th>%s</th></tr>' % (s_entry, status)

    def save(self):
        page = self._save()
        return redirect_to('%s/inventory/' % g.base_url)

