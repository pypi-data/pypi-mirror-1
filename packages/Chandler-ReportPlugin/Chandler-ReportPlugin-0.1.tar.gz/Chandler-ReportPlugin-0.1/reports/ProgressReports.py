#   Copyright (c) 2004-2007 Open Source Applications Foundation
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

from osaf.pim import *
from osaf.pim.calendar import Calendar
from i18n import ChandlerMessageFactory as _
from osaf.pim.calendar.DateTimeUtil import shortDateTimeFormat

from datetime import datetime, timedelta
import time
from time import mktime
from PyICU import ICUtzinfo

from ReportStamps import ReportStamp


import re

import History

""" Main module that handles reporting functionality.

Methods:
utility functions for time conversion
utility method for reported item representation
methods to parse the user command for reports
methods for retrieval of items for each section of report


Assumption: commit time in repository represents the real time of changes
happening to the items. For instance, if triage status has changed, there 
will be a  new version of the item commited to the repository right away

"""
def getEpochTime(floatTime):
    """Return timestamp since the epoch equivalent to given floatTime."""
    return mktime(floatTime.astimezone(ICUtzinfo.default).timetuple())

def getShortDateTimeFromEpoch(view, epochTime):
    """Return shortDateTimeFormat of timestamp epochTime in given view."""
    return shortDateTimeFormat.format(view,
                                      datetime.fromtimestamp(epochTime,
                                                             ICUtzinfo.default))

"""Template to represent information about reported item"""
item_template = _(u"""\
"%(name)s" - %(displaysource)s: %(displaydate)s [%(stamps)s]
%(details)s""")

"""Template to represent detailed information about reported item"""
details_template = _(u"""\
Details:
%(details)s""")

#######string representations########
def getItemValues(item):
    """Update and return a dictionary with values of item.
    
    item -- examined item
    
    Update a dictionary with the values stored in the repository for item.
    update the value for item's uuid.
    
    Recurring event: if the item is a recurring events, some of its values 
    are not explicitly stored in the repository. The values for its name, 
    and date of creation are updated.
    
    Return the retrieved and updated dictionary of item's values.
    
    """
    values = {}
    values.update(item.itsValues)
    values['uuid'] = item.itsUUID
    # special case for recurring events
    if has_stamp(item, EventStamp):
        event = EventStamp(item)
        if Calendar.isRecurring(event):
            values['displayName'] = item.displayName
            values['createdOn'] = item.createdOn
            values['recurring'] = True
    return values

def getVersion(items, itemValues):
    """Return itemValues['version'] if exists, or return current version."""
    return itemValues.get('version', items.itsView.itsVersion)

def getRecurAttr(items, itemValues, attr, view=None):
    """Return given attribute, or if not available return inherited attribute.
    
    items - current collection
    itemValues - a dictionary with the values stored in repository for item
    attr - name of attribute of the item
    
    For attributes that do not appear in values of the given item return the
    attribute it inherits. Useful for recurring events.
    
    return value of the attribute (typically datetime or string)
    """
    res = itemValues.get(attr)
    
    if res is None:
        res = History.getItemFeatureByVersion(items, 
                                              getVersion(items, itemValues),
                                              itemValues['uuid'],
                                              'inheritFrom',
                                              attr, view)[0]
    return res

def getRepresentation(view, items,itemValues):
    """Return string representation for reported item's essentials.
    
    view - current view
    items - current collection
    itemValues - a dictionary with item's values from repository
    
    Note: Using locals() in the implementation
    
    Concatenate information on name, stamps, deletion and details of an item.
    Return string representation of the information.
    
    """
    if itemValues is None:
        return "None"
    name = getRecurAttr(items, itemValues, 'displayName')
    stamps = itemValues.get('osaf.pim.Stamp.stamp_types', '')
    if stamps != '':
       stamps = ", ".join(stamp.__name__ for stamp in stamps)
    if 'deleted' in itemValues:
       displaysource = _(u"deleted or transferred")
       displaydate = getShortDateTimeFromEpoch(view, itemValues['deleted'])
    else:
       displaydate = shortDateTimeFormat.format(view,
                                                itemValues['displayDate'])
       displaysource = itemValues['displayDateSource']
    details = itemValues.get('details', '')
    return item_template % locals()

