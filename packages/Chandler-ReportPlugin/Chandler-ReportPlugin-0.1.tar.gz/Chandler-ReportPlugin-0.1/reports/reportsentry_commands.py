#   Copyright (c) 2007 Open Source Applications Foundation
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

import re

from application import schema
from osaf import sharing

from osaf.pim.stamping import has_stamp
from osaf.pim.notes import Note
from osaf.pim.calendar.Calendar import parseText
from osaf.usercollections import UserCollection
from osaf.framework.blocks.Block import Block

from osaf.quickentry import QuickEntryState, QuickEntryCommand

from reports import ProgressReports
from reports.ReportStamps import ReportStamp

from i18n import ChandlerMessageFactory as _
from datetime import datetime, timedelta

class ReportState(QuickEntryState):
    """
    State for creating and processing a report
    """
    def __init__(self, view, text):
        self.view = view
        self.text = text
        self.item = Note(itsView = view)
        self.item.InitOutgoingAttributes()
        
        self.parse_tuple = parseText(view, text)
        self.until = datetime.now()
        self.since = datetime.now() - timedelta(days=7)
        self.collection = None
        
    def finalize(self):
        self.item.displayName = _(u"Report")
    
    def set_time(self):
        startTime, endTime, countFlag, typeFlag = self.parse_tuple
        # Check whether there is a date/time range
        # if only one date it will be the start date
        if startTime == endTime:
            endTime = None 
        # if there is no time set evoke default report for one week
        if (typeFlag == 0) :
            startTime = None
            endTime = None
        
        (self.since, self.until) = ProgressReports.parseTime(self.collection, 
                                                             self.text, 
                                                             startTime, endTime)
        ReportStamp(self.item).until = self.until
         
         
    def set_collection(self):
        mainView = Block.findBlockByName("MainView")
        allCollection = schema.ns('osaf.pim',mainView).allCollection
        selectedCollection = mainView.getSidebarSelectedCollection()
        if (selectedCollection is None or
            sharing.isReadOnly(selectedCollection) or
            not UserCollection(selectedCollection).canAdd):
            self.collection = allCollection
        else:
            self.collection = selectedCollection
    
    def set_report_body(self):
        self.item.body =   ProgressReports.getReport(self.view, 
                                                self.collection,
                                                self.since, self.until)

class ReportCommand(QuickEntryCommand):
    """
    If the selected collection allows it, Report will be added to it, and
    the progress of items in the selected collection will be analyzed.
    Otherwise, 'all' collection will be used as selected collection.
    
    parse user's command, and create a report in accordance to it. Update
    the fields of the report. Write the report info in the body of newly 
    created ReportStamp item. Select the created report.
    
    """
#    single_command = False
    stamp_types = [ReportStamp]
    # L10N: A comma separated list of names for commands to create a report
    command_names = _(u"report").split(',')
    state_class = ReportState
    @classmethod
    def process(cls, state):
        for stamp in cls.stamp_types:
            if not has_stamp(state.item, stamp):
                stamp(state.item).add()

        state.set_collection()
        state.set_time()
        state.set_report_body()
        return state
    

#stamp_to_command = {ReportStamp       : ReportCommand}
           