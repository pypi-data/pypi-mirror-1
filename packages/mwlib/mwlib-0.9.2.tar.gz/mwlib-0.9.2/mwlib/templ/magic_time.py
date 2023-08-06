
import datetime
import re
import calendar
from dateutil.parser import parse as parsedate
from mwlib.strftime import strftime

def ampm(date):
    if date.hour < 12:
        return "am"
    else:
        return "pm"

rx = re.compile('"[^"]*"|\\\\.|.')
codemap = dict(
    y = '%y',
    Y = '%Y',
    n = lambda d: str(d.month),
    m = '%m',
    M = '%b',
    F = '%B',
    W = lambda d: "%02d" % (d.isocalendar()[1],),
    j = lambda d: str(d.day),
    d = '%d',
    z = lambda d: str(d.timetuple().tm_yday-1),
    D = '%a',
    l = '%A',
    N = lambda d: str(d.isoweekday()),
    w = lambda d: str(d.isoweekday() % 7),
    a = ampm,
    A = lambda d: ampm(d).upper(),
    g = lambda d: str(((d.hour-1) % 12) + 1),
    h = "%I",
    G = lambda d: str(d.hour),
    H = lambda d: "%02d" % (d.hour,),
    i = '%M',
    s = '%S',
    U = lambda d: str(calendar.timegm(d.timetuple())),
    L = lambda d: str(int(calendar.isleap(d.year))),
    c = "%Y-%m-%dT%H:%M:%S+00:00",
    r = "%a, %d %b %Y %H:%M:%S +0000",
    t = lambda d: str(calendar.monthrange(d.year, d.month)[1]),
    )


def formatdate(format, date):
    split = rx.findall(format)

    tmp = []
    for x in split:
        f = codemap.get(x, None)
        if f is None:
            if len(x)==2 and x.startswith("\\"):
                tmp.append(x[1])
            elif len(x)>=2 and x.startswith('"'):
                tmp.append(x[1:-1])
            else:
                tmp.append(x)
        else:
            if isinstance(f, basestring):
                tmp.append(strftime(date, f))
            else:
                tmp.append(f(date))


    tmp = u"".join(tmp).strip()
    return tmp

def time(format, datestring=None):
    date = None
    if datestring:
        try:
            date = parsedate(datestring)
        except ValueError:
            pass

    if date is None:
        date = datetime.datetime.now()

    return formatdate(format, date)
