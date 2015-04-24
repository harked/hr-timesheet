# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.osv import fields, osv
from dateutil import rrule, parser

class hr_timesheet_dh(osv.osv):
    """
        Addition plugin for HR timesheet for work with duty hours
    """
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
        'total_diff_hours': fields.float('Total Diff Hours', readonly=True, default=-10.0),
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

    def get_previous_month_diff(self, cr, uid, employee_id, prev_timesheet_date_to, context=None):
        total_diff = 0.0
        for timesheet in self.search_read(cr, uid, [('employee_id','=',employee_id),
                                                    ('date_to', '<', prev_timesheet_date_to),
                                                    ], ['total_diff_hours']):
            total_diff += timesheet['total_diff_hours']
        return total_diff

    def attendance_analysis(self, cr, uid, employee_id, start_date, end_date, context=None):
        previous_month_diff = self.get_previous_month_diff(cr, uid, employee_id, start_date, context)
        current_month_diff = previous_month_diff
        res = {
            'previous_month_diff': previous_month_diff,
            'hours': []
        }
        attendance_obj = self.pool.get('hr.attendance')

        dates = list(rrule.rrule(rrule.DAILY,
                                 dtstart=parser.parse(start_date),
                                 until=min(parser.parse(end_date), datetime.now())))
        total = {'worked_hours': 0.0, 'diff': current_month_diff}
        for date_line in dates:
            dh = self.calculate_duty_hours(cr, uid, employee_id, date_line, context)
            worked_hours = 0.0
            for attendance in attendance_obj.search_read(cr, uid, [('employee_id','=', employee_id),
                                                         ('action', '=', 'sign_out'),
                                                         ('name', '>=', date_line.strftime('%Y-%m-%d 00:00:00')),
                                                         ('name', '<=', date_line.strftime('%Y-%m-%d 23:59:59')),
                                                         ], ['name', 'worked_hours']):
                worked_hours = attendance['worked_hours']

            diff = worked_hours-dh
            current_month_diff += diff
            res['hours'].append({'name': date_line.strftime('%Y-%m-%d'),
                                 'worked_hours': attendance_obj.float_time_convert(worked_hours),
                                 'dh': attendance_obj.float_time_convert(dh),
                                 'diff': self.sign_float_time_convert(diff),
                                 'running': self.sign_float_time_convert(current_month_diff)})
            total['worked_hours'] += worked_hours
            total['diff'] += diff
        res['total'] = total
        return res

    def sign_float_time_convert(self, float_time):
        sign = '-' if float_time < 0 else ''
        attendance_obj = self.pool.get('hr.attendance')
        return sign+attendance_obj.float_time_convert(float_time)

    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals and vals['state'] == 'done':
            vals['total_diff_hours'] = self.calculate_diff(cr, uid, ids, context)
        elif 'state' in vals and vals['state'] == 'draft':
            vals['total_diff_hours'] = 0.0
        res = super(hr_timesheet_dh, self).write(cr, uid, ids, vals, context=context)
        return res

    def calculate_diff(self, cr, uid, ids, context=None):
        attendance_obj = self.pool.get('hr.attendance')
        for sheet in self.browse(cr, uid, ids, context):
            worked_hours = 0.0
            for attendance in attendance_obj.search_read(cr, uid, [('sheet_id', '=', sheet.id),
                                                                   ('action', '=', 'sign_out'),
                                                                  ], ['name', 'worked_hours']):
                worked_hours = attendance['worked_hours']
            return worked_hours-sheet.total_duty_hours

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
