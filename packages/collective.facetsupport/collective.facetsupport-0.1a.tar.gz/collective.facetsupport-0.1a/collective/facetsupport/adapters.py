from collective.facetsupport.interfaces import IFacetBuilder
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from Products.CMFPlone.utils import safe_unicode

import logging
logger = logging.getLogger('collective.facetsupport')

class FacetBuilder(object):
    implements(IFacetBuilder)
    
    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST
        self.catalog = getToolByName(context,'portal_catalog')
        self.catalog_indexes = self.catalog.indexes()
        self.normalizer = getUtility(IIDNormalizer)

        #Check context for usable request method. Plone root has a Python FS script called queryCatalog which we don't want!
        if self.context.meta_type != 'Plone Site' and shasattr(context, 'queryCatalog'):
            self.query_method = context.queryCatalog
        else:
            #We might want to update this
            self.query_method = context.getFolderContents
    
    def _construct_facet_query(self):
        """ Construct a catalog query from a request.
            Only fetches things from the request object if it exists as a catalog index.
            Most of the time, you'' want to fetch this data from request.facetsupport['query']
        """
        reqkeys = self.request.keys()
        indexes = self.catalog_indexes
        query = {}
        for index in indexes:
            if index in reqkeys:
                query[index] = self.request[index]
        
        return query
    
    def normalize_css(self, text):
        """ Fix css classes or ids so they're okay with i18n chars.
        """
        if type(text) != unicode:
            text = text.decode('utf-8')
        return self.normalizer.normalize(text)


    def facet_data(self, facets):
        """ facets are facets to use. This equals catalog indexes.
            Layout of the request.facetsupport property
            
            facet: list of FacetData objects. See FacetData below.
            
            query: The query to pass along to get this result.
            
            SearchableText: The SearchableText query.
            
            This should in most cases be set as the request.facetsupport property
            
            Only executes if facetsupport doesn't exist in the request, otherwise it returns None
        """
        
        context = self.context
        request = self.request
        
        fs  = {}
        
        fs['query'] = self._construct_facet_query()
        #fs['brains'] = self.query_method(**fs['query'])
        fs['facets'] = []

        catalog_indexes = self.catalog.indexes()
        for facet in facets:
            if facet in catalog_indexes:
                val = list(self.catalog.uniqueValuesFor(facet))
                val.sort()
            else:
                facet = u'Index not found: %s' % facet 
                val = []
            #FIXME: This should handle UIDs that are relations too
            obj = FacetData(facet)
            obj.terms = val
            fs['facets'].append(obj)
            
        #SearchableText is a special case - it should always be there
        search = getattr(request,'SearchableText',None)
        if search:
            fs['SearchableText'] = search
        
        return fs

    def add_weight_data(self, facetobjects):
        """ Updates facetobjects with weight
        """
        query = self.request.facetsupport['query']
        for obj in facetobjects:
            obj.weight = self._per_facet_weight(obj.facet, obj.terms, query)


    def _per_facet_weight(self, facet, terms, query):
        """ Returns a dict with layout {item:weight,...}
            query is the base query that's active right now.
        """
        result = {}
        for item in terms:
            thisq = query.copy()
            thisq.update({facet:item})
            result[item] = len( self.query_method(thisq) )
        return result

    def add_brains(self):
        """ Add brains to the existing request """
        fs = self.request.get('facetsupport',None)
        if fs is None:
            return None
        fs['brains'] = self.query_method(**fs['query'])
        return True

    def facet_query(self, **kw):
        """ Returns a dict with the query updated with this item selected.
            Used for constructing links or calculating weight of a facet.
        """
        if kw is None or not hasattr(self.request, 'facetsupport'):
            return None

        query = self.request.facetsupport['query'].copy()

        for k in kw:
            #TODO: Should we allow anything here?
            if k in self.catalog_indexes:
                #This will replace any existing keys in the dict, which is the point
                query[k] = kw[k]
        return query 

class FacetData(object):
    """ This object is used to fetch results for each facet.
        facet: The name of this facet. Must be the same as the catalog index
        terms: The different terms in this facet
        weight: weight for each term
        
    """
    facet = ''
    terms = []
    weight = {}
    #FIXME: Implement - Some facets can have uids as terms. In that case they need to be handled in a special way.
    reference_terms = False
    
    def __init__(self, facet):
        setattr(self, 'facet', facet)

    @property
    def title(self):
        """Just to make skinning a bit easier :) """
        return self.facet