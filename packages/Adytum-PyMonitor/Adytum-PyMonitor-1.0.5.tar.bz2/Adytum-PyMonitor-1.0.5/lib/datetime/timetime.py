'''
From http://tycho.usno.navy.mil/sidereal.html:

"Local mean sidereal time is computed from the current Greenwich
Mean Sideral Time plus an input offset in longitude (converted to
a sidereal offset by the ratio 1.00273790935 of the mean solar day
to the mean sidereal day.) Applying the equation of equinoxes, or
nutation of the mean pole of the Earth from mean to true position,
yields local apparent sidereal time."

When it is 12 o'clock (noon) solar time on the vernal equinox, it
is 0 hours sidereal time.

The reference against which the julian dates were checked is here:
    http://aa.usno.navy.mil/data/docs/JulianDate.html

Various elements of this module were copied and/or modified from the following sources:
    http://cwashington.netreach.net/depo/view.asp?Index=105&ScriptType=python
    http://vsg.cape.com/~pbaum/date/jdimp.htm
    http://www2.arnes.si/~gljsentvid10/sidereal.htm
    http://www.seti.net/SETINet/OtherInformation/Calculators/calculators.htm
    http://aa.usno.navy.mil/faq/docs/GAST.html
'''
from datetime import datetime
from datetime import time
import math

import pytz

DAYS_IN_YEAR = 365.25
X1 = 100
X2 = 30.6001
GREGORIAN_YEAR = 1582
GREGORIAN_MONTH = 10
GREGORIAN_DAY = 15
JD_NUM1_OFFSET = 1720994.5
JULIAN_EPOCH = 2451545.0
CENTURY_DAYS = 36525.0
COEF1 = 6.697374558
COEF2 = 2400.051336
COEF3 = 0.000025862
GMST_A = 280.46061837
GMST_B = 360.98564736629
GMST_C = 0.000387933
GMST_D = 38710000
SOLAR_SIDEREAL_RATIO = 1.002737909350795

GMT = pytz.timezone('GMT')

def cos(deg):
    return math.cos(math.radians(deg))

def sin(deg):
    return math.sin(math.radians(deg))

def todecimalhours(time_obj):
    seconds = time_obj.second/(60.**2)
    minutes = time_obj.minute/60.
    return time_obj.hour + minutes + seconds

def fromdecimalhours(float_num):
    pass

def hoursdayfraction(time_obj):
    return todecimalhours(time_obj)/24.

def check_tz(datetime_obj):
    if not datetime_obj.tzinfo:
        raise "You must pass a datetime object with a timezone ('see pytz.timzone()')"

def ut(datetime_obj):
    check_tz(datetime_obj)
    return datetime_obj.astimezone(GMT)

def degreesToTime(degrees):
    d = degrees % 360
    hour, minutes = divmod((d/360) * 24, 1)
    minute, seconds = divmod(minutes*60, 1)
    second, micro = divmod(seconds*60, 1)
    return time(int(hour), int(minute), int(second))

def isLeapYear(datetime_obj):
    '''
    >>> from datetime import datetime
    >>> dt = datetime(1972,8,17); isLeapYear(dt)
    True
    >>> dt = datetime(2000,8,17); isLeapYear(dt)
    True
    >>> dt = datetime(2004,8,17); isLeapYear(dt)
    True
    >>> dt = datetime(2005,8,17); isLeapYear(dt)
    False
    '''
    y = datetime_obj.year
    if (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0):
        return True
    else:
        return False

def daysInMonth(datetime_obj):
    '''
    >>> from datetime import datetime
    >>> dt = datetime(2000,1,1); daysInMonth(dt)
    31
    >>> dt = datetime(2000,2,1); daysInMonth(dt)
    29
    >>> dt = datetime(2001,2,1); daysInMonth(dt)
    28
    >>> dt = datetime(2005,3,1); daysInMonth(dt)
    31
    >>> dt = datetime(2005,4,1); daysInMonth(dt)
    30
    >>> dt = datetime(2005,5,1); daysInMonth(dt)
    31
    >>> dt = datetime(2005,6,1); daysInMonth(dt)
    30
    >>> dt = datetime(2005,7,1); daysInMonth(dt)
    31
    >>> dt = datetime(2005,8,1); daysInMonth(dt)
    31
    >>> dt = datetime(2005,9,1); daysInMonth(dt)
    30
    >>> dt = datetime(2005,10,1); daysInMonth(dt)
    31
    >>> dt = datetime(2005,11,1); daysInMonth(dt)
    30
    >>> dt = datetime(2005,12,1); daysInMonth(dt)
    31
    '''
    m = datetime_obj.month
    y = datetime_obj.year 
    if m == 2:
        if isLeapYear(datetime_obj):
            return 29
        else:
            return 28
    elif m in [9,4,6,11]:
        return 30
    elif m in [1,3,5,7,8,10,12]:
        return 31

