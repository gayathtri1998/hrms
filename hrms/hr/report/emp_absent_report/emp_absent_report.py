# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count


def execute(filters=None):
	columns = get_columns()
	data = []
	row = []
	attendance = get_attendance(filters)
	for att in attendance:
		data.append(att)
	return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Link/Employee:150",
        _("Employee Name") + ":Data:180",
        _("Department") + ":Data:180",
        _("Status") + ":Data:180"
        
    
	]
        
    return columns

def get_attendance(filters):
    row = []
    attendance = frappe.db.sql("""Select * From `tabAttendance` Where status in ('Absent','On Leave') and attendance_date between '%s' and '%s and %s order by employee'"""% (filters.from_date,filters.to_date,filters.employee), as_dict=1)
    if not filters.employee:
        employee = frappe.get_all("Employee",{'status':'Active'},['*'])
    else:
        employee = frappe.get_all("Employee",{'employee':filters.employee,'status':'Active'},['*'])
    for emp in employee:
        att_date = []
        for att in attendance:
            if emp.name == att.employee:
                att_date += [att.attendance_date.strftime("%d-%m-%Y")]
                att_list = (','.join(att_date))
        count = len(att_date)
        if count:
            row += [(emp.name,emp.employee_name,emp.department,att_list,count)]
    return row		
