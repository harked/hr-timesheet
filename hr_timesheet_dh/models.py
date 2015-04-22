# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from dateutil import rrule, parser

class hr_timesheet_dh(osv.osv):
    """
        Addition plugin for HR timesheet for work with duty hours
    """
    #_name = 'hr_timesheet_sheet.sheet'
    _inherit = 'hr_timesheet_sheet.sheet'

    def _duty_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sheet in self.browse(cr, uid, ids, context=context or {}):
            res.setdefault(sheet.id, {
                'total_duty_hours': 0.0,
            })
            for duty_hours in sheet.duty_hour_ids:
                res[sheet.id]['total_duty_hours'] += duty_hours.duty_hours
        return res

    _columns = {
        'total_duty_hours': fields.function(_duty_hours, method=True, string='Total Duty Hours', multi="_duty_hours"),
        'duty_hour_ids': fields.one2many('hr_timesheet.day.dh', 'sheet_id', 'Daily Duty Hours', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        res = super(hr_timesheet_dh, self).create(cr, uid, vals, context=context)
        self.create_days_dh(cr, uid, [res], context)
        return res

    def create_days_dh(self, cr, uid, ids, context=None):
        for sheet in self.browse(cr, uid, ids, context=context or {}):

            dates = list(rrule.rrule(rrule.DAILY,
                                     dtstart=parser.parse(sheet.date_from),
                                     until=parser.parse(sheet.date_to)))
            for date_line in dates:
                duty_hours = self.calculate_duty_hours(cr, uid, sheet.employee_id.id, date_line, context)
                self.pool.get('hr_timesheet.day.dh').create(cr,
                                                            uid,
                                                            {'name': date_line, 'duty_hours': duty_hours, 'sheet_id': sheet.id},
                                                            context)

    def calculate_duty_hours(self, cr, uid, employee_id, date_from, context):
        contract_obj = self.pool.get('hr.contract')
        calendar_obj = self.pool.get('resource.calendar')
        duty_hours = 0.0
        contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_id),
                                                     ('date_start','<=', date_from), '|',
                                                     ('date_end', '>=', date_from), ('date_end', '=', None) ], context=context)
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            dh = calendar_obj.get_working_hours_of_date(cr=cr, uid=uid,
                                                         id=contract.working_hours.id,
                                                         start_dt=date_from,
                                                         context=context)
            duty_hours += dh
        return duty_hours

    def get_previous_month_diff(self, cr, uid, employee_id, month, year, context=None):
        return -15.00

    def attendance_analysis(self, cr, uid, employee_id, month, year, context=None):
        previous_month_diff = self.get_previous_month_diff(cr, uid, employee_id, month, year, context)
        current_month_diff = previous_month_diff
        res = {
            'previous_month_diff': previous_month_diff,
            'hours': []
        }
        attendence_obj = self.pool.get('hr.attendance')
        attendence_ids = attendence_obj.search(cr, uid, [('employee_id','=', employee_id), ('action', '=', 'sign_out')])
        for attendence in attendence_obj.browse(cr, uid, attendence_ids, context=context):
            dh = self.calculate_duty_hours(cr, uid, employee_id, parser.parse(attendence.name), context)
            worked_hours = attendence.worked_hours
            diff = attendence.worked_hours-dh
            current_month_diff += diff
            res['hours'].append({'name': attendence.name,
                                 'worked_hours': attendence_obj.float_time_convert(worked_hours),
                                 'dh': attendence_obj.float_time_convert(dh),
                                 'diff': self.sign_float_time_convert(diff),
                                 'running': self.sign_float_time_convert(current_month_diff)})
        return res

    def sign_float_time_convert(self, float_time):
        sign = '-' if float_time < 0 else ''
        attendence_obj = self.pool.get('hr.attendance')
        return sign+attendence_obj.float_time_convert(float_time)


class hr_timesheet_day_dh(osv.osv):
    """
        Daily duty hours
    """
    _name = 'hr_timesheet.day.dh'

    def _init_duty_hours(self):
        self.duty_hours = 5.0

    _columns = {
        'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet'),
        'name': fields.date('Date'),
        'duty_hours': fields.float('Duty Hours'),
    }
