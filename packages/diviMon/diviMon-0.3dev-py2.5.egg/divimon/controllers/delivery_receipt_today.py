import logging

from datetime import datetime,timedelta
from divimon.lib.base import *
from delivery_receipt import DeliveryReceiptController

log = logging.getLogger(__name__)



class DeliveryReceiptTodayController(DeliveryReceiptController):

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        now = datetime.now()
        today = datetime(now.year, now.month, now.day, 0, 0)
        tomorrow = today + timedelta(1)
        self.query = self.query.filter_by(type=2).filter(self.table.c.created<tomorrow).filter(self.table.c.created>=today)

        try:
            area = request.params['area']
        except KeyError:
            return
        if area is not None and area != '':
            self.query = self.query.filter_by(area=area)

    def render_list(self):
        if not request.params.has_key('area') or request.params['area'] == '':
            c.list_functions = ('delete')
        return render('/delivery_receipt/list.mako')

    def render_edit(self):
        return render('/delivery_receipt/edit.mako')

    def _save_for_stocks(self, id, params):
        if params.has_key('id'):
            self._save_for_stocks_dc(id, params)
        else:
            self._save_for_stocks_dr(id, params)
        return params

    def _save_custom(self, params):
        if params.has_key('id'):
            params['type'] = 3
            return params
        else:
            params['type'] = 2

        cnt = 0
        args = []
        for item in params.dict_of_lists()['trans_item.item']:
            args.append({
                    'item': item,
                    'qty': params.dict_of_lists()['trans_item.qty'][cnt]
                })
            cnt +=1

        for arg in args:
            inv_item = model.Session.query(model.Inventory).filter_by(item=arg['item'])
            inv_item_qty = inv_item[0].qty
            stocks_out_items = model.Session.query(model.StocksOut)
            stocks_out_items = stocks_out_items.filter_by(item=arg['item']).filter(model.StocksOut.c.confirmed==0)

            if stocks_out_items:
                for stocks_out_item in stocks_out_items:
                    inv_item_qty -= int(stocks_out_item.qty)
                if inv_item_qty < int(arg['qty']):
                    redirect_to('invalid')
        return params


    def _save_for_stocks_dc(self, id, params):
        _stocks_out = StocksOutController()
        params['type'] = 3

        cnt = 0
        args = []
        for item in params.dict_of_lists()['trans_item.item']:
            args.append({
                    'item': item,
                    'received_qty': params.dict_of_lists()['trans_item.received_qty'][cnt]
                })
            cnt +=1

        for arg in args:
            entry = model.Session.query(model.Inventory).filter_by(item=arg['item'])
            entry[0].qty -= int(arg['received_qty'])
            model.Session.save_or_update(entry[0])

            entry2 = model.Session.query(model.StocksOut).filter_by(item=arg['item']).filter_by(dr=id)
            entry2[0].confirmed += int(arg['received_qty'])
            model.Session.save_or_update(entry2[0])
            model.Session.commit()
        return params


    def _save_for_stocks_dr(self, id, params):
        _stocks_out = StocksOutController()
        params['type'] = 2

        cnt = 0
        args = []
        for item in params.dict_of_lists()['trans_item.item']:
            args.append({
                    'item': item,
                    'qty': params.dict_of_lists()['trans_item.qty'][cnt]
                })
            cnt +=1

        for arg in args:
            stocks_out_params = dict(item=arg['item'],area=params['area'],qty=arg['qty'],dr=id)
            entry2 = _stocks_out._save(None, stocks_out_params)

        return params

    def invalid(self):
        return 'Invalid!'

    def save(self):
        self._dbg('save')
        try:
            id = request.params['id']
        except KeyError:
            id = None
        entry = self._save(id, request.params)
        self._save_for_stocks(entry.id, request.params)
        self._dbg('save', entry.id)

        if int(entry.pay_type) == 3:
            redirect_to('/cheques/add?')
        else:
            redirect_to('list')
        return 'Saved'

    def add(self):
        self._dbg('add')
        self._add()
        c.children['trans_item']['columns'] = ('item', 'qty', 'price')
        return render('/delivery_receipt/add.mako')

    def edit(self, id):
        self._dbg('edit', request.params)
        self._details(request.params['id'])
        c.children['trans_item']['columns'] = ('item', 'qty', 'price', 'received_qty')
        return render('/delivery_receipt/edit.mako')

    def render_add_child(self):
        return render('/delivery_receipt/add_child.mako')

    def render_edit_child(self):
        return render('/delivery_receipt/edit_child.mako')



