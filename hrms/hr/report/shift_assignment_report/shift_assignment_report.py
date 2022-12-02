# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.utils import formatdate


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Employee ID") + ":Data/:150",_("Employee Name") + ":Data/:200",_("Department") + ":Data/:150",_("Employee Type") + ":Data/:150",_("Shift Type") + ":Data/:100",_("Shift Date") + ":Data/:150",_("Document Status") + ":Data/:200"
	]
	return columns

def get_data(filters):
	data = []
	docstatus = ''
	if filters.employee:
		shifts = frappe.db.sql("""select * from `tabShift Assignment` where start_date between '%s' and '%s' and employee = '%s' and docstatus != '2' """%(filters.from_date,filters.to_date,filters.employee),as_dict=True)
		for s in shifts:
			if s.docstatus == 1:
				docstatus = 'Submitted'
			elif s.docstatus == 0:
				docstatus = 'Draft'
			data.append([s.employee,s.employee_name,s.department,s.employee_type,s.shift_type,formatdate(s.start_date),docstatus])
	elif filters.department:
		shifts = frappe.db.sql("""select * from `tabShift Assignment` where start_date between '%s' and '%s' and department = '%s' and docstatus != '2' """%(filters.from_date,filters.to_date,filters.department),as_dict=True)
		for s in shifts:
			if s.docstatus == 1:
				docstatus = 'Submitted'
			elif s.docstatus == 0:
				docstatus = 'Draft'
			data.append([s.employee,s.employee_name,s.department,s.employee_type,s.shift_type,formatdate(s.start_date),docstatus])	
	else:
		shifts = frappe.db.sql("""select * from `tabShift Assignment` where start_date between '%s' and '%s' and docstatus != '2' """%(filters.from_date,filters.to_date),as_dict=True)
		for s in shifts:
			if s.docstatus == 1:
				docstatus = 'Submitted'
			elif s.docstatus == 0:
				docstatus = 'Draft'
			data.append([s.employee,s.employee_name,s.department,s.employee_type,s.shift_type,formatdate(s.start_date),docstatus])
	return data