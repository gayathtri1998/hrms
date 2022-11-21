# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, getdate
from frappe.utils import data, formatdate

from hrms.hr.doctype.leave_allocation.leave_allocation import get_previous_allocation
from hrms.hr.doctype.leave_application.leave_application import (
    get_leave_balance_on,
    get_leaves_for_period,
)
Filters = frappe._dict

def execute(filters = None):
    if filters.to_date <= filters.from_date:
        frappe.throw(_('"From Date" can not be greater than or equal to "To Date"'))

    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:100",
        _("Employee Name") + ":Data:150",
        _("Department") + ":Data:150",
        _("From Date") + ":Data:150",
        _("To Date") + ":Data:150",
        _("Leave Type") + ":Data:150",
        _("Leave Availed") + ":Data:150",
        _("Leave Balance Before Application") + ":Data:150",
        _("Leave Approver") + ":Data:150",
        _("Status") + ":Data:150",
    ]	
    return columns

def get_data(filters):  
    data = []
    docstatus = ''

    if filters.employee:
        leave_types = frappe.db.sql("""select * from `tabLeave Application` where from_date between '%s' and '%s' and employee = '%s' and docstatus = '1' """%(filters.from_date,filters.to_date,filters.employee),as_dict=True)
        for lt in leave_types:
            data.append([lt.employee,lt.employee_name,lt.department,formatdate(lt.from_date),formatdate(lt.to_date),lt.leave_type,lt.total_leave_days,lt.leave_balance,lt.leave_approver,lt.status])

    elif filters.department:
        leave_types = frappe.db.sql("""select * from `tabLeave Application` where from_date between '%s' and '%s' and department = '%s' and docstatus = '1' """%(filters.from_date,filters.to_date,filters.department),as_dict=True)
        for lt in leave_types:
            
            data.append([lt.employee,lt.employee_name,lt.department,formatdate(lt.from_date),formatdate(lt.to_date),lt.leave_type,lt.total_leave_days,lt.leave_balance,lt.leave_approver,lt.status])
    
    else:
        leave_types = frappe.db.sql("""select * from `tabLeave Application` where from_date between '%s' and '%s' and docstatus = '1' """%(filters.from_date,filters.to_date),as_dict=True)
        for lt in leave_types:
            
            data.append([lt.employee,lt.employee_name,lt.department,formatdate(lt.from_date),formatdate(lt.to_date),lt.leave_type,lt.total_leave_days,lt.leave_balance,lt.leave_approver,lt.status])
    return data

