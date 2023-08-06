import traceback
from StringIO import StringIO

from zope import component
import AccessControl
import Acquisition
import Globals
from AccessControl import Permissions
from Products.CMFPlone import CatalogTool as base

from Products.pluggablecatalog import interfaces

import logging
logger = logging.getLogger('pluggablecatalog')

class CatalogTool(base.CatalogTool):

    meta_type = 'Pluggable Plone Catalog Tool'

    security = AccessControl.ClassSecurityInfo()
    
    # permission is inherited
    def searchResults(self, REQUEST=None, **kw):
        """Wraps CMFPlone's CatalogTool to add default parameters
        collected from IQueryDefaults utilities.

        Install the catalog:
        
          >>> from StringIO import StringIO
          >>> from Products.pluggablecatalog.Extensions.install \\
          ...     import _replaceCatalog
          >>> self.loginAsPortalOwner()
          >>> _replaceCatalog(self.portal, StringIO())
          >>> self.login()

          >>> from Products.pluggablecatalog.tool import CatalogTool
          >>> catalog = self.portal.portal_catalog
          >>> isinstance(catalog, CatalogTool)
          True

        We create two documents and make sure they're indexed:

          >>> before = len(catalog())
          >>> self.folder.invokeFactory('Document', 'doc1')
          'doc1'
          >>> self.folder.invokeFactory('Document', 'doc2')
          'doc2'
          >>> doc1, doc2 = self.folder.doc1, self.folder.doc2
          >>> doc1.setTitle('First Document')
          >>> doc2.setTitle('Second Document')
          >>> doc1.reindexObject(); doc2.reindexObject()
          >>> len(catalog()) - before
          2

        Let's now add a rather stupid IQueryDefaults utility that
        restricts searches by default to objects with the Title 'First
        Document':

          >>> from zope import component
          >>> from zope import interface
          >>> from Products.pluggablecatalog.interfaces import IQueryDefaults
          >>> def myDefaults(context, request, args):
          ...     return {'Title': 'First Document'}
          >>> interface.directlyProvides(myDefaults, IQueryDefaults)
          >>> component.provideUtility(myDefaults)

        With this utility in place, we should only retrieve doc1 now,
        unless we explicitly provide a 'Title' query parameter:

          >>> len(catalog())
          1
          >>> catalog()[0].getObject().aq_base is doc1.aq_base
          True

          >>> len(catalog(Title='Second Document'))
          1
          >>> (catalog(Title='Second Document')[0].getObject().aq_base is
          ...  doc2.aq_base)
          True

        There's also an IQueryOverrides utility.  With this component,
        we can override existing query arguments:

          >>> from Products.pluggablecatalog.interfaces import IQueryOverrides
          >>> def myOverrides(context, request, args):
          ...     if args.get('Title') == 'Second Document':
          ...         return {'Title': 'First Document'}
          ...     else:
          ...         return {}
          >>> interface.directlyProvides(myOverrides, IQueryOverrides)
          >>> component.provideUtility(myOverrides)

        With this component registered, we can expect to get the first
        document even if we specify the second document's title:
        
          >>> len(catalog())
          1
          >>> catalog()[0].getObject().aq_base is doc1.aq_base
          True

          >>> len(catalog(Title='Second Document'))
          1
          >>> (catalog(Title='Second Document')[0].getObject().aq_base is
          ...  doc1.aq_base)
          True

        Keyword arguments that are passed to the catalog's
        searchResults will be passed to registered IQueryDefaults and
        IQueryOverrides utilties as part of the `args` argument.

          >>> def mySecondDefaults(context, request, args):
          ...     special = args.get('somespecial')
          ...     if special:
          ...         print "Received args['somespecial'] = %r" % (special,)
          ...     return {}
          >>> interface.directlyProvides(mySecondDefaults, IQueryDefaults)
          >>> component.provideUtility(mySecondDefaults)
          >>> results = catalog(somespecial='kwarg')
          Received args['somespecial'] = 'kwarg'

        Cleanup.  I couldn't figure out the equivalent for the
        following call for Zope < 2.10.  However, our
        `mySecondDefaults` utility doesn't really do anything, so
        we'll keep it registered.

          >>> #component.globalSiteManager.unregisterUtility(mySecondDefaults)
        """
        request = REQUEST
        if request is None:
            request = getattr(self, 'REQUEST', None)

        # BBB
        if not hasattr(request, 'form'):
            out = StringIO()
            traceback.print_stack(file=out)
            logger.error("REQUEST argument is not a real request:\n%s"
                         % out.getvalue())
            return base.CatalogTool.searchResults(self, request, **kw)

        args = dict(request.form)
        args.update(kw)
        defaults = dict()
        for name, util in component.getUtilitiesFor(interfaces.IQueryDefaults):
            defaults.update(util(self, request, args))
        
        for key, value in defaults.items():
            kw.setdefault(key, value)

        for name, util in component.getUtilitiesFor(interfaces.IQueryOverrides):
            kw.update(util(self, request, args))

        return base.CatalogTool.searchResults(self, REQUEST, **kw)

    __call__ = searchResults

CatalogTool.__doc__ = base.CatalogTool.__doc__
Globals.InitializeClass(CatalogTool)