def getDetailsRepresentation(history, before_dates):
    """ Return representation of details on triage statuses that changed.
   
    history - dictionary of item values by versions
    before_dates - list of the dates of interest in history
    
    Since the earliest date in before_dates, iterate versions of item in 
    history and add information about every change of triage status. Include
    the new triage status and the time of commit of the changes. Triage
    statuses that remained the same from version to version are reported
    only the first time.
    
    If before_dates is empty, return empty string.
    Return string representation of status change history.
    """
    
    statuses = [then for then in before_dates if
                               '_triageStatus' in history[then]]
    if len(statuses)>0:
        statuses.sort(reverse=True)
        changes = []
        status = statuses.pop()
        prevStatus = history[status]
        changes.append(status)
        while len(statuses) > 0:
            status = statuses.pop()
            if (prevStatus['_triageStatus'] != history[status]['_triageStatus']):
                changes.append(status)
            prevStatus = history[status] 
   
        details = []

        for then in changes:
            status = history[then]['_triageStatus']
            details.append(getTriageStatusName(status) 
                           + " " + time.strftime("%d-%b-%y,%H:%M:%S", 
                                                 time.localtime(then)))
        values = {}
        values['details'] = ",\n".join(details) 
        representation = details_template % values
    else:
        representation = ""          
    return representation + "\n"


#######parsing######################
def getLastReport(itemsToReport):
    """ Return the datetime of the latest report item in current collection.
    
    itemsToReport -- current collection of items
    
    Not implemented: retrieving reports on the given collection that are
    located outside itemsToReport is not supported. Collection attribute 
    in ReportStamp is needed.
    
    DateTime is retrieved from the latest report's 'until' attribute
    
    Return a datetime of the latest report that was not:
     - deleted
     - transferred from the given collection
     - unstamped
    Return None if:
    -there is no such report
    -all the reports were deleted
    -all the reports were transferred from this collection 
    -no reports ever existed 
    """
    last = None
    reports = [ReportStamp(item) for item in itemsToReport 
                        if has_stamp(item, ReportStamp)]
    if (len(reports)>0):
        lastReport = max(reports, key=lambda item: item.until)
        last = lastReport.until
        
    return last

def parseDuration(duration, until):
    """ Return datetime of report period start time from the given command.
    
    duration - string that starts with 'days=n', or 'weeks=n', 
    or 'hours=n'
    until - Datetime of the end time of report
    
    If duration is not one of the expected patterns,
    return default of startTime until - one week. Otherwise return
    until - delta (as given by weeks, days or hours)
    
    Return DateTime of start time for the intended report 
   
    """
    #default is 7 days delta
    units = 7
    delta = timedelta(days=units)
    days = re.compile('^days=(\d*)')
    weeks = re.compile('^weeks=(\d*)')
    hours = re.compile('^hours=(\d*)')
    patterns = [days, weeks, hours]
    
    if duration is not None:
        for pattern in patterns:
            if (pattern.search(duration) is not None):
                units = int(pattern.search(duration).groups()[0])
                if (pattern == days):
                    delta = timedelta(days=units)
                elif (pattern == weeks):
                    delta = timedelta(weeks=units)
                elif (pattern == hours):
                    delta = timedelta(hours=units)
    since = until - delta    
    return since

