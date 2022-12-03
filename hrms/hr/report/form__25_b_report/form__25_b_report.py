# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from doctest import SKIP
from lzma import FORMAT_RAW
from unittest import skipUnless
import frappe
from frappe.utils import cstr, cint, getdate,add_days
import datetime
from datetime import date, datetime
from frappe import msgprint, _
from calendar import monthrange
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates, get_end_date



status_map = {
	"A": "A",
	"H": "HD",
	"Holiday": "H",
	"Weekly Off": "WO",
	"On Leave": "L",
	"Present": "P",
	"Work From Home": "WFH",
	"1":"1",
	"2":"2",
	"3":"3",
	"E": "EL",
	"C": "CL",
	"S": "SL",
	"O": "OD",
	"P": "PL",
	"L": "LWP",
	"M": "ML",
	"Compensatory Off": "CO",
  
	"":"A",
  
	}

day_abbr = [
	"Mon",
	"Tue",
	"Wed",
	"Thu",
	"Fri",
	"Sat",
	"Sun"
]
def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns, days = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	if not att_map:
		return columns, [], None, None
	if filters.group_by:
		emp_map, group_by_parameters = get_employee_details(filters.group_by, filters.company)
		holiday_list = []
		for parameter in group_by_parameters:
			h_list = [emp_map[parameter][d]["holiday_list"] for d in emp_map[parameter] if emp_map[parameter][d]["holiday_list"]]
			holiday_list += h_list
	else:
		emp_map = get_employee_details(filters.group_by, filters.company)
		holiday_list = [emp_map[d]["holiday_list"] for d in emp_map if emp_map[d]["holiday_list"]]


	default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
	holiday_list.append(default_holiday_list)
	holiday_list = list(set(holiday_list))
	holiday_map = get_holiday(holiday_list, filters["month"],filters["year"])

	data = []

	leave_list = None
	leave_list = None
	if not filters.summarized_view:
		leave_types = frappe.db.sql("""select name from `tabLeave Type`""", as_list=True)
		leave_list = [d[0] + ":Float:120" for d in leave_types]
		l_list = [d[0] for d in leave_types]
		columns.extend(leave_list)

	if filters.group_by:
		emp_att_map = {}
		for parameter in group_by_parameters:
			emp_map_set = set([key for key in emp_map[parameter].keys()])
			att_map_set = set([key for key in att_map.keys()])
			if (att_map_set & emp_map_set):
				parameter_row = ["<b>"+ parameter + "</b>"] + ['' for day in range(filters["total_days_in_month"] + 2)]
				data.append(parameter_row)
				record, emp_att_data = add_data(emp_map[parameter], att_map, filters, holiday_map, conditions, default_holiday_list, leave_list=l_list)
				emp_att_map.update(emp_att_data)
				data += record
				
	else:
		record, emp_att_map = add_data(emp_map, att_map, filters, holiday_map, conditions, default_holiday_list, leave_list=l_list)
		data += record

	chart_data = get_chart_data(emp_att_map, days)

	return columns, data, None, chart_data
def get_chart_data(emp_att_map, days):
	labels = []
	datasets = [
		{"name": "Absent", "values": []},
		{"name": "Present", "values": []},
		{"name": "Leave", "values": []},
	]
	for idx, day in enumerate(days, start=0):
		p = day.replace("::65", "")
		labels.append(day.replace("::65", ""))
		total_absent_on_day = 0
		total_leave_on_day = 0
		total_present_on_day = 0
		total_holiday = 0
		for emp in emp_att_map.keys():
			if emp_att_map[emp][idx]:
				if emp_att_map[emp][idx] == "A":
					total_absent_on_day += 1
				if emp_att_map[emp][idx] in ["1", "2","3"]:
					total_present_on_day += 1
				if emp_att_map[emp][idx] == "HD":
					total_present_on_day += 0.5
					total_leave_on_day += 0.5
				if emp_att_map[emp][idx] == "L":
					total_leave_on_day += 1


		datasets[0]["values"].append(total_absent_on_day)
		datasets[1]["values"].append(total_present_on_day)
		datasets[2]["values"].append(total_leave_on_day)


	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	chart["type"] = "line"

	return chart
