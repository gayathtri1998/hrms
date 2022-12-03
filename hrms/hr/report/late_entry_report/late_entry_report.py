# Copyright (c) 2013, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count






def execute(filters=None):
    data = []
    columns = get_columns()
    attendance = get_attendance(filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        _("Attendance Date") + ":Data:120",
        _("Shift") + ":Data:100",
        _("Shift Start Time") + ":Data:120",
        _("In Time") + ":Data:170",
    ]
    return columns

def get_attendance(filters):
    data = []
    attendance = frappe.db.sql("""select * from `tabAttendance` where status = 'Present' and docstatus !=2 """,as_dict=1)
    for att in attendance:
        frappe.errprint(att.in_)
        if att.shift and att.in_:
            shift_start_time = frappe.db.get_value("Shift Type",att.shift,"start_time")
            str_time= datetime.strptime(str(shift_start_time),'%H:%M:%S').time()
            in_time = datetime.strptime(str(att.in_),'%H:%M:%S').time()
            if in_time > str_time:
                row = [att.employee,att.employee_name,format_date(att.attendance_date),att.shift,shift_start_time,in_time]
                data.append(row)
    return data



