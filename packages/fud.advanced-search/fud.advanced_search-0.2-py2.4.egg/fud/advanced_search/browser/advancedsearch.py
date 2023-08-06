from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.AdvancedQuery import And , Eq, In, Or
from Products.CMFPlone.browser.navtree import getNavigationRoot



from fud.advanced_search import advanced_searchMessageFactory as _


class IAdvancedsearchView(Interface):
    """
    Fudresult view interface
    """

    def getSearchItems():
        """ test method"""

    def getCreators():
        """
        returns all creators who have a full name specified
        """
    def isSorterTitle():
        """retturns true if the sorter is a title"""
    def isSorterTitleDesc():
        """retturns true if the sorter is a Title descending"""
    def isSorterCreator():
        """retturns true if the sorter is a Creator"""
    def isSorterCreatorDesc():
        """retturns true if the sorter is a Creator descending"""
    def isSorterDate():
        """retturns true if the sorter is a Date"""
    def isSorterDateDesc():
        """retturns true if the sorter is a Date descending"""
    def __createTextQuery():
        """
        returns the query for the text search
        """
    def __listEqTuple():
        """
        Compare a list's content with a tuple's content
        """
    def __listHasElemFromTuple():
        """Compare a list's content with a tuple's content"""


class AdvancedsearchView(BrowserView):
    """
    Fudresult browser view
    """

    implements(IAdvancedsearchView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def isSorterTitle(self):
        """retturns true if the sorter is a title"""
        return self.request.SortBy=='sortable_title'

    def isSorterTitleDesc(self):
        """retturns true if the sorter is a Title descending"""
        return self.request.SortBy=='sortable_title desc'

    def isSorterCreator(self):
        """retturns true if the sorter is a Creator"""
        return self.request.SortBy=='Savedby'

    def isSorterCreatorDesc(self):
        """retturns true if the sorter is a Creator descending"""
        return self.request.SortBy=='Savedby desc'

    def isSorterDate(self):
        """retturns true if the sorter is a Date"""
        return self.request.SortBy=='modified'

    def isSorterDateDesc(self):
        """retturns true if the sorter is a Date descending"""
        return self.request.SortBy=='modified desc'

    def getCreators(self):
        """
        returns the query for the text search
        """
        creators = []
        candidates = self.portal_catalog.uniqueValuesFor('listCreators')
        for can in candidates:
            #check whether it has a last name
            if self.portal_membership.getMemberInfo(can)['fullname']:
                creators.append(can)
        return creators
    
    def getSearchItems(self):
        """ test method"""
        context = self.context
        request = self.request
        allowed_types = ['Quellentext','Fachartikel']
        #batch start specification
        
        
        
#        import pdb; pdb.set_trace()
#        Get the physical path to an object
#        The getPhysicalPath() method returns a list contained the ids of the object's containment heirarchy :
        context_path = '/'.join(context.getPhysicalPath())
        compositeQuery = And() #a query built out of many queries
        zcatQuery={}#initialize the ZCatalog styled query

        if request.DocType:
            compositeQuery.addSubquery(Eq('portal_type',request.DocType))
        else:
            doctypeQuery=Or()
            for at in allowed_types:
                doctypeQuery.addSubquery(Eq('portal_type',at))
            compositeQuery.addSubquery(doctypeQuery)

        textQuery=self.__createTextQuery()

        if textQuery:
            zcatQuery['SearchableText']=textQuery
            subQuery = self.portal_catalog.makeAdvancedQuery(zcatQuery)
            compositeQuery.addSubquery(subQuery)

        if request.subjects:
            if isinstance(request.subjects, str):
                subjects = [request.subjects]
            else:
                subjects = request.subjects

            for subj in subjects:
                compositeQuery.addSubquery(Eq('Subject',subj))

                

        if request.creators:
            if request.coop:
                creatorsQuery=And()
            else:
                creatorsQuery=Or()
            #creators were chosen in the creator field
            if isinstance(request.creators, str):
                creators=[request.creators]
            else:
                creators=request.creators
            for rc in creators:
                creatorsQuery.addSubquery(Eq('listCreators',rc))
            compositeQuery.addSubquery(creatorsQuery)
            
        if(request.notcreators):
            if isinstance(request.notcreators, str):
                creators=[request.notcreators]
            else:
                creators=request.notcreators
            for rc in creators:
                compositeQuery.addSubquery(~ Eq('listCreators',rc))


        #import pdb; pdb.set_trace();
        listSortKey=''
        listSortDesc=False
        if request.SortBy:
            #make a list out of the user input for SortBy
            sortCriteria = request.SortBy.split() 
            #validate 1st input
#            if sortCriteria[0]=='Creator'
            if sortCriteria[0] in ('Savedby'):
                listSortKey=sortCriteria[0];
                brains = self.portal_catalog.evalAdvancedQuery(compositeQuery)
                if len(sortCriteria)>1:
                    #validate 2nd input
                    if sortCriteria[1]=='desc':
                         listSortDesc=True
            elif sortCriteria[0] in ('modified','sortable_title'):
                if len(sortCriteria)>1:
                    if sortCriteria[1]=='desc':
                        brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0],sortCriteria[1]),))
                else:
                    brains = self.portal_catalog.evalAdvancedQuery(compositeQuery,((sortCriteria[0]),))
        else:
            #Ignore sorting
            brains = self.portal_catalog.evalAdvancedQuery(compositeQuery)

        items = []
        #rough filtering.
        #Every item, which has in its creators list a name from the requested creators
        #will be returned
        for brain in brains:
            if brain.getPath() <> context_path:
                savedby = self.portal_membership.getMemberInfo(brain.Creator)['fullname']
                creators=[]
                for creator in brain.listCreators:
                    creators.append(self.portal_membership.getMemberInfo(creator)['fullname'])
                items.append({'Title':brain.Title,
                              'Type':brain.Type,
                              'url':brain.getURL(),
                              'created':brain.created,
                              'modified':brain.modified,
                              'Creators':creators,
                              'Savedby':savedby,
                              'subjects':brain.Subject,
                              'fundort':brain.fundort,
                              'druckort':brain.druckort,
                              'uid':brain.UID})

        if listSortKey:
            items.sort(key=lambda i: i[listSortKey],reverse=listSortDesc)

        return items

    def __listEqTuple(self,l,t):
        """Compare a list's content with a tuple's content"""
        if(len(l)==len(t)):
            for elem in l:
                if elem not in t:
                    return False
            return True
        else:
            return False

    def __listHasElemFromTuple(self,l,t):
        """Compare a list's content with a tuple's content"""
        for elem in l:
            if elem in t:
                return True
        else:
            return False

    def __createTextQuery(self):
        """
        returns the query for the search
        """
        request = self.request
        
        searchabletext=''

        if(request.AndWords):
            #AndWords is not empty
            #=> list the words and create a string with '+and+' between them
            andwords = ' and '.join(request.AndWords.split())
        else:
            andwords =  ''
        searchabletext+=andwords

        if(request.OrWords):
            if(searchabletext):
                #append to andwords
                orwords  = ' or '+' or '.join(request.OrWords.split())
            else:
                orwords  = ' or '.join(request.OrWords.split())
        else:
            orwords  = ''
        searchabletext+=orwords

        if(request.Phrase):
            if(searchabletext):
                phrase  = " and \""+' '.join(request.Phrase.split())+"\""
            else:
                phrase  = "\""+' '.join(request.Phrase.split())+"\""
        else:
            phrase  = ''
        searchabletext+=phrase
        
        if(request.NotWords):
            if(searchabletext):
                notwords  = ' and not '+' and not '.join(request.NotWords.split())
            else:
                notwords = ''
        else:
            notwords  = ''
        searchabletext+=notwords

        return searchabletext

    
