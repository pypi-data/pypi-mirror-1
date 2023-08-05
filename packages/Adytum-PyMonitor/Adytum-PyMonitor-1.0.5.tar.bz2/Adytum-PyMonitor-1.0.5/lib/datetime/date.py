from datetime import datetime

def fromCtime(ctime_string):
    dow, month, day, hms, year = ctime_string.strip().split()
    months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
        'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    month = months[month]
    h, m, s = hms.split(':')
    return datetime(int(year), month, int(day), int(h), int(m), int(s))

fromctime = getDateFromCtime = dateFromCtime = fromCtime
