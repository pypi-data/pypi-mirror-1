import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class ItemController(ListController):
    table = model.Item

    def _save(self, id=None, params=request.params):
        all_args = self._save_custom(params)
        entry_args = {}
        child_args = {}
        # Sorting of fields for parent and children
        for k in all_args.keys():
            if k in self.table.c.keys():
                entry_args[k] = all_args[k]
            else:
                child_args[k] = all_args.dict_of_lists()[k]
        entry = self._save_entry(id, entry_args)
        self._dbg('_save', '%s Successfully saved' % entry)
        self._save_children(entry, **child_args)
        self._save_properties(entry, **child_args)
        model.Session.save_or_update(entry)
        model.Session.commit()
        inventory = model.Inventory(
                item = entry.id,
                qty = 0,
            )
        model.Session.save_or_update(inventory)
        model.Session.commit()
        return entry

