import logging

from subicpos.lib.base import *
from subicpos import model

log = logging.getLogger(__name__)

class ClassificationController(ListController):
    table = model.Classification

