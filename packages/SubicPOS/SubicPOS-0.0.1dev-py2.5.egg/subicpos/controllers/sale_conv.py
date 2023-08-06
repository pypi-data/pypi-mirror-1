import logging

from subicpos.lib.base import *
from sale import SaleController

log = logging.getLogger(__name__)

class SaleConvController(SaleController):

    def _init_custom(self):
        c.title = 'Convenience Store Sale'

    def render_edit(self):
        return render('/sale/edit.mako')

