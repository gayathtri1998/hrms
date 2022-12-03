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
        _("Shift End Time") + ":Data:120",
        _("Out Time") + ":Data:170",
    ]
    return columns

def get_attendance(filters):
    data = []
    attendance = frappe.db.sql("""select * from `tabAttendance` where status = 'Present' """,as_dict=1)
    # attendance = frappe.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date))},['*'])
    late_by = ''
    for att in attendance:
        # frappe.errprint(type(att.out_))
        if att.shift and att.out_:
            shift_end_time = frappe.db.get_value("Shift Type",att.shift,"end_time")
            str_time= datetime.strptime(str(shift_end_time),'%H:%M:%S').time()
            out_time = datetime.strptime(str(att.out_),'%H:%M:%S').time()
            # frappe.errprint((out_time) < str_time)
            if out_time < str_time:
                frappe.errprint("hi")
                row = [att.employee,att.employee_name,format_date(att.attendance_date),att.shift,shift_end_time,out_time]
                data.append(row)
    return data



