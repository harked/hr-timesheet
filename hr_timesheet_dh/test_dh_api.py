#!/usr/bin/env python

import xmlrpclib

url = "http://localhost:8069"
db = "stclaus_1"
username = "admin"
password = "admin"

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
print common.version()

uid = common.authenticate(db, username, password, {})
print uid

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=True)
print models.execute_kw(db, uid, password,
                  'hr_timesheet_sheet.sheet', 'attendance_analysis', [], dict(employee_id= 1, month=5, year=2015))