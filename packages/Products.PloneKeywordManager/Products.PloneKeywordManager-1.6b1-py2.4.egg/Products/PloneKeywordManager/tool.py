# Copyright (c) 2005 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tool.py 47645 2007-08-20 14:59:10Z glenfant $

# Python imports
try:
    import Levenshtein
    USE_LEVENSHTEIN = True
except ImportError:
    import difflib
    USE_LEVENSHTEIN = False

# Zope imports
import Globals
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo 
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.Expression import Expression
try:
    from Products.CMFCore import CMFCorePermissions
except ImportError, e:
    from Products.CMFCore import permissions as CMFCorePermissions

# Sibling imports
from Products.PloneKeywordManager.interfaces import IPloneKeywordManager
from Products.PloneKeywordManager import config

class PloneKeywordManager(UniqueObject, SimpleItem):
    """A portal wide tool for managing keywords within Plone."""

    plone_tool = 1

    id = "portal_keyword_manager"
    meta_type = "Plone Keyword Manager Tool"
    security = ClassSecurityInfo()
    
    __implements__ = (IPloneKeywordManager,)

    manage_options = ({'label' : 'Overview', 'action' : 'manage_overview'},)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/explainTool', globals(), 
            __name__='manage_overview')

    security.declarePublic('usingLevenshtein')
    def usingLevenshtein(self):
        """ Returns True iff Levenshtein is installed and will be used instead
        of difflib
        """
        return USE_LEVENSHTEIN

    security.declarePrivate('getSetter')
    def getSetter(self,obj,field):
        """Gets the setter function for the field.
        
        Returns None if it can't get the function
        """
        if field.startswith("get"):
            setter = field.replace("get","set",1)
        else:
            setter = "set" + field.capitalize() #"Subject" => "setSubject"
        
        return getattr(obj,setter,None)
        
        
    security.declarePublic('change')
    def change(self, old_keywords, new_keyword, context=None,field='Subject'):
        """Updates all objects using the old_keywords.

        Objects using the old_keywords will be using the new_keywords
        afterwards.

        Returns the number of objects that have been updated.
        """
        self._checkPermission(context)
        ##MOD Dynamic field getting
        query = {field: old_keywords}
        if context is not None:
            query['path'] = '/'.join(context.getPhysicalPath())
        querySet = self._query(**query)

        for item in querySet:
            obj = item.getObject()
            ##MOD Dynamic field getting
            subjectList = list(getattr(obj,field,'Subject')())      

            for element in old_keywords:
                while (element in subjectList) and (element <> new_keyword):
                    subjectList[subjectList.index(element)] = new_keyword

            # dedupe new Keyword list (an issue when combining multiple keywords)
            subjectList = list(set(subjectList))
            
            ##MOD Dynamic field update
            updateField = self.getSetter(obj,field)
            if updateField is not None:
                updateField(subjectList)
                idxs=[field].extend([i for i in config.ALWAYS_REINDEX if i != field])
                obj.reindexObject(idxs=idxs)
        
        return len(querySet)

    security.declarePublic('delete')
    def delete(self, keywords, context=None, field='Subject'):
        """Removes the keywords from all objects using it.
        
        Returns the number of objects that have been updated.
        """
        self._checkPermission(context)
        ##Mod Dynamic field
        query = {field: keywords}
        if context is not None:
            query['path'] = '/'.join(context.getPhysicalPath())
        querySet = self._query(**query)

        for item in querySet:
            obj = item.getObject()
            
            subjectList = list(getattr(obj,field)())

            for element in keywords:
                while element in subjectList:
                    subjectList.remove(element)
            
            updateField = self.getSetter(obj,field)
            if updateField is not None:
                updateField(subjectList)
                idxs=[field].extend([i for i in config.ALWAYS_REINDEX if i != field])
                obj.reindexObject(idxs=idxs)

        return len(querySet)

    security.declarePublic('getKeywords')
    def getKeywords(self, context=None, field='Subject'):
        self._checkPermission(context)
        if field not in self.getKeywordIndexes():
            raise ValueError, "%s is not a valid field" % field
        
        catalog = getToolByName(self, 'portal_catalog')
        
        #why work hard if we don't have to?
        #if hasattr(catalog,'uniqueValuesFor'):
        keywords = list(catalog.uniqueValuesFor(field))
        #else:
        #    query = {}
        #    if context is not None:
        #        query['path'] = '/'.join(context.getPhysicalPath())
        #    keywords = {}
        #    for b in self._query(**query):
        #        for keyword in getattr(b,field)():
        #            keywords[keyword] = True
        #    keywords = keywords.keys()
        
        keywords.sort()
        return keywords

    security.declarePublic('getScoredMatches')
    def getScoredMatches(self, word, possibilities, num, score, context=None):
        """ Take a word,
            compare it to a list of possibilities,
            return max. num matches > score).
        """
        self._checkPermission(context)
        if not USE_LEVENSHTEIN:
            # No levenshtein module around. Fall back to difflib
            return difflib.get_close_matches(word, possibilities, num, score)
        
        # Levenshtein is around, so let's use it.
        res = []
        
        # Search for all similar terms in possibilities
        for item in possibilities:
            lscore = Levenshtein.ratio(word, item)
            if lscore > score:
                res.append((item,lscore))

        # Sort by score (high scores on top of list)
        res.sort(lambda x,y: -cmp(x[1],y[1]))

        # Return first n terms without scores
        return [item[0] for item in res[:num]]

    def _query(self, **kwargs):
        catalog = getToolByName(self, 'portal_catalog')
        return catalog(**kwargs)

    def _checkPermission(self, context):
        if context is not None:
            context = context
        else:
            context = self
        if not getSecurityManager().checkPermission(
            config.MANAGE_KEYWORDS_PERMISSION, context):
            raise Unauthorized("You don't have the necessary permissions to "
                               "access %r." % (context,))

    def getKeywordIndexes(self):
        """Gets a list of indexes from the catalog. Uses config.py to choose the
        meta type and filters out a subset of known indexes that should not be
        managed.
        """
        catalog = getToolByName(self, 'portal_catalog')
        idxs = catalog.index_objects()
        idxs = [i.id for i in idxs if i.meta_type==config.META_TYPE and
                i.id not in config.IGNORE_INDEXES]
        idxs.sort()
        return idxs

Globals.InitializeClass(PloneKeywordManager)
