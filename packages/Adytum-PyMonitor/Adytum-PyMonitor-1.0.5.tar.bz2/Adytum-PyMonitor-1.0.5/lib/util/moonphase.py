try:
    from ephem import Moon
    from mx.DateTime import DateTime, DateTimeFromJDN
except:
    raise '''
You must have pyephem and mxDateTime installed in order to use this module. 

PyEphem (ephem): http://www.rhodesmill.org/brandon/projects/pyephem.html
mxDateTime (mx.DateTime): http://www.egenix.com/files/python/eGenix-mx-Extensions.html#Download-mxBASE
     
'''

PHASE_DAYS = 29.530587


'''
from MoonPhase import MoonPhase
m = MoonPhase('2004/08/01')
m.getStageName()
m.getPhaseDay()

from math import radians

for i in range(31):
  m.setDate('2004/08/%s' % str(i+1));p = m.getPhasePercent();degs = 90*p/100;rads = radians(degs)
  print i + 1, round(p), m.getStageName(), round(degs)


'''

class MoonPhase:

    def __init__(self, date_str):
        '''
        date_str takes the form 'YYYY/MM/DD'
        '''
        self.moon = Moon()
        self.setDate(date_str)

    def getPhasePercent(self):
        try:
            if self.phase_percent:
                return self.phase_percent
        except:
            self.phase_percent = self.moon.phase
            return self.phase_percent

    def getPhaseDegrees(self):
            self.phase_degrees = self.moon.moon_phase
            return self.phase_degrees

    def getPhaseName(self):
        pcnt = self.getPhaseDay()
        if pcnt < 2:
            self.phase_name = 'New'
        elif pcnt <= 6:
            self.phase_name = 'Cresent Waxing'
        elif pcnt > 46 and pcnt < 54:
            self.phase_name = 'Half Moon'
        elif pcnt > 99:
            self.phase_name = 'Full'
        else:
            self.phase_name = None

    def getAll(self):
        return (self.getPhasePercent(), self.getPhaseDegrees(), self.getPhaseName())

    def getStage(self):
        try:
            if self.stage:
                return self.stage
        except:
            pass
        start_day = self.start
        start = self.getPhasePercent()
        day_before = self.getMoonPhaseDate(start_day - 1)
        self.setDate(day_before)
        day_before = self.getPhasePercent()
        day_after = self.getMoonPhaseDate(start_day + 1)
        self.setDate(day_after)
        day_after = self.getPhasePercent()
        #print day_before, start, day_after
        if day_after > start and day_before > start:
            stage = 0
        elif day_after < start and day_before < start:
            stage = 1
        elif day_after > start and day_before < start:
            stage = 0.5
        elif day_after < start and day_before > start:
            stage = -0.5

        # put things back
        self.resetMoon(start_day)

        self.stage = stage
        return self.stage

    def getStageName(self):
        try:
            if self.stage_name:
                return self.stage_name 
        except:
            self.getStage()
            stages = {
                0: 'New',
                1: 'Full',
                0.5: 'Waxing',
                -0.5: 'Waning',
            }
            self.stage_name = stages[self.stage]
        return self.stage_name

    def resetMoon(self, dt_object):
        start = self.getMoonPhaseDate(dt_object)
        self.setDate(start)

    def getRecentNew(self):
        '''
        Returns a string date, but saves a DateTime object to instance
        '''
        start_day = self.start
        if self.getStageName == 'New':
            return start_day
        else:
            for day in range(1,31):
                check_day = DateTimeFromJDN(start_day.jdn - day)
                check_day_str = self.getMoonPhaseDate(check_day)
                #print check_day.jdn, check_day_str
                self.setDate(check_day_str)
                if self.getStageName() == 'New':
                    self.last_new = check_day
                    # put things back
                    self.resetMoon(start_day)
                    return check_day_str
        
    def getMoonPhaseDate(self, dt_object):
        return dt_object.strftime('%Y/%m/%d')
        
    def getDayOfPhase(self):
        try:
            if self.phase_day:
                return self.phase_day
        except:
            pass
        self.getRecentNew()
        self.phase_day = int(self.start.jdn - self.last_new.jdn)
        return self.phase_day

    getPhaseDay = getDayOfPhase

    def setDate(self, date_str):
        (self.year, self.month, self.day) = [ int(x) for x in date_str.split('/') ]
        self.start = DateTime(self.year, self.month, self.day)
        self.daybefore = DateTimeFromJDN(self.start.jdn - 1)
        self.dayafter = DateTimeFromJDN(self.start.jdn + 1)
        self.moon.compute(date_str)
        try:
            del(self.phase_day)
        except:
            pass
        try:
            del(self.phase_percent)
        except:
            pass
        try:
            del(self.phase_degrees)
        except:
            pass
        try:
            del(self.stage)
        except:
            pass
        try:
            del(self.stage_name)
        except:
            pass


