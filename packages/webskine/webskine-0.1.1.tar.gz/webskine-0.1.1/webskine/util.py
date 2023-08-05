import datetime

from dateutil.relativedelta import relativedelta


def time_ago(dt):
    rd = relativedelta(datetime.datetime.utcnow(), dt)
    
    attrs = ["years", "months", "days", "hours", "minutes", "seconds"]
    for attr in attrs:
        v = getattr(rd, attr)
        if v:
            if v == 1: attr = attr[:-1]
            return "%s %s ago" % (v, attr)
            break
    return 'right now'
