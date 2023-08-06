import Acquisition
from Products.CMFCore.utils import getToolByName
from Products.pluggablecatalog import tool

import logging 
logger = logging.getLogger(__name__)

def replaceCatalog(context):
    if context.readDataFile('pluggablecatalog-default.txt') is None:
        return
    site = context.getSite()
    catalog = getToolByName(site, 'portal_catalog')
    if not isinstance(Acquisition.aq_base(catalog), tool.CatalogTool):
        catalog.__class__ = tool.CatalogTool
