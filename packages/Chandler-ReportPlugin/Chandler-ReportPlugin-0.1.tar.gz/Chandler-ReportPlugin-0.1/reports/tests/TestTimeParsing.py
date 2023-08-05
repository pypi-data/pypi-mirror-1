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
from osaf.pim import *

from reports import ProgressReports
from reports.ReportStamps import ReportStamp

class TestTimeParsing(unittest.TestCase):
    """Tests correctness of  the report command  interpretation
    from the quick entry"""
    
    def setUp(self):
        # setting up the repository, a new view and a trash collection
        self.chandlerDir = os.environ['CHANDLERHOME']
        self.repoDir = os.path.join(self.chandlerDir, '__repository__')
        rep = DBRepository(self.repoDir)
        rep.create(create=True, refcounted=True, ramdb=True)
        self.view = rep.createView()
        
        # specific to reports testing
        self.testCollection = SmartCollection('test', itsView=self.view)
        # times
        self.now = datetime.now(self.view.tzinfo.default)
        self.before_now = self.now - timedelta(hours=1)
        self.almost_now = self.now - timedelta(hours=0.5)
        self.since = self.now - timedelta(days=7)
        self.before_since = self.since - timedelta(days=1)
        self.after_now = self.now + timedelta(hours=0.1)
    
         
    def testLastReportExisting(self):
        """
        Tests correct retrieval of the latest report from a collection
        """
        def _createReport(created, until): 
            item = Note(displayName = "Report", itsView=self.view, 
                        createdOn = created)
            report = ReportStamp(item)
            report.add()
            report.until = until
            return report
        startTime = None
        endTime = None
        existingReport = _createReport(self.before_since, self.almost_now)
        previousReport = _createReport(self.before_now, self.before_now)
        self.testCollection.add(existingReport.itsItem)
        self.testCollection.add(previousReport.itsItem)
        self.view.commit()
        
        (since, until) = ProgressReports.parseTime(self.testCollection, 
                                                   "last", startTime, 
                                                   endTime)
        self.failIf(since==previousReport.until, 
                    "reporting on earlier report, instead of the latest")
        self.failUnless(since==existingReport.until, 
                        "last report is not recognized as the latest")
       
        