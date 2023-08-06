import logging

from subicpos.lib.base import *
from subicpos import model

log = logging.getLogger(__name__)

class InventoryController(ListController):
    table = model.Inventory
    parent = dict(
            branch = dict(
                    table = model.Branch,
                    column = ('name'),
                ),
            item = dict(
                    table = model.Item,
                    column = ('code'),
                )
        )