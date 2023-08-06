from plone.sequencebatch.batch import Batch

from AccessControl import allow_class
from AccessControl import allow_module

allow_module('plone.sequencebatch')
allow_class(Batch)
