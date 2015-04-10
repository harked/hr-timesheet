# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class hr_timesheet_overtime(osv.osv):
    _name = 'hr_timesheet_overtime.hr_timesheet_overtime'
    _inherit = 'hr_timesheet_sheet.sheet'

    def _total_duty_hours(self, cr, uid, ids, name, args, context=None):
        """ Compute the attendances, analytic lines timesheets and differences between them
            for all the days of a timesheet and the current day
        """

        res = {}
        for sheet in self.browse(cr, uid, ids, context=context or {}):
            res.setdefault(sheet.id, {
                'total_attendance': 0.0,
                'total_timesheet': 0.0,
                'total_difference': 0.0,
            })
            for period in sheet.period_ids:
                res[sheet.id]['total_attendance'] += period.total_attendance
                res[sheet.id]['total_timesheet'] += period.total_timesheet
                res[sheet.id]['total_difference'] += period.total_attendance - period.total_timesheet
        return res

    _columns = {
        'total_duty_hours': fields.function(_total_duty_hours, method=True, string='Total Duty Hours', multi="_total"),
    }
