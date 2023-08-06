#!/usr/bin/env python

__rev_id__ = """$Id: __init__.py 21 2009-09-24 16:00:34Z chalkdust1011 $"""

import sys
if sys.version_info[:2] < (2, 4):
    print >>sys.stderr, "Sorry, django-excel-templates requires Python 2.4 or later"
    sys.exit(1)

from ExcelReports import *

