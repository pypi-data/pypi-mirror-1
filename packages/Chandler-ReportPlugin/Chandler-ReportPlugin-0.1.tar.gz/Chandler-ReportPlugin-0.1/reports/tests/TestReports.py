#   Copyright (c) 2003-2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os,unittest,logging
from osaf.pim.collections import *
from datetime import datetime, timedelta
from repository.persistence.DBRepository import DBRepository
from osaf.pim import Note, TriageEnum, Triageable
from osaf.pim import *
import time

from reports import ProgressReports, History


class TestReports(unittest.TestCase):
    """
    Sanity check of the basic sections in reports.
    
    iCalUID attribute is used as the unique key to test the presence of items
    in reports
    
    Reports from one week ago until now are tested
    
    Known issues:
    It is impossible to set the commit time for the repository, and 
    reports is based on the timestamps of commits to deduce about items 
    history. Hence, reports commiting is tested here in a very fine granularity
    of several seconds, commiting and making small changes in real time.
    In realistic usecases, reports are supposed to be of rougher granularity 
    (days and not minutes)
    
    """
    def setUp(self):
        """ Setup a repository, a collection and time for testing."""
        # setting up the repository, a new view and a trash collection
        self.chandlerDir = os.environ['CHANDLERHOME']
        self.repoDir = os.path.join(self.chandlerDir, '__repository__')
        rep = DBRepository(self.repoDir)
        rep.create(create=True, refcounted=True, ramdb=True)
        self.view = rep.createView()
        self.trash = schema.ns('osaf.pim', self.view).trashCollection
        
        # specific to reports testing
        self.testCollection = SmartCollection('test', itsView=self.view)
        # times
        self.now = datetime.now(self.view.tzinfo.default)
        self.before_now = self.now - timedelta(hours=1)
        self.almost_now = self.now - timedelta(hours=0.5)
        self.since = self.now - timedelta(days=7)
        self.before_since = self.since - timedelta(days=1)
        self.after_now = self.now + timedelta(hours=0.1)
        
        #parent item
        self.papa = ContentItem("papa", self.view, None)
    
    def createNote(self,name, created):
        """Return a new note.
        
        name -- the displayName of the new note
        created -- the datetime for createdOn attribute
        
        This method is used internally by the test methods
        
        """  
        createdNote = Note(displayName=name, itsView =self.view, 
                           createdOn = created)
        return createdNote

    def testNewItems(self):
        """Test the reporting on new arrivals.
        
        create a new note item and an old note item,
        test that the new item is reported as new
        test that the old item is not reported as new
        
        Not Implemented: Does not test for items newly received from somewhere
        
        """
        
        newItem = self.createNote("new test item", self.before_now)
        oldItem = self.createNote("old test item", self.before_since)
        
        self.testCollection.add(newItem)
        self.view.commit()
    
        self.assert_(newItem in self.testCollection)
        self.testCollection.add(oldItem)
        self.assert_(newItem in self.testCollection)
     
        reportList = ProgressReports.getNewArrivals(self.testCollection,
                                                    self.now,self.since)
    
        uids = [itemValues['icalUID'] for itemValues in reportList]
        self.failIf(oldItem.icalUID in uids, "an old item is reported as new")
        self.failUnless(newItem.icalUID in uids, 
                        "a new item is not reported as a new arrival")
        
    def testDeletedItems(self):
        """Test retrieval of items that were deleted.
        
        create a new note item and commit it to the repository,
        delete the item and commit the change
        test that the deleted item is retrieved as such.
        
        """
        newItem = self.createNote("deletedTestItem", self.now)
        self.testCollection.add(newItem)
        self.view.commit()
        uid = newItem.icalUID
        newItem.delete(True)
        self.view.commit()
        delView = History.makeView(self.testCollection)
        deletedItems = History.getDeletedItems(self.testCollection, delView)
        History.cleanupView(delView)
        uids = [itemValues['icalUID'] for itemValues in deletedItems]
        self.failUnless(uid in uids, "a deleted item's data is not retrieved")
    
    def testAchievements(self):
        """Test reporting on items that were DONE during the reported period.
        
        create two items, set triage status of NOW for both,
        commit the settings to the repository
        change one of the items' status to DONE
        
        test that the doneItem appears in the list of achievements
        test that the stillNowItem does not appear in the list of achievements
        
        """
        doneItem = self.createNote("achievement", self.before_now)
        stillNowItem = self.createNote("oldAchievement", self.before_now)
        
        doneItem.setTriageStatus(TriageEnum.now, self.before_now)
        stillNowItem.setTriageStatus(TriageEnum.done, self.before_now)
        self.view.commit()
        
        doneItem.setTriageStatus(TriageEnum.done, self.almost_now)
        
        self.testCollection.add(doneItem)
        self.testCollection.add(stillNowItem)
      
        reportList = ProgressReports.getAchievements(self.testCollection,
                                                     self.now,self.since)
        names = [itemValues['icalUID'] for itemValues in reportList]
        
        self.failIf(stillNowItem.icalUID in names, 
                    "an item that is not an achievement is reported as such")
        self.failUnless(doneItem.icalUID in names, 
                        "a new achievement is not reported as such")
        
    
    def testTransitionIn(self):
        """Test reporting on items that came into focus during reported period.
        
        In real time:
        inItem: create with status of LATER, commit the change, sleep
        change the status to NOW, commit
        stillOutItem: same as for inItem, but after additional 10 seconds sleep,
        change the status back to LATER, commit
        
        test that the inItem appears in the list of transitioned in
        test that the stillOutItem does not appear in the list of achievements, 
        because it is still in the status of LATER
        
        """
        
        stillOutItem = self.createNote("item still out of focus", 
                                       self.before_since)
        inItem = self.createNote("came in focus", self.before_since)
        
        stillOutItem.setTriageStatus(TriageEnum.later, self.before_since)
        inItem.setTriageStatus(TriageEnum.later, self.before_since)
        self.testCollection.add(stillOutItem)
        self.testCollection.add(inItem)
        self.view.commit()
        
        delta = 8
        time.sleep(delta)
        new_now = datetime.now
        stillOutItem.setTriageStatus(TriageEnum.now, new_now)
        inItem.setTriageStatus(TriageEnum.now, new_now)
        self.view.commit()
        
        time.sleep(delta)
        new_now = datetime.now
        stillOutItem.setTriageStatus(TriageEnum.later, new_now)
        self.view.commit()
        
        reportList = ProgressReports.getTransitionOfFocus(self.testCollection, 
                                                          self.after_now, 
                                                          self.almost_now, 
                                                          direction="in")
        
        uids = [itemValues['icalUID'] for itemValues in reportList]
        self.failUnless(inItem.icalUID in uids, 
                        "an item with transition focus in was not reported")
        self.failIf(stillOutItem.icalUID in uids, 
                    "an item with transition focus out was reported")
       
    def testPersistentItemsNow(self):
        """Test reporting on persistent items in the status of NOW .
        
        create two items from more than one week ago. 
        oldItem: set an old triage status of NOW, and don't change it.
        changedItem: create it with a status of LATER, and change to NOW 30
        minutes ago.
        
        test that oldItem appears in the list of persistent items
        test that changedItem does not appear in the list of persistent items
        
        """
        oldItem = self.createNote("old persistent item", self.before_since)
        oldItem.setTriageStatus(TriageEnum.now, self.before_since)
        self.testCollection.add(oldItem)
        
        changedItem = self.createNote("changing item", self.before_since)
        changedItem.setTriageStatus(TriageEnum.later, self.before_since)
        changedItem.setTriageStatus(TriageEnum.now, self.almost_now)
        self.testCollection.add(changedItem)
        
        reportList = ProgressReports.getPersistentItems(self.testCollection,
                                                        self.now,self.since, 
                                                        TriageEnum.now)
        
        uids = [itemValues['icalUID'] for itemValues in reportList]
        self.failUnless(oldItem.icalUID in uids, 
                        "a persistent item is not reported")
        self.failIf(changedItem.icalUID in uids, 
                    "recently changed item is reported as persistent") 
    
    def testUpdatedItems(self):
        """Test reporting on items that their body was edited.
        
        create two items from more than one week ago and commit the change.
        changedItem: change its body's text
        anotherItem: no change to its body text
        change the modification state to edited for both items in the current
        time, commit the changes.
        
        test that changedItem appears in the list of updated items
        test that anotherItem does not appear in the list of updated items
        
        Not Implemented: test whether body was changed by this user, or another
        """
        changedItem = Note(
                  itsParent=self.papa,
                  createdOn=self.before_since,
                  lastModification=Modification.created,
                  lastModified=self.before_since,
                  body = "some text that will be changed",
                  displayName = "changed item"
               )
        anotherItem = Note(
                  itsParent=self.papa,
                  createdOn=self.before_since,
                  lastModification=Modification.created,
                  lastModified=self.before_since,
                  body = "some text that is never changed",
                  displayName = "another Item"
               )
        self.testCollection.add(changedItem)
        self.testCollection.add(anotherItem)
        self.view.commit()
        
        modified = datetime.now(self.view.tzinfo.default)
        #changedItem's body was updated and it is supposed to be reported
        changedItem.body="new text"
        changedItem.changeEditState(Modification.edited, when=modified)
        #anotherItem is just edited, but no update to the body
        anotherItem.changeEditState(Modification.edited, when=modified)
        self.view.commit()
        
        reportList = ProgressReports.getUpdatedItems(self.testCollection, 
                                                     self.after_now, 
                                                     self.since)
        uids = [itemValues['icalUID'] for itemValues in reportList]
        
        self.failUnless(changedItem.icalUID in uids, 
                        "an updated item is not reported")
        self.failIf(anotherItem.icalUID in uids, 
                    "not updated item is reported") 


    #def tearDown(self):
     #   self.view.closeView()
      #  pass

if __name__ == "__main__":
    unittest.main()
