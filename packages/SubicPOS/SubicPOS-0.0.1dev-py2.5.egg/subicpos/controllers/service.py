import logging

from subicpos.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class ServiceController(TransactionController):

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=2)

    def render_edit(self):
        return render('/service/edit.mako')

    def _save_custom(self, params):
        # insert branch here
        if g.branch_id > 0:
            params['branch'] = g.branch_id
        params['type'] = 2
	#No Point Of Sale here 
        return params

#'Fuel', 'Service', 'Treats', 'Delivered', 'Returns', 'Waste', 'Consumed',