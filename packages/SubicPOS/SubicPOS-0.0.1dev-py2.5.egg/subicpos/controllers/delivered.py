import logging

from subicpos.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class DeliveredController(TransactionController):

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=4)

    def render_edit(self):
        return render('/delivered/edit.mako')

    def _save_custom(self, params):
        # insert branch here
        if g.branch_id > 0:
            params['branch'] = g.branch_id
        params['type'] = 4
	params['in_out'] = 'in'
	entry = model.Session.query(model.Inventory).filter_by(branch=params['branch']).filter_by(item=params['trans_item.item'])
	entry[0].qty += int(params['trans_item.qty'])
        
        return params

#'Fuel', 'Service', 'Treats', 'Delivered', 'Returns', 'Waste', 'Consumed',