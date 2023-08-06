from zope.interface import Interface

class IFacetBuilder(Interface):
    """Tool"""
    
    def facet_data(facets):
        """ See adapters.FacetBuilder
        """
    
    def add_weight_data(facetobjects):
        """ See adapters.FacetBuilder
        """
        
    def add_brains():
        """ See adapters.FacetBuilder
        """
        
    def facet_query(**kw):
        """ Return a dict with info about a selection of this facet. kw is the index to search for, ie Type='Document'
        """
        
class IFacetBaseView(Interface):
    """ Base view for anything regular BrowserView class that handles facets.
        Populates the request with facet brains and search data.
    """