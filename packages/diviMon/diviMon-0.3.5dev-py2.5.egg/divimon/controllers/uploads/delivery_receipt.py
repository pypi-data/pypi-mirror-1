from base import *

log = logging.getLogger(__name__)


class DeliveryReceiptController(UploadController):
    table = model.Transaction
    columns = ['area', 'customer', 'agent', 'pay_type', 'item', 'qty', 'price', 'received_qty', ]
    permanent_store = '/tmp/divimon-upload/'
    permanent_filename = os.path.join(permanent_store, 'dr.csv')
    last_row = {}
    last_trans = None
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
            type = dict(
                    table = model.TransType,
                    column = 'name',
                ),
            customer = dict(
                    table = model.Customer,
                    column = 'name',
                ),
            agent = dict(
                    table = model.Agent,
                    column = 'name',
                ),
            pay_type = dict(
                    table = model.PayType,
                    column = 'name',
                ),
            item = dict(
                    table = model.Item,
                    column = 'name',
                ),
        )

    def _create_transaction(self, **kw):
        '''Create a new transaction entry
        '''
        for k,v in kw.iteritems():
            if k not in self.parent:
                continue
            if v == '':
                kw[k] = None
            else:
                kw[k] = self._get_id_from_parent(k, v)
        kw['type'] = 2
        trans = model.Transaction(**kw)
        return trans

    def _create_trans_item(self, trans, **kw):
        '''Create a new trans_item entry
        '''
        for k,v in kw.iteritems():
            if k not in self.parent:
                continue
            if v == '':
                kw[k] = None
            else:
                kw[k] = self._get_id_from_parent(k, v)
        trans_item = model.TransItem(**kw)
        return trans_item

    def _get_id_from_parent(self, col, val):
        parent = self.parent[col]
        f_kw = {parent['column']: val}
        entries = model.list(parent['table']).filter_by(**f_kw)
        try:
            return entries[0].id
        except IndexError:
            return None

    def _save_entry(self, **all):
        kw_p = {}
        kw_c = {}
        for k,v in all.iteritems():
            if k in model.Transaction.c.keys():
                kw_p[k] = v
            elif k in model.TransItem.c.keys():
                kw_c[k] = v
        if self.last_trans is None:
            return self._save_entry_new(kw_p, kw_c)
        else:
            return self._save_entry_old(kw_c)

    def _save_entry_new(self, kw_p, kw_c):
        '''Create a new transaction, a new trans_item
        and add the trans_item to the transaction.
        Also, add the price of the trans_item to the total price.
        '''
        trans = self._create_transaction(**kw_p) 
        trans_item = self._create_trans_item(trans, **kw_c) 
        trans.total_price = int(trans_item.price)
        trans.trans_item.append(trans_item)
        model.Session.save(trans)
        model.Session.commit()
        self.last_trans = trans
        return 'Saved new entry'

    def _save_entry_old(self, kw):
        '''Create a new trans_item
        and add the trans_item to the last transaction.
        Also, add the price of the trans_item to the total price.
        '''
        trans = self.last_trans
        trans_item = self._create_trans_item(trans, **kw) 
        trans.total_price += int(trans_item.price)
        trans.trans_item.append(trans_item)
        model.Session.update(trans)
        model.Session.commit()
        return 'Saved new entry'

    def _save_row(self, row):
        #print 'Saving %s' % row
        s_entry = ''
        kw = {}
        for cnt in range(0, len(c.columns)):
            #print c.columns[cnt], row[cnt]
            column = str(c.columns[cnt])
            value = unicode(row[cnt])
            kw[column] = value
            if cnt < 4 and value != '':
                self.last_trans = None
            #if value == '':
            #    kw[column] = self.last_row[column]
            #else:
            #    kw[column] = value
            #    if cnt < 5:
            #        self.last_row[column] = kw[column]
            s_entry += '<td>%s</td>\n' % (kw[column])
        status = self._save_entry(**kw)
        return '<tr>%s<th>%s</th></tr>' % (s_entry, status)

