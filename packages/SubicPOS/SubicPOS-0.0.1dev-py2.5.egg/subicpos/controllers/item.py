import logging

from subicpos.lib.base import *
from subicpos import model

log = logging.getLogger(__name__)

class ItemController(ListController):
    table = model.Item
    parent = dict(
            classification = dict(
                    table = model.Classification,
                    column = ('name'),
                )
        )



# Add invenotry item with quantity = 0