def parseTime(itemsToReport, command, startTime, endTime):
    """ Return start time adn end time of report period from user command
    
    itemsToReport -- current collection for report
    command -- string of the given report command
    startTime -- explicit start time of report period
    endTime -- explicit end time of report period (default: datetime.now)
    
    command may include:
    "last" or "latest" -- report on what happened since the latest report in
                         the collection until current time
    "last" time        -- report on 'last report's until' until time
    "days=x"           -- report on 'x days ago' until current time
    "hours=x"          -- report on 'x hours ago' until current time
    "weeks=x"          -- report on 'x weeks ago' until current time
    startTime-endTime  -- report on startTime until endTime
    None of the above  -- default: report on 'one week ago' until current time
    
    Raise ValueError if given endTime is earlier than startTime
    Return tuple (DateTime, DateTime) of start time and end time
    of the intended report period
    
    """
    #set defaults - from one week ago until now
    now = datetime.now(ICUtzinfo.default)
    until = now
    since = until - timedelta(days=7)
  
    if (startTime is None):
        since = parseDuration(command,until)
    if (startTime is not None):
        since = startTime
    if (endTime is not None):
        until = endTime
    if (command == "last" or command == "latest"):
        
        latest = getLastReport(itemsToReport)
        #if the latest report is None then the default rules are valid
        if latest is not None: 
            # if only some date is mentioned
            if (startTime is not None and endTime is None): 
                until = since
            else:
                until = now
            since = latest
    
    if since>until:
        raise ValueError, "End time must not be earlier than start time"
    
    return (since, until)

#######getting reports######################

def getChangedItems(itemsToReport, until, since, triageStatus, changed=True):
    """Return list of items that are candidates for reporting.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    triageStatus -- expected current triage status to be included
    changed -- flag for change of triage status (default: True)
              if True: return items that their triage status changed
              after since 
              if False: return items that their triage status did not
              change after since
   
    Filters the given collection and return only the items that may be 
    reported. This method is useful for pre-filtering to improve efficiency
    and spare redundant versions tracking in the repository. Only items that
    were created before until are included.
    
    Return list of items that are candidates for reporting. 
      
    """
    epoch_time = getEpochTime(since)
    basicFilter = [item for item in itemsToReport if
                     item.triageStatus == triageStatus and
                     item.createdOn < until]
    changeFilter = []
    if changed:
        changeFilter =  [item for item in basicFilter if
                          item._triageStatusChanged is not None and
                          -item._triageStatusChanged > epoch_time]
    else:
        changeFilter = [item for item in basicFilter if
                        item.createdOn < since]

    return changeFilter

