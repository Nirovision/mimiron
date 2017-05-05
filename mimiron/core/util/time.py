# -*- coding: utf-8 -*-
from dateutil import tz
import humanize


def pretty_print_datetime(dt):
    # Make sure the `dt` is timezone aware before pretty printing.
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt_pretty = dt.replace(tzinfo=tz.gettz('UTC'))
        dt_pretty = dt_pretty.astimezone(tz.tzlocal())
    else:
        dt_pretty = dt.astimezone(tz.tzlocal())

    dt_pretty_friendly = dt_pretty.strftime('%a %d %b, %I:%M%p')
    dt_pretty_humanized = humanize.naturaltime(dt_pretty.replace(tzinfo=None))

    return '%s (%s)' % (dt_pretty_friendly, dt_pretty_humanized)
