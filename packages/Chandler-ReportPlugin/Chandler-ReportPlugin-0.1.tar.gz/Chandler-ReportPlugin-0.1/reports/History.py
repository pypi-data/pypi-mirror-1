import os, time
from repository.persistence.DBRepository import DBRepository
from osaf.usercollections import UserCollection
from osaf.pim import TriageEnum, getTriageStatusName

""" Provide methods to extract historic information from repository.

Warning: creating a new view in the repository is a costly operation. 
Recommended usage: Create a new view using makeView and reuse it for 
other methods. Don't forget to call cleanup to close it after you are done.

"""
def makeView(items, view=None):
    """ Create and return a new view for the given collection.
    
    items -- given collection
    view -- an optional argument of an already existing repository view, if
    not None, a new view is NOT created and it is returned as is for reusal
    
    return DBRepositoryView
     
    """
    newView = view
    if view is None:
        newView = items.itsView.repository.createView()
    
    return newView

def cleanupView(newView, view=None):
    """ Cleanup the view (close or leave for reusing).
    
    newView -- given collection
    view -- an optional argument of an already existing repository view. 
    if not provided newView is closed, otherwise it is left open for reusal
    
    take care of the views that were newly created within the function and
    need to be closed
    
    """
    if view is None:
        newView.closeView() 
    
def getItemHistory(uuid, items, view=None):
        """Return all historic values for a given item in the given collection.
        
        uuid - the given item's uuid
        items - collection that contains the item, history is checked within it
        view - optional DBRepositoryView argument (default None). If provided 
        this view will be reused
        
        return dictionary of dictionaries of item's values for all the versions
        in the repository. 
        
        """
        newView = makeView(items,view)
        curVersion = newView.itsVersion
        itemHistory = {}
        
        while curVersion > 0:
            itemSnapshot = newView.findUUID(uuid)
            then = getDateForView(newView)
            values = {}
            values['uuid'] = uuid
            values['version'] = newView.itsVersion
            if itemSnapshot is None:
                values['exists'] = False
            else:
                values.update(itemSnapshot.itsValues)
                values['exists'] = True
            itemHistory[then] = values  
            if (newView.itsVersion > 1):
                newView.itsVersion -= 1 
            curVersion -= 1             
        cleanupView(newView, view)
        return itemHistory    
 
def getItemHistorySince(uuid, items, since,view=None):
        """Return versions of a given item that were committed after given time.
        
        uuid - the given item's uuid
       items - collection that contains the item, history is checked within it.
        since - timestamp for the deepest version to iterate in repository
        view - optional DBRepositoryView argument (default None). If provided 
        this view will be reused
        
        return dictionary of dictionaries of item's values for all the versions 
        after since in repository. 
        
        """
        newView = makeView(items,view)
        curVersion = newView.itsVersion
        itemHistory = {}
        # handler the case when the view version is 0, it is not iterable
        if curVersion == 0:
            return itemHistory
        then = getDateForView(newView)
    
        while (curVersion > 0) and (then >= since):
            itemSnapshot = newView.findUUID(uuid)
            then = getDateForView(newView)
            values = {}
            values['uuid'] = uuid
            values['version'] = newView.itsVersion
            if itemSnapshot is None:
                values['exists'] = False
            else:
                values.update(itemSnapshot.itsValues)
                values['exists'] = True
            itemHistory[then] = values  
            if (newView.itsVersion > 1):
                newView.itsVersion -= 1 
            curVersion -= 1             
        cleanupView(newView, view)
        return itemHistory   
     
def getDateForView(view):
    """Return timestamp view's current version's commit to the repository."""
    store = view.store
    then, x, x, x = store.getCommit(view.itsVersion)
    return then

def getItemFeatureByVersion(items, version, uuid, ref, feature, view=None):
        """Return attribute of an attribute value for item from repository
        
        items - collection that contains the item
        version - the item's version in repository
        uuid - item's uuid
        ref - the name of a complex attribute
        feature - the attribute name of attribute in ref
        view - optional DBRepositoryView argument (default None). If provided 
        this view will be reused
        
        return list of ref.feature values for the given version of item in 
        collection
        
        """
        newView = makeView(items,view)
        result = None
        if version >= 0:   
            newView.itsVersion = version
            itemSnapshot = newView.findUUID(uuid)
            if hasattr(itemSnapshot, ref):
                val = getattr(itemSnapshot, ref)
                if hasattr(val, feature) :
                    result = [getattr(val, feature)]
                elif isinstance(val, list):
                    result = [getattr(itemRef, feature) for itemRef in val]
        cleanupView(newView, view)   
        return result

def getDeletedItems(items, view):
        """Return items that were deleted from given collection
        
        items - collection that is searched for deleted items
        
        Note: a new view is created in this method, and there is no option to 
        reuse an old view. This method is collection based, rather than item-based,
        which reduces the cost of new view creation. Refreshing the view 
        forwards is not possible within a reused view.
        
        
        Return list of dictionaries with values of deleted items. Each dictionary
        is added the keys 'deleted', 'version' and 'uuid' to mark the items as 
        deleted, to make the version before deletion and the uuid retrievable.
         
        """
        itemsUUIDList = [item.itsUUID for item in items]
        newView = makeView(items, view)
        curVersion = newView.itsVersion
        #assuming all of the items appear in the same collection
        colUUID = items.itsUUID
        deletedItems = []
        deletedUUIDs = []
        while curVersion > 0:
            collection = newView.findUUID(colUUID) 
            if collection is not None:    
                for item in collection:
                    curUUID = item.itsUUID
                    if (not curUUID in itemsUUIDList and 
                        not curUUID in deletedUUIDs):
                        values = {}
                        values.update(item.itsValues)
                        values['uuid'] = curUUID
                        values['version'] = curVersion
                        values["deleted"] = getDateForView(newView)
                        deletedUUIDs.append(curUUID)
                        deletedItems.append(values)
            if (newView.itsVersion > 1):
                newView.itsVersion -= 1 
            curVersion -= 1               
        cleanupView(newView, view)
        return deletedItems      