def add_data(employee_map, att_map, filters, holiday_map, conditions, default_holiday_list, leave_list=None):

	record = []
	emp_att_map = {}
	for emp in employee_map:
		emp_det = employee_map.get(emp)
		if not emp_det or emp not in att_map:
			continue

		row = []
		if filters.group_by:
			row += [" "]
		row += [emp, emp_det.employee_name,emp_det.department,emp_det.designation,emp_det.date_of_birth,emp_det.date_of_joining,emp_det.branch,emp_det.grade]

		total_p = total_a = total_l = total_w = total_h = total_um= total_1 = total_2 = total_3 = total_e = total_c = total_12 = total_hh = total_m = total_ll = total_s = total_pp = total_23 = total_31 = total_123 = total_231 = total_312 = total_od = 0.0
		emp_status_map = []
		emp_attt_map =[]
		for day in range(filters["total_days_in_month"]):
			status = None
			status = att_map.get(emp).get(day + 1)
			from_date = str(filters.year) + "-" + str(filters.month)+ "-" + str(day+1)
			from_date = datetime.strptime(from_date, "%Y-%m-%d")
			doj = frappe.db.get_value("Employee",emp,'date_of_joining')
			status = None
			emp_holiday_list = emp_det.holiday_list if emp_det.holiday_list else default_holiday_list
			holiday = check_holiday(emp_holiday_list,from_date)
			if holiday:
				status = holiday
				total_h += 1
				if total_h > 4:
					total_w = 4
				else:
					total_h += 1
			elif att_map:
				att = att_map.get(emp).get(day + 1) 
				if att:
					try:
						status = att[0]
					except KeyError:
						status = None
									

									
			att = att_map.get(emp).get(day + 1)            
			abbr = status_map.get(status, "")
			emp_status_map.append(abbr)
			frappe.errprint(status)

			if not filters.summarized_view:
				if status == "Present" or status == "Work From Home":
					total_p += 1
				elif status == "A":
					total_a += 1
				elif status == "1":
					total_p += 1
					total_1 += 1
				elif status == "2":
					total_p += 1
					total_2 += 1
				elif status == "3":
					total_p += 1
					total_3 += 1
				elif status == "On Leave":
					total_l += 1
					total_p += 1
				elif status == "E":
					total_e += 1
					total_p += 1
				elif status == "C":
					total_c += 1
					total_p += 1
				elif status == "S":
					total_s += 1
					total_p += 1
				elif status == "P":
					total_pp += 1
					total_p += 1
				elif status == "L":
					total_ll += 1
					total_p += 1
				elif status == "M":
					total_m += 1
					total_p += 1
					
				elif status == "H":
					total_hh += 0.5
					total_a += 0.5
					total_l += 0.5
					
				elif status == 'O':
					total_od += 1
				elif not status:
					total_um += 1

		if not filters.summarized_view:
			row += emp_status_map

		if not filters.summarized_view:
			row += emp_status_map

		if not filters.summarized_view:
			
			dates = get_start_end_dates('Monthly', filters.month)
			shift_1 = (total_1 + total_12 + total_123) * 30
			shift_2 = (total_2 + total_23 + total_231) * 30
			shift_3 = (total_3 + total_31 + total_312) * 50
			row += [total_1,total_2,total_3,total_od,total_p, total_a,total_w ,total_h,total_um]
			overtime = frappe.db.sql(""" select sum(total_hours) as total_hours from `tabTimesheet` where start_date between '%s'and '%s' and employee = '%s' """ % (dates.start_date,dates.end_date,emp), as_dict=True) or 0
			if overtime:
				row.extend([overtime[0]["total_hours"]])
		if not filters.get("employee"):
			filters.update({"employee": emp})
			conditions += " and employee = %(employee)s"
		elif not filters.get("employee") == emp:
			filters.update({"employee": emp})

		if not filters.summarized_view:
			leave_details = frappe.db.sql("""select leave_type, status, count(*) as count from `tabAttendance`\
				where leave_type is not NULL %s group by leave_type, status""" % conditions, filters, as_dict=1)

			time_default_counts = frappe.db.sql("""select (select count(*) from `tabAttendance` where \
				late_entry = 1 %s) as late_entry_count, (select count(*) from tabAttendance where \
				early_exit = 1 %s) as early_exit_count""" % (conditions, conditions), filters)

			leaves = {}
			for d in leave_details:
				if d.status == "Half Day":
					d.count = d.count * 0.5
				if d.leave_type in leaves:
					leaves[d.leave_type] += d.count
				else:
					leaves[d.leave_type] = d.count
			for d in leave_list:
				if d in leaves:
					row.append(leaves[d])
				else:
					row.append("0.0")

			
		emp_att_map[emp] = emp_status_map
		record.append(row)

	return record, emp_att_map

