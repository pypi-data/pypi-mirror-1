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

from setuptools import setup

setup(
    name = "Chandler-ReportPlugin",
    version = "0.1",
    description = "Progress reports for Chandler",
    author = "Vera Sheinman",
    author_email = "vera46@gmail.com",
    test_suite = "reports.tests",
    packages = ["reports"],
    include_package_data = True,
    entry_points = {
        "chandler.parcels": ["Report API = reports"],
        "chandler.quick_entry": ['report = reports.reportsentry_commands:ReportCommand']
    },
    classifiers = ["Development Status :: 3 - Alpha",
                   "Environment :: Plugins",
                   "Framework :: Chandler",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache Software License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Office/Business :: Groupware"],
    long_description = open('README.txt').read(),
)