def hasChangedFromStartToEnd(itemsToReport, item, until, since, 
                             expectedTS, oldTS, historyView=None):
    """Return list of items' values dictionaries for candidates for reporting.
    
    itemsToReport -- current collection
    item -- current item
    until -- end time of report period
    since -- start time of report period
    expectedTS -- expected triageStatus in latest version of item before until
    oldTS -- a list of possible previous triageStatus for versions at the 
             time of since
    historyView -- optional (default: None). DBRepositoryView for reusal in
                   when extracting historic information on older versions
    
    Assumption: if there is no explicit triage attribute in repository.
    we assume that the initial triage status is TriageEnum.now
    
    Return tuple (Boolean, dictionary of item values). 
    True for item that had one of triage statuses in OldTS at version 
    committed at since, and that has expectedTS at version committed at 
    until.
      
    """
    epoch_time = getEpochTime(since)
    created_epoch = getEpochTime(item.createdOn)
    values = getItemValues(item)
    history = History.getItemHistorySince(item.itsUUID, 
                                          itemsToReport, 
                                          created_epoch, historyView)
    changed = -item._triageStatusChanged
    startItem = None
    thenDate = None
    result = False
    beforeDates = []
    # new items
    if item.createdOn >= since:
       
        before_dates = [then for then in history.keys() if 
                        time.localtime(then) >= time.localtime(created_epoch)]
        
        if len(before_dates) > 0:
            thenDate = min(before_dates)
            startItem = history[thenDate]
            
    # old items
    else:
        before_dates = [then for then in history.keys() if
                        time.localtime(then) <= time.localtime(epoch_time) and
                        time.localtime(then) >= time.localtime(created_epoch)]
        if len(before_dates) > 0:
            thenDate = max(before_dates)
            startItem = history[thenDate]
        # not commited to the repository in a timely manner, but an old item
        else:
            before_dates = [then for then in history.keys() if
                            time.localtime(then) >= time.localtime(created_epoch)]
        # get the first available commit
        if len(before_dates) > 0:
            thenDate = min(before_dates)
            startItem = history[thenDate]
    values['details'] = getDetailsRepresentation(history, before_dates)
    if (startItem is not None and '_triageStatus' in startItem and 
        startItem['_triageStatus'] in oldTS):
        result = True 
    # Handling the items with no explicit triage status
    elif (startItem is not None and '_triageStatus' not in startItem):
        # in the case of startTimeKey presence, the first
        # existing triage status will be checked, otherwise
        # NOW is assumed to be the initial status
         startTimeKey = 'osaf.pim.calendar.EventStamp.startTime'
         if (startTimeKey in startItem):
             triage_dates = [then for then in history.keys() if
                            '_triageStatus' in history[then] and
                            time.localtime(then) >= time.localtime(created_epoch)]
             earlyItem = None
             if len(triage_dates)>0:
                 triage_dates.sort(reverse=True)
                 earlyStatus = triage_dates.pop()
                 earlyItem = history[earlyStatus]
             else:
                 if TriageEnum.now in oldTS:
                     result = True
             if (earlyItem and startTimeKey in earlyItem and 
                 earlyItem['_triageStatus'] in oldTS):
                result = True
          # if not event with start time assume initial triage status is NOW
         elif TriageEnum.now in oldTS:
             result = True
    return (result, values)
def getNewArrivals(itemsToReport,until,since):
    """Return sorted list of items' values dictionaries for new arrivals.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    
    New Arrivals are:
    Items that were created after since and before until. Including items
    that were DELETED after creation.
    
    Note: Occurrences of recurring event that was created before since
    are NOT defined as new 
    
    Return list (sorted by displayed date from earliest to latest) of 
    item values, for new arrival items.
      
    """
    filteredList = [getItemValues(item) for item in itemsToReport 
                         if item.createdOn > since and item.createdOn < until]
    historyView = History.makeView(itemsToReport)
    deletedItems = History.getDeletedItems(itemsToReport, historyView)
    for itemValues in deletedItems:
        if (getRecurAttr(itemsToReport, itemValues, 
                         'createdOn', historyView) > since and 
            getRecurAttr(itemsToReport, itemValues, 
                         'createdOn', historyView) < until):
                filteredList.append(itemValues)
    History.cleanupView(historyView)
    return sorted(filteredList, 
                  key=lambda itemValues: itemValues['displayDate'])

def getAchievements(itemsToReport,until,since):
    """Return sorted list of items' values dictionaries for achievements.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    
    Achievements are:
    Items that were created before until
    New items in the status of DONE that were not created as DONE
    Old items that changed their status to DONE  during the reported
    period, but were in another status at the time of since.
    
    Return list (sorted by date of displayDate from earliest to latest) of 
    item values items that are defined as achievements.
      
    """
    doneItems = getChangedItems(itemsToReport,until,since,TriageEnum.done)
    filteredList = []
    startTSList = [TriageEnum.now, TriageEnum.later, None]
    # reusing the view
    historyView = History.makeView(itemsToReport)
    for itemValues in doneItems:
        toReport, values = hasChangedFromStartToEnd(itemsToReport, 
                                                    itemValues, until, 
                                                    since, TriageEnum.done, 
                                                    startTSList, historyView)
        if toReport:
            filteredList.append(values)
    History.cleanupView(historyView)
    return sorted(filteredList, 
                  key=lambda itemValues: itemValues['_triageStatusChanged'])