def get_columns(filters):

	columns = []

	if filters.group_by:
		columns = [_(filters.group_by)+ ":Link/Branch:120"]

	columns += [
		_("Employee") + ":Link/Employee:120", _("Employee Name") + ":Data/:120", _("Department") + ":Data/:120", _("Designation") + ":Data/:120", _("DOB") + ":Date/:120", _("DOJ") + ":date/:120", _("Location") + ":Data/:120", _("Grade") + ":Data/:120"
	]
	days = []
	for day in range(filters["total_days_in_month"]):
		date = str(filters.year) + "-" + str(filters.month)+ "-" + str(day+1)
		day_name = day_abbr[getdate(date).weekday()]
		days.append(cstr(day+1)+ " " +day_name +"::65")
	if not filters.summarized_view:
		columns += days

	if not filters.summarized_view:
		columns += [_("1st Shift") + ":Float:120",_("2nd Shift") + ":Float:120",_("3rd Shift") + ":Float:120",_("On Duty") + ":Float:120",_("Total Present") + ":Float:120", _("Total Absent") + ":Float:120", _("Total Week Off") + ":Float:120", _("Total Holidays") + ":Float:120", _("Unmarked Days")+ ":Float:120",_("Overtime")+ ":Data:120"]
	frappe.errprint(days)
	return columns, days

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select employee, day(attendance_date) as day_of_month,
		status,shift,attendance_request,leave_type from tabAttendance where docstatus in (0,1) %s order by employee, attendance_date""" %
		conditions, filters, as_dict=1)

	if not attendance_list:
		msgprint(_("No attendance record found"), alert=True, indicator="orange")

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month,"")
		
		if d.shift:
			att_map[d.employee][d.day_of_month] = d.shift
		if d.status == 'On Leave':
			att_map[d.employee][d.day_of_month] = d.leave_type
		if d.attendance_request:
			att_map[d.employee][d.day_of_month] = "On Duty"
		if d.status in ["Absent","Work From Home","Half Day"]:
			att_map[d.employee][d.day_of_month] = d.status

	return att_map

def get_conditions(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

	conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	

	return conditions, filters

def get_employee_details(group_by, company):
	emp_map = {}
	query = """select name, employee_name, designation, date_of_birth, date_of_joining, grade, department, branch, company, 
		holiday_list from `tabEmployee` where company = %s and status = "Active" """ % frappe.db.escape(company)

	if group_by:
		group_by = group_by.lower()
		query += " order by " + group_by + " ASC"

	employee_details = frappe.db.sql(query , as_dict=1)

	group_by_parameters = []
	if group_by:

		group_by_parameters = list(set(detail.get(group_by, "") for detail in employee_details if detail.get(group_by, "")))
		for parameter in group_by_parameters:
				emp_map[parameter] = {}


	for d in employee_details:
		if group_by and len(group_by_parameters):
			if d.get(group_by, None):

				emp_map[d.get(group_by)][d.name] = d
		else:
			emp_map[d.name] = d

	if not group_by:
		return emp_map
	else:
		return emp_map, group_by_parameters

def get_holiday(holiday_list, month,year):
	
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql('''select day(holiday_date), weekly_off from `tabHoliday`
				where parent=%s and month(holiday_date)=%s and year(holiday_date)=%s''', (d, month,year)))
	return holiday_map

@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)

def check_holiday(hl,date):
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(hl,date),as_dict=True)
	if holiday:
		
		if holiday[0].weekly_off == 1:
			return "Weekly Off"
		else:
			return "Holiday"