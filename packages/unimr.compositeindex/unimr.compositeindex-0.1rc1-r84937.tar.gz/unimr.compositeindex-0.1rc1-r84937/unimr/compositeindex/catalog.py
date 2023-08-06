import logging

from Acquisition import aq_parent

from Products.ZCatalog.Catalog import Catalog

from CompositeIndex import compositeSearchArgumentsMap

from wrapper import wrap_method, call

from config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)


def search(self, request, sort_index=None, reverse=0, limit=None, merge=1):

    compositeSearchArgumentsMap(self,request)
    
    return call(self,'search',request, sort_index=sort_index, reverse=reverse, limit=limit, merge=merge)


def patch(scope,original,replacement):
    wrap_method(scope, original, replacement)

