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

from application import schema
from osaf.pim import Stamp, Note
from osaf.pim.calendar import DateTimeUtil

""" Provide a class for stamping an item as report."""
class ReportStamp(Stamp):
    """ Report stamp with a single attribute until (datetime)."""
    
    schema.kindInfo(annotates = Note)
    
    __use_collection__ = True
    # an attribute of until date of a report
    until = schema.One(schema.DateTimeTZ, indexed=True)
    
    def __str__(self):
        untilStr = DateTimeUtil.shortDateTimeFormat.format(until)
        return '<Report until %s>' % untilStr
    