def getTransitionOfFocus(itemsToReport, until, since, direction="in"):
    """Return sorted list of items' values dict. for items with focus changed.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    direction -- optional (default: "in"), indication of transition, 'in'
                 or 'out'
    
    Items with transition of focus IN:
    LATER (at since) ---> NOW (at until)
    Items with transition of focus OUT:
    NOW (at since) ---> LATER (at until)
    
    Not implemented:
    NOW (at since) ---> DELETED (at until)

    Return list (sorted by date of triage change from earliest to latest) of 
    item values for items that their focus was changed, for given direction.
      
    """
    triageStatus = TriageEnum.now
    startTSList = [TriageEnum.later, TriageEnum.done, None]
    if (direction == "out"):
        triageStatus = TriageEnum.later
        startTSList = [TriageEnum.now]
    
    filteredList = []
    
    focusItems = getChangedItems(itemsToReport, until, since, triageStatus, 
                                 changed=True)
    historyView = History.makeView(itemsToReport)
    for item in focusItems:
        toReport, values = hasChangedFromStartToEnd(itemsToReport, item, 
                                                    until, since, 
                                                    triageStatus, 
                                                    startTSList, historyView)
        if toReport:
            filteredList.append(values)
    History.cleanupView(historyView)
    return sorted(filteredList, 
                  key=lambda itemValues: itemValues['_triageStatusChanged'])

def getPersistentItems(itemsToReport,until,since,triageStatus):
    """Return sorted list of items' values dict. for persistent items.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    triageStatus -- the triage status that is not changing
  
    Persistent items with triageStatus=TriageEnum.now:
    NOW (at since) ---> NOW (at until)
    
    Note: New items are NOT reported as persistent.
    
    Return list (sorted by date of triage changes from earliest to latest) of 
    item values for items that keep the same triage status from before since.
      
    """
    epoch_time = getEpochTime(since)
   
    filteredList = []
    startTSList = [triageStatus]
    persistentItems = getChangedItems(itemsToReport, until, since, 
                                      triageStatus, changed=False)
    historyView = History.makeView(itemsToReport)
   
    for item in persistentItems:
        toReport, values = hasChangedFromStartToEnd(itemsToReport, item, 
                                                    until, since, 
                                                    triageStatus, 
                                                    startTSList, historyView)
        # never changed, or changed before since
        if (item._triageStatusChanged is None or 
            -item._triageStatusChanged < epoch_time):
            prefix = "Details:\ntriage changed before "
            view = item.itsView 
            values['details'] = prefix + shortDateTimeFormat.format(view,
                                                                    since)
            filteredList.append(values)
        # changed but maybe is persistent
        elif toReport:
            filteredList.append(values)
    History.cleanupView(historyView)
    return sorted(filteredList, 
                  key=lambda itemValues: itemValues['displayDate'])

