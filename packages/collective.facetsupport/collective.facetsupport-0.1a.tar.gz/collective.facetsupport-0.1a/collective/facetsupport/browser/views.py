from Products.Five.browser import BrowserView
from zope.interface import implements

from collective.facetsupport.interfaces import IFacetBuilder, IFacetBaseView
from collective.facetsupport.config import DEFAULT_INDEXES
from ZTUtils.Zope import make_query
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('collective.facetsupport')

class FacetBaseView(BrowserView):
    """ Base view for anything regular BrowserView class that handles facets.
        Populates the request with facet brains and search data.
    """
    implements(IFacetBaseView)
    
    def __init__(self, context, request):
        super(FacetBaseView, self).__init__(context, request)
        fb = IFacetBuilder(context)
        #FIXME: This should be configurable in the control panel, and easily overridden in templates.
        #If it's added here that won't be possible
        self.use_indexes = DEFAULT_INDEXES
        
        #The adapter returns None if no update of the request is needed.
        data = fb.facet_data(self.use_indexes)
        if data is not None:
            request.facetsupport = data
        
        fb.add_weight_data(request.facetsupport['facets'])
        
        self.fb = fb
        self.catalog = getToolByName(context,'portal_catalog')

    @property
    def facets(self):
        return self.request.facetsupport['facets']
    
    @property
    def query(self):
        return self.request.facetsupport['query']

    def normalize_css(self, text):
        return self.fb.normalize_css(text)

    def query_link(self, remove=None):
        """ A link for a query. Remove keyword in remove.
        """
        query = self.query.copy()
        if remove in query:
            del query[remove]
        return make_query(query)

    #FIXME: This should be a part of the request instead. Really... :)
    #FIXME: Template name could be a part of the request too
    def link_for_term(self, facet, term):
        query = self.fb.facet_query(**{facet:term})
        return "?%s" % make_query(query)

class InlineFacetResultView(FacetBaseView):
    """ Inline view facet results.
    """

class InlineFacetMenuView(FacetBaseView):
    """ Inline view for facet menu.
    """
    

