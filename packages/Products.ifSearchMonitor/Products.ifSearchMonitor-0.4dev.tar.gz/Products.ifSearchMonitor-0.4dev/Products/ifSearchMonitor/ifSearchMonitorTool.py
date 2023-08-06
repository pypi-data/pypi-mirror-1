## Written by Matias Bordese <matiasb@except.com.ar>
## (c) 2007 ifPeople http://ifpeople.net/

# This file is part of ifSearchMonitor.
#
#     ifSearchMonitor is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     ifSearchMonitor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with ifSearchMonitor; if not, write to the Free Software
#     Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CMFCore.utils import getToolByName, UniqueObject
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from Globals import InitializeClass

from string import join
import re

from config import TOOLNAME

class ifSearchMonitorTool(UniqueObject, SimpleItem):
    """A tool to handle the search statistics"""

    id = 'ifSearchMonitor_tool'
    meta_type= TOOLNAME
    plone_tool = 1

    security = ClassSecurityInfo()

    def __init__(self):
        self._searchStatistics = PersistentMapping({})

    security.declareProtected(View, 'getTermStatistics')
    def getTermStatistics(self, term):
        """Return the search statistics of the term"""
        key = self.getTermsKey(term)
        ret = self._searchStatistics.get(key, [0,0,0,0,0])
        return ret

    security.declareProtected(View, 'getSuggestedCriterias')
    def getSuggestedCriterias(self):
        """Returns a list of the terms that has suggested results"""
        index = self.portal_catalog.Indexes['SuggestedCriteria']
        suggested = index.items()
        suggested = [r[0] for r in suggested]
        #terms = self.getSearchedTerms('number', 'des')
        #ret = []
        #for r in terms:
            #if r in suggested:
                #ret.append(r)
        return suggested

    security.declareProtected(View, 'getSearchedTerms')
    def getSearchedTerms(self, sort_key=None, order='asc'):
        """Returns a list of the terms that were used for the searches.
        The params are used to sort this list according to the statistics of
        each term, in 'asc'endig or 'des'cending order"""
#         (a) number of search for a given term, (b) number of results for a given search term, (c) number of click-throughs to a resul
        k=0 #if the sort_key is invalid, it will sort by the number of searches
        if not sort_key: return list(self._searchStatistics)
        elif sort_key=='number':
            k=0
        elif sort_key=='results':
            k=2
        elif sort_key=='clicks':
            k=1
        res = [(self.getTermStatistics(term)[k],term) for term in list(self._searchStatistics)]
        if res:
            def sort_order(a,b):
                return cmp(a[0],b[0])
            res.sort(sort_order)
            if order=='des': res.reverse()
            res = [t for (k,t) in res]
        return res

    security.declareProtected(View, 'doSearch')
    def doSearch(self, REQUEST=None,use_types_blacklist=True):
        """Search interface that keeps statistics"""
# [number of times searched for, number of results clicked, number of results (total), not usefuls, usefuls]
        #import pdb;pdb.set_trace()
        res = self.queryCatalog(REQUEST,use_types_blacklist=use_types_blacklist)
        if not REQUEST.has_key('b_start') and REQUEST.has_key('SearchableText'):
            terms = REQUEST.get('SearchableText', '')
            if terms:
                key = self.getTermsKey(terms)
                res_q = len(res)
                stats = self._searchStatistics.get(key, [0,0,0,0,0])
                stats[0] = stats[0] + 1
                stats[2] = stats[2] + res_q
                self._searchStatistics[key] = stats
        return res

    security.declareProtected(View, 'searchedResult')
    def searchedResult(self, REQUEST=None, RESPONSE=None):
        """Registers the user click in the search results"""
        search_terms = REQUEST.get('searchterm', '')
        if search_terms:
            key = self.getTermsKey(search_terms)
            stats = self._searchStatistics.get(key)
            if stats:
                stats[1] = stats[1] + 1
                self._searchStatistics[key] = stats
        url = REQUEST['resulturl']
        if RESPONSE:
            RESPONSE.redirect(url + '?searchterm=' + search_terms)

    security.declareProtected(View, 'sendFeedback')
    def sendFeedback(self, searchterm, feedback, REQUEST=None, RESPONSE=None):
        """Registers the user feedback"""
        search_terms = REQUEST.get('searchterm', '')
        if search_terms:
            key = self.getTermsKey(search_terms)
            stats = self._searchStatistics.get(key)
            if stats:
                pos = 3 + int(feedback)
                stats[pos] = stats[pos] + 1
                self._searchStatistics[key] = stats

    security.declareProtected(View, 'getSuggestedResults')
    def getSuggestedResults(self, searchterm):
        """Return the suggested search results for searchterm"""
        res = []
        if searchterm:
            key = self.getTermsKey(searchterm)
            res = self.portal_catalog.searchResults(SuggestedCriteria=key)
        return res

    security.declareProtected(View, 'getTermsKey')
    def getTermsKey(self, searchterm):
        """Return the searchterms in alphabetical order, removing and/or/not"""
        terms = searchterm.lower()
        #terms = terms.split()
        terms = re.findall('\w+', terms)
        while 'not' in terms:
            terms.remove('not')
        while 'and' in terms:
            terms.remove('and')
        while 'or' in terms:
            terms.remove('or')
        terms.sort()
        key = ' '.join(terms)
        return key

InitializeClass(ifSearchMonitorTool)
