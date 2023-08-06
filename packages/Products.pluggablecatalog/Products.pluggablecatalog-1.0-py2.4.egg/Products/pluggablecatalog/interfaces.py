from zope import interface


class IQueryDefaults(interface.Interface):
    """A component that adds default query parameters."""
    
    def __call__(context, request, args):
       """Returns a dictionary of query arguments which are used by
       the catalog in 'searchResults'.

         - `context` is the context in which the request was made.

         - `request` is the REQUEST as passed to
           `CatalogTool.searchResults`.

         - `args` is a dictionary that holds all search request info.
           It contains arguments from request and kwargs passed to
           `CatalogTool.searchResults`.
       """

class IQueryOverrides(interface.Interface):
    """A component that overrides query parameters."""

    def __call__(context, request, args):
        """See IQueryDefaults.__call__"""
