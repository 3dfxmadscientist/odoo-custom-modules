# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from osv import fields, osv
from service import web_services
from tools.translate import _
import pytz
import re
import time
import tools
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

months = {
    1: "January", 2: "February", 3: "March", 4: "April", \
    5: "May", 6: "June", 7: "July", 8: "August", 9: "September", \
    10: "October", 11: "November", 12: "December"
}

def get_recurrent_dates(rrulestring, exdate, startdate=None, exrule=None):
    """
    Get recurrent dates based on Rule string considering exdate and start date
    @param rrulestring: Rulestring
    @param exdate: List of exception dates for rrule
    @param startdate: Startdate for computing recurrent dates
    @return: List of Recurrent dates
    """
    def todate(date):
        val = parser.parse(''.join((re.compile('\d')).findall(date)))
        return val
    
    if not startdate:
        startdate = datetime.now()
        
    if not exdate:
        exdate = []
        
    rset1 = rrule.rrulestr(str(rrulestring), dtstart=startdate, forceset=True)
    for date in exdate:
        datetime_obj = todate(date)
        rset1._exdate.append(datetime_obj)
    
    if exrule:
        rset1.exrule(rrule.rrulestr(str(exrule), dtstart=startdate))

    return list(rset1)

def base_calendar_id2real_id(base_calendar_id=None, with_date=False):
    """
    This function converts virtual event id into real id of actual event
    @param base_calendar_id: Id of calendar
    @param with_date: If value passed to this param it will return dates based on value of withdate + base_calendar_id
    """

    if base_calendar_id and isinstance(base_calendar_id, (str, unicode)):
        res = base_calendar_id.split('-')

        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime("%Y-%m-%d %H:%M:%S", \
                                 time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, "%Y-%m-%d %H:%M:%S")
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime("%Y-%m-%d %H:%M:%S"))
            return int(real_id)

    return base_calendar_id and int(base_calendar_id) or base_calendar_id

def real_id2base_calendar_id(real_id, recurrent_date):
    """
    Convert  real id of record into virtual id using recurrent_date
    e.g. real id is 1 and recurrent_date is 01-12-2009 10:00:00 then it will return
        1-20091201100000
    @return: real id with recurrent date.
    """

    if real_id and recurrent_date:
        recurrent_date = time.strftime("%Y%m%d%H%M%S", \
                            time.strptime(recurrent_date, "%Y-%m-%d %H:%M:%S"))
        return '%d-%s' % (real_id, recurrent_date)
    return real_id

def _links_get(self, cr, uid, context=None):
    """
    Get request link.
    @param cr: the current row, from the database cursor,
    @param uid: the current user’s ID for security checks,
    @param context: A standard dictionary for contextual values
    @return: list of dictionary which contain object and name and id.
    """
    obj = self.pool.get('res.request.link')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['object', 'name'], context=context)
    return [(r['object'], r['name']) for r in res]

html_invitation = """
<html>
<head>
<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
<title>%(name)s</title>
</head>
<body>
<table border="0" cellspacing="10" cellpadding="0" width="100%%"
    style="font-family: Arial, Sans-serif; font-size: 14">
    <tr>
        <td width="100%%">Hello,</td>
    </tr>
    <tr>
        <td width="100%%">You are invited for <i>%(company)s</i> Event.</td>
    </tr>
    <tr>
        <td width="100%%">Below are the details of event:</td>
    </tr>
</table>

<table cellspacing="0" cellpadding="5" border="0" summary=""
    style="width: 90%%; font-family: Arial, Sans-serif; border: 1px Solid #ccc; background-color: #f6f6f6">
    <tr valign="center" align="center">
        <td bgcolor="DFDFDF">
        <h3>%(name)s</h3>
        </td>
    </tr>
    <tr>
        <td>
        <table cellpadding="8" cellspacing="0" border="0"
            style="font-size: 14" summary="Eventdetails" bgcolor="f6f6f6"
            width="90%%">
            <tr>
                <td width="21%%">
                <div><b>Start Date</b></div>
                </td>
                <td><b>:</b></td>
                <td>%(start_date)s</td>
                <td width="15%%">
                <div><b>End Date</b></div>
                </td>
                <td><b>:</b></td>
                <td width="25%%">%(end_date)s</td>
            </tr>
            <tr valign="top">
                <td><b>Description</b></td>
                <td><b>:</b></td>
                <td colspan="3">%(description)s</td>
            </tr>
            <tr valign="top">
                <td>
                <div><b>Location</b></div>
                </td>
                <td><b>:</b></td>
                <td colspan="3">%(location)s</td>
            </tr>
            <tr valign="top">
                <td>
                <div><b>Event Attendees</b></div>
                </td>
                <td><b>:</b></td>
                <td colspan="3">
                <div>
                <div>%(attendees)s</div>
                </div>
                </td>
            </tr>
        </table>
        </td>
    </tr>
</table>
<table border="0" cellspacing="10" cellpadding="0" width="100%%"
    style="font-family: Arial, Sans-serif; font-size: 14">
    <tr>
        <td width="100%%">From:</td>
    </tr>
    <tr>
        <td width="100%%">%(user)s</td>
    </tr>
    <tr valign="top">
        <td width="100%%">-<font color="a7a7a7">-------------------------</font></td>
    </tr>
    <tr>
        <td width="100%%"> <font color="a7a7a7">%(sign)s</font></td>
    </tr>
</table>
</body>
</html>
"""

