# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime, format_date)
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates, get_end_date
import datetime as dt

def execute(filters=None):
    data = []
    columns = get_columns()
    employee = get_details(filters)
    for emp in employee:
        data.append(emp)
        dep = []
        st = []
        for d in data:
            p = [d[0]]
            s = [d[1]]
            dep.append(p)
            st.append(s)
            chart = {
            'data':{
                'labels':dep,
                'datasets':[
                    {'values':st},
                    # {'values':st}
                ]
            },
            'type':'bar',
            'height':40,
            'colors':['#52BD52'], 
            }
        return columns, data, None, chart

def get_columns():
	columns = [
		_("Department") + ":Data:150",
		_("Status") + ":Select:150",
		_("Date of Joining") + ":Data:200",   
	]
	return columns

def get_details(filters):
	data = []
	employee = frappe.db.sql("""select count(status) as status,department,date_of_joining,company from `tabEmployee` where status in('Active','Left') group by status,department""",as_dict=1)
	for emp in employee:
		date = emp.date_of_joining
		date_y = emp.date_of_joining
		dm = date.month
		dy =date_y.year
		if filters.month == str(dm) and filters.year == str(dy): 
			row = [emp.department,emp.status,emp.date_of_joining]    
			data.append(row)
	return data
