# This isnt a BrowserView because it has no management tab
# so causes acquisition pickling errors when accessed
# as a child object of the migration tool - so use SimpleItem
# NB: memoize also causes pickling errors 
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from ilrt.migrationtool.browser.interfaces import IATFieldIndexInfo

class ATFieldIndexInfo(SimpleItem):
    """
       Code from Products.PloneKeywordManager
       by Maik Jablonski and the Plone Collective
       adapted to move keywords between different fields / indexes

       A use case being to move a subset of the standard
       keywords into their own field and controlled vocabulary.
    """
 
    implements(IATFieldIndexInfo)

    def fieldNameForIndex(self, indexName):
        """The name of the index may not be the same as the field on the object, and we need
           the actual field name in order to find its mutator. 
        """
        catalog = getToolByName(self, 'portal_catalog')    
        indexObjs = [idx for idx in catalog.index_objects() if idx.getId() == indexName]
        try:
            fieldName = indexObjs[0].indexed_attrs[0]
        except IndexError:
            raise ValueError('Found no index named %s' % indexName)
        return fieldName

    def getListFieldValues(self, obj,indexName):
        """Returns the current values for the given Lines field as a list.
           Checks if its only a brain and retrieves source object
        """
        fieldName = self.fieldNameForIndex(indexName)
        if not hasattr(obj,fieldName) and hasattr(obj,'getObject'):
            obj = obj.getObject()
        fieldVal = getattr(obj,fieldName,())
        if callable(fieldVal):
            return list(fieldVal())
        else:
            return list(fieldVal)

    def getSetter(self, obj,indexName):
        """Gets the setter function for the field based on the index name.
        """
        fieldName = self.fieldNameForIndex(indexName)
        fieldObj = obj.getField(fieldName) or obj.getField(fieldName.lower())
        if fieldObj is not None:
            return fieldObj.getMutator(obj)
        return None

    def moveKeyword(self, portal, old_keyword, new_keyword='', old_index='Subject', new_index=''):
        """Updates all objects using the old_keyword and index to the new ones.
           Returns the number of objects that have been updated.

           There are various options for use to move, merge or delete keywords:
           
           1. keywords different and indexes different - migrates a keyword to a new one in a different index
              or merges it if new_keyword exists already in new_index
           2. both keywords the same but indexes different - moves a keyword between indexes
           3. keywords different but indexes the same - moves a keyword within an index to a new keyword
              or merges items with the old_keyword into an existing one if new_keyword exists already
           4. new_keyword not supplied or empty string - deletes the old_keyword from old_index 
           If no new keyword supplied it deletes the old ones.
        """
        if old_keyword == new_keyword and old_index == new_index:
            return 0
        query = {old_index: [old_keyword,]}
        query['path'] = '/'.join(portal.getPhysicalPath())
        catalog = getToolByName(portal, 'portal_catalog')
        querySet = catalog(**query)

        for item in querySet:
            idxs = []
            obj = item.getObject()
            old_subjectList = self.getListFieldValues(obj,old_index)                
            old_subjectList.remove(old_keyword)

            if new_keyword:
                new_subjectList = self.getListFieldValues(obj,new_index)
                if new_keyword not in new_subjectList:
                    new_subjectList.append(new_keyword)
                new_subjectList = list(set(new_subjectList))
                if old_index == new_index:
                    new_subjectList.remove(old_keyword)

            if old_index != new_index:
                old_subjectList = list(set(old_subjectList))        
                updateField = self.getSetter(obj,old_index)
                if updateField is not None:
                    updateField(old_subjectList)
                    idxs.append(old_index)

            if new_keyword:
                updateField = self.getSetter(obj,new_index)
                if updateField is not None:
                    updateField(new_subjectList)
                    idxs.append(new_index)

            if idxs:
                obj.reindexObject(idxs=idxs)

        return len(querySet)