class calendar_event(osv.osv):
    _inherit = "calendar.event"
   

    def get_recurrent_date_by_event(self, cr, uid, event, context=None):
        """Get recurrent dates based on Rule string and all event where recurrent_id is child
        """
        def todate(date):
            val = parser.parse(''.join((re.compile('\d')).findall(date)))
            ## Dates are localized to saved timezone if any, else current timezone.
            if not val.tzinfo:
                val = pytz.UTC.localize(val)
            return val.astimezone(timezone)

        timezone = pytz.timezone(context.get('tz') or 'UTC')
        startdate = pytz.UTC.localize(datetime.strptime(event.start, DEFAULT_SERVER_DATETIME_FORMAT))  # Add "+hh:mm" timezone
        if not startdate:
            startdate = datetime.now()

        ## Convert the start date to saved timezone (or context tz) as it'll
        ## define the correct hour/day asked by the user to repeat for recurrence.
        startdate = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
        rset1 = rrule.rrulestr(str(event.rrule), dtstart=startdate, forceset=True)
        ids_depending = self.search(cr, uid, [('recurrent_id', '=', event.id), '|', ('active', '=', False), ('active', '=', True)], context=context)
        all_events = self.browse(cr, uid, ids_depending, context=context)
        for ev in all_events:
            rset1._exdate.append(todate(ev.recurrent_id_date))
        return [d.astimezone(pytz.UTC) for d in rset1]

    def _get_recurrency_end_date(self, cr, uid, id, context=None):
        data = self.read(cr, uid, id, ['final_date', 'recurrency', 'rrule_type', 'count', 'end_type', 'stop'], context=context)

        if not data.get('recurrency'):
            return False

        end_type = data.get('end_type')
        final_date = data.get('final_date')
        if end_type == 'count' and all(data.get(key) for key in ['count', 'rrule_type', 'stop']):
            count = data['count'] + 1
            delay, mult = {
                'daily': ('days', 1),
                'weekly': ('days', 7),
                'monthly': ('months', 1),
                'yearly': ('years', 1),
            }[data['rrule_type']]

            deadline = datetime.strptime(data['stop'], tools.DEFAULT_SERVER_DATETIME_FORMAT)
            return deadline + relativedelta(**{delay: count * mult})
        return final_date 

    
    def get_search_fields(self, browse_event, order_fields, r_date=None):
        sort_fields = {}
        for ord in order_fields:
            if ord == 'id' and r_date:
                sort_fields[ord] = '%s-%s' % (browse_event[ord], r_date.strftime("%Y%m%d%H%M%S"))
            else:
                sort_fields[ord] = browse_event[ord]
                if type(browse_event[ord]) is osv.orm.browse_record:
                    name_get = browse_event[ord].name_get()
                    if len(name_get) and len(name_get[0]) >= 2:
                        sort_fields[ord] = name_get[0][1]
        return sort_fields

    def get_recurrent_ids(self, cr, uid, event_id, domain, order=None, context=None):

        """Gives virtual event ids for recurring events
        This method gives ids of dates that comes between start date and end date of calendar views

        @param order: The fields (comma separated, format "FIELD {DESC|ASC}") on which the events should be sorted
        """
        if not context:
            context = {}

        if isinstance(event_id, (str, int, long)):
            ids_to_browse = [event_id]  # keep select for return
        else:
            ids_to_browse = event_id

        if order:
            order_fields = [field.split()[0] for field in order.split(',')]
        else:
            # fallback on self._order defined on the model
            order_fields = [field.split()[0] for field in self._order.split(',')]

        if 'id' not in order_fields:
            order_fields.append('id')

        result_data = []
        result = []
        for ev in self.browse(cr, uid, ids_to_browse, context=context):
            if not ev.recurrency or not ev.rrule:
                result.append(ev.id)
                result_data.append(self.get_search_fields(ev, order_fields))
                continue
            rdates = self.get_recurrent_date_by_event(cr, uid, ev, context=context)

            for r_date in rdates:
                # fix domain evaluation
                # step 1: check date and replace expression by True or False, replace other expressions by True
                # step 2: evaluation of & and |
                # check if there are one False
                pile = []
                ok = True
                for arg in domain:
                    if str(arg[0]) in ('start', 'stop', 'final_date'):
                        if (arg[1] == '='):
                            ok = r_date.strftime('%Y-%m-%d') == arg[2]
                        if (arg[1] == '>'):
                            ok = r_date.strftime('%Y-%m-%d') > arg[2]
                        if (arg[1] == '<'):
                            ok = r_date.strftime('%Y-%m-%d') < arg[2]
                        if (arg[1] == '>='):
                            ok = r_date.strftime('%Y-%m-%d') >= arg[2]
                        if (arg[1] == '<='):
                            ok = r_date.strftime('%Y-%m-%d') <= arg[2]
                        pile.append(ok)
                    elif str(arg) == str('&') or str(arg) == str('|'):
                        pile.append(arg)
                    else:
                        pile.append(True)
                pile.reverse()
                new_pile = []
                for item in pile:
                    if not isinstance(item, basestring):
                        res = item
                    elif str(item) == str('&'):
                        first = new_pile.pop()
                        second = new_pile.pop()
                        res = first and second
                    elif str(item) == str('|'):
                        first = new_pile.pop()
                        second = new_pile.pop()
                        res = first or second
                    new_pile.append(res)
                if [True for item in new_pile if not item]:
                    continue
                result_data.append(self.get_search_fields(ev, order_fields, r_date=r_date))

        if order_fields:
            def comparer(left, right):
                for fn, mult in comparers:
                    result = cmp(fn(left), fn(right))
                    if result:
                        return mult * result
                return 0

            sort_params = [key.split()[0] if key[-4:].lower() != 'desc' else '-%s' % key.split()[0] for key in (order or self._order).split(',')]
            comparers = [((itemgetter(col[1:]), -1) if col[0] == '-' else (itemgetter(col), 1)) for col in sort_params]
            ids = [r['id'] for r in sorted(result_data, cmp=comparer)]

        if isinstance(event_id, (str, int, long)):
            return ids and ids[0] or False
        else:
            return ids


    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        if context is None:
            context = {}

        if context.get('mymeetings', False):
            partner_id = self.pool['res.users'].browse(cr, uid, uid, context).partner_id.id
            args += [('partner_ids', 'in', [partner_id])]

        new_args = []
        for arg in args:
            new_arg = arg

            if arg[0] in ('start_date', 'start_datetime', 'start',) and arg[1] == ">=":
                if context.get('virtual_id', True):
                    new_args += ['|', '&', ('recurrency', '=', 1), ('final_date', arg[1], arg[2])]
            elif arg[0] == "id":
                new_id = get_real_ids(arg[2])
                new_arg = (arg[0], arg[1], new_id)
            new_args.append(new_arg)

        # This allow to bypass the search function defined on the base_calendar module
        metaModel = [tup for tup in self.__class__.__mro__ if str(tup) == "<class 'openerp.osv.orm.Model'>"][0]
        
        if not context.get('virtual_id', True):
            return super(metaModel,self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, count=count, context=context)
        # offset, limit, order and count must be treated separately as we may need to deal with virtual ids
        res = super(metaModel,self).search(cr, uid, new_args, offset=0, limit=0, order=None, context=context, count=False)
        res = self.get_recurrent_ids(cr, uid, res, args, order=order, context=context)
        if count:
            return len(res)
        elif limit:
            return res[offset: offset + limit]
        return res

calendar_event()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