def getUpdatedItems(itemsToReport,until,since):
    """ Return list of items values of items that their body was changed.
    
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    
    Updated Items:
    items created before until
    item (at since) ----> item body text changed ----> item (at until)
    
    Notes: 
    Differs from other reporting procedures, because reports on
    any change during the given period, and not on the change between 
    the start and the end point
    Modification by users other than the owner are NOT considered
    updates for owner's report.
    New items are not included!
    
    Known issue: If the user has deleted one of the accounts his items 
    updated long ago, will not be recognized as modified by him
    Not implemented: fix by finding out the old MeEmail info in repository 
    
    Return list (sorted by displayDate from earliest to latest) of 
    item values for items that were updated (worked on) during report
    period (since - until).
   
    """
    epoch_time = getEpochTime(since)
    filteredList = []
    historyView = History.makeView(itemsToReport)
   
    updatedItems = [item for item in itemsToReport if
                        item.lastModification is not None and
                        item.lastModified is not None and
                        item.lastModified >= since and
                        item.lastModification != Modification.created and
                        item.createdOn <= until]
    
    for item in updatedItems:
        values = getItemValues(item)
        history = History.getItemHistorySince(item.itsUUID, 
                                              itemsToReport, 
                                              epoch_time, historyView)
        # check the e-mail addresses currently associated with the user
        addresses = mail.getCurrentMeEmailAddresses(itemsToReport.itsView)
        addresses_str = [add.emailAddress for add in addresses 
                         if hasattr(add, 'emailAddress')]    
        modifiedByMe = True
        
        before_dates = [then for then in history.keys() if
                        time.localtime(then) >= time.localtime(epoch_time)]
        
        if len(before_dates)>0:
            maxItem = before_dates.pop(before_dates.index(max(before_dates)))
            oldItem = history[maxItem]
            oldModified = History.getItemFeatureByVersion(itemsToReport, 
                                                          oldItem['version'], 
                                                          item.itsUUID, 
                                                          'lastModifiedBy', 
                                                          'emailAddress')
                                                          
            if oldModified is not None:
                values['details'] = "Modified by: " + oldModified[0]
            while oldItem is not None and oldItem['exists']==True:
                if (oldModified is not None and 
                    oldModified not in addresses_str):
                    modifiedByMe = False
                else:
                    modifiedByMe = True
                if ('body' in oldItem and 
                    oldItem['body'] != item.body and 
                    modifiedByMe):
                    filteredList.append(values)
                    oldItem = None
                elif (('body' not in oldItem or oldItem['body'] is None) and 
                      item.body != "" and modifiedByMe):
                    filteredList.append(values)
                    oldItem = None
                elif len(before_dates) > 0:
                    maxIndex = before_dates.index(max(before_dates))
                    maxItem = before_dates.pop(maxIndex)
                    oldItem = history[maxItem]
                elif len(before_dates) == 0:
                    oldItem = None
    History.cleanupView(historyView)
    return sorted(filteredList, 
                  key=lambda itemValues: itemValues['displayDate'])

"""Template for single section representation in report"""
section_template = _(u"""\
%(title)s - %(total)d items:
---------------------------------
%(items)s""")

"""Template for report's body representation"""
report_template =  _(u"""\
Report %(from)s - %(until)s

%(entered)s

%(achievements)s

%(out)s

%(into)s

%(snow)s

%(slater)s

%(updated)s
""")


section_definitions = {#function,           #title,                #extra args
    'achievements' : [getAchievements,      _(u"Achievements")],
    'entered' :      [getNewArrivals,       _(u"Newly Received")],
    'out' :          [getTransitionOfFocus, _(u"Focus Transition Out"), "out"],
    'into'   :       [getTransitionOfFocus, _(u"Focus Transition In"),  "in"],
    'updated' :      [getUpdatedItems,      _(u"Worked On")], 
    'snow'   :       [getPersistentItems,   _(u"Persistent Items (NOW)"),  
                      TriageEnum.now],
    'slater' :       [getPersistentItems,   _(u"Persistent Items (LATER)"),   
                      TriageEnum.later]   
}

def getReport(view, itemsToReport, since, until):
    """Main method. Return a string with a report for collection itemsToReport.
    
    view -- MainView
    itemsToReport -- current collection
    until -- end time of report period
    since -- start time of report period
    
    Not implemented: full support for end time until. Currently only
    the check for items created before until exists.
    
    Call the functions to retrieve information needed for each of the 5
    sections in report. Return string with full text for report for period
    since - until.
    
    """
   
    sectionDict = {'from' : shortDateTimeFormat.format(view,since),
                   'until' : shortDateTimeFormat.format(view,until)}
    for key, data in section_definitions.iteritems():
        function, title = data[:2]
        args = data[2:]
        section_items = function(itemsToReport, until, since, *args)
        items_text = "\n".join(getRepresentation(view, itemsToReport,item) 
                               for item in section_items)
        sectionDict[key] = section_template % {'title' : title,
                                               'items' : items_text,
                                               'total' : len(section_items)}

    output =  report_template % sectionDict
    return output