def dayOfYear(datetime_obj):
    '''
    >>> from datetime import datetime
    >>> dt = datetime(2000,1,1); dayOfYear(dt)
    1
    >>> dt = datetime(2000,12,31); dayOfYear(dt)
    366
    >>> dt = datetime(2005,12,31); dayOfYear(dt)
    365
    >>> dt = datetime(1972,8,17); dayOfYear(dt)
    230
    >>> dt = datetime(2005,8,17); dayOfYear(dt)
    229
    '''
    y, m, d = datetime_obj.year, datetime_obj.month, datetime_obj.day
    if isLeapYear(datetime_obj):
        n = int((275*m)/9 - ((m + 9)/12) + int(d) - 30)
    else:
        n = int((275*m)/9 - 2*((m + 9)/12) + int(d) - 30)
    return n

def julianToDateTime(jd):
    '''
    >>> julianToDateTime(2451544.49999).timetuple()
    (1999, 12, 31, 23, 59, 59, 4, 365, 0)
    >>> julianToDateTime(2451544.5).timetuple()
    (2000, 1, 1, 0, 0, 0, 5, 1, 0)
    >>> julianToDateTime(2453682.54411).timetuple()
    (2005, 11, 8, 1, 3, 31, 1, 312, 0)
    >>> julianToDateTime(2453736.49999).timetuple()
    (2005, 12, 31, 23, 59, 59, 5, 365, 0)
    >>> julianToDateTime(2453736.5).timetuple()
    (2006, 1, 1, 0, 0, 0, 6, 1, 0)
    '''
    if jd < 0:  raise "Can't handle negative days."
    jd += 0.5
    z = int(jd)
    f = jd - z
    a = z
    if z >= 2299161:
        alpha = int((z - 1867216.26)/36254.25)
        a = z + 1 + alpha - int(alpha/4)
    b = a + 1524
    c = int((b - 122.1)/365.25)
    d = int(365.25 * c)
    e = int((b - d)/30.6001)
    day = b - d - int(30.6001 * e) + f
    if e < 13.5:
        month = int(e - 1)
    else:
        month = int(e - 13)
    if month > 2.5:
        year = int(c - 4716)
    else:
        year = int(c - 4715)
    day, hours = divmod(day, 1)
    hour, minutes = divmod(hours * 24, 1)
    minute, seconds = divmod(minutes * 60, 1)
    second, micros = divmod(seconds * 60, 1)
    micro = round(micros * 1000)
    return datetime(int(year), int(month), int(day), 
        int(hour), int(minute), int(second), int(micro), GMT)

def dayOfWeek(datetime_obj):
    '''
    >>> from datetime import datetime
    >>> dt = datetime(2005,11,6); dayOfWeek(dt)
    0
    >>> dt = datetime(2005,11,7); dayOfWeek(dt)
    1
    >>> dt = datetime(2005,11,11); dayOfWeek(dt)
    5
    >>> dt = datetime(2005,11,12); dayOfWeek(dt)
    6
    '''
    return (datetime_obj.weekday() + 1) % 7

def julian(datetime_obj):
    '''
    Currently, this produces incorrect julian dates for dates
    less than the Gregorian switch-over.

    >>> dt = datetime(2299, 12, 31, 23, 59, 59); julian(dt) - 2561117.49999
    0.0
    >>> dt = datetime(2199, 12, 31, 23, 59, 59); julian(dt) - 2524593.49999
    0.0
    >>> dt = datetime(2099, 12, 31, 23, 59, 59); julian(dt) - 2488069.49999
    0.0
    >>> dt = datetime(1999, 12, 31, 23, 59, 59); julian(dt) - 2451544.49999
    0.0
    >>> dt = datetime(1899, 12, 31, 23, 59, 59); julian(dt) - 2415020.49999
    0.0
    >>> dt = datetime(1799, 12, 31, 23, 59, 59); julian(dt) - 2378496.49999
    0.0
    >>> dt = datetime(1699, 12, 31, 23, 59, 59); julian(dt) - 2341972.49999
    0.0
    >>> dt = datetime(1599, 12, 31, 23, 59, 59); julian(dt) - 2305447.49999
    0.0
    >>> dt = datetime(1499, 12, 31, 23, 59, 59)
    >>> dt = datetime(1399, 12, 31, 23, 59, 59)
    >>> dt = datetime(1299, 12, 31, 23, 59, 59)
    '''
    tz = datetime_obj.tzinfo
    if tz and tz != GMT:
        datetime_obj = ut(datetime_obj)
    y, m, d, h, mn, s, nil, nil, tz = (datetime_obj.timetuple())
        
    d = float(d + h/24. + mn/60. + s/60.**2)
    if m < 3:
        m += 12
        y -= 1
    # my day correction to bring it into accordance with the USNO Julian Calculator
    d -= 0.9580655555
    #julian = d + (153*m - 457)/5 + int(365.25 *y) - int(y * .01 ) + int(y * .0025 ) + 1721118.5
    if datetime_obj < datetime(GREGORIAN_YEAR, GREGORIAN_MONTH,
        GREGORIAN_DAY):
        b = 0
    else:
        b = int(y / 4) - int(y / 100) + int(y / 400)
    if y < 0:
        c = int((365.25 * Y) - .75)
    else:
        c = int(365.25) * y
    julian = d + int((153 * m - 457)/5) + b + c + 1721118.5
    return float(julian)

def julianToDegrees(jd):
    '''
    >>>
    '''
    

def meanSiderealTime(datetime_obj):
    '''
    Returns the Mean Sidereal Time in degrees:

    >>> dt = datetime(1994, 06, 16, 18, 0, 0)
    >>> degreesToTime(meanSiderealTime(dt))
    datetime.time(11, 39, 5)

    # vernal equinox in 2006
    >>> dt = datetime(2006, 03, 20, 13, 26, 00)
    >>> degreesToTime(meanSiderealTime(dt))
    datetime.time(11, 17, 23)

    # hmmm... 
    '''
    jd = julian(datetime_obj)
    d = jd - (julian(datetime(2000,1,1)) + 0.5)
    #d = -2024.75000
    mst = GMST_A + (GMST_B * d) + (GMST_C * (d/CENTURY_DAYS)**2)
    return mst % 360

greenwhichMeanSiderealTime = meanSiderealTime
GMST = meanSiderealTime

def localSiderealTime(datetime_obj, longitude):
    '''
    >>> dt = datetime(1994, 06, 16, 18, 0, 0)
    >>> longitude = -105.09 # loveland, co
    >>> localSiderealTime(dt, longitude)
    >>> degreesToTime(localSiderealTime(dt, longitude))
    datetime.time(4, 38, 43)
    '''
    gmst = meanSiderealTime(datetime_obj)
    return (gmst + longitude) % 360

#localMeanSiderealTime = localSiderealTime
#LMST = localSiderealTime

def equationOfTheEquinoxes(datetime_obj):
    jd = julian(datetime_obj)
    d = jd - (julian(datetime(2000,1,1)) + 0.5)
    c = d/CENTURY_DAYS
    Om = (125.04452 - 0.052954 * c) % 360
    L = (280.4665 + 0.98565 * c) % 360
    epsilon = (23.4393 - 0.0000004 * c) % 360
    delta_psi = -0.000319 * sin(Om) - 0.000024 * sin(2*L)
    return delta_psi * cos(epsilon)

def apparentSideralTime(datetime_obj):
    '''
    >>> dt = datetime(1994, 06, 16, 18, 0, 0)
    >>> apparentSideralTime(dt)
    174.77457329366436
    >>> dt = datetime.now()
    >>> apparentSideralTime(dt)
    '''
    jd = julian(datetime_obj)
    d = jd - (julian(datetime(2000,1,1)) + 0.5)
    c = d/CENTURY_DAYS

    Om = (125.04452 - 1934.136261 * c) % 360
    L = (280.4665 + 36000.7698 * c) % 360
    L1 = (218.3165 + 481267.8813 * c) % 360
    e = (23.4393 - 0.0000004 * c) % 360
    dp = -17.2 * sin(Om) - 1.32 * sin(2 * L) - 0.23 * sin(2 * L1)  + 0.21 * sin(2 * Om)
    de = 9.2 * cos(Om) + 0.57 * cos(2 * L) + 0.1 * cos(2 * L1) - 0.09 * cos(2 * Om)

    gmst = meanSiderealTime(datetime_obj)
    correction = dp * cos(e) / 3600

    return gmst + correction
    
def localApparentSiderealTime(datetime_obj, longitude):
    '''

    '''
    gast = apparentSideralTime(datetime_obj)
    return (gast + longitude) % 360
    
def currentLAST(longitude):
    '''
    >>> currentLAST(-105.09)
    >>> degreesToTime(currentLAST(-105.09))
    '''
    return localApparentSiderealTime(datetime.now(), longitude)

def _test():
    from doctest import testmod
    import timetime
    testmod(timetime)

if __name__ == '__main__':
    _test()
