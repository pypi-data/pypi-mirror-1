"""Module to provide classes for various kinds of peiods.
"""

import datetime

class GenericPeriod:
    """Class to represent a generic period.
    """

    
    def __init__(self, periodStr):
        self.periodStr = periodStr

    def ActivateP(self, now=None):
        """Return True/False for whether period has been activated.

        Sub-classes should override this.

        Takes optional datetime indicating time to consider as now.
        If this is None, we check datetime.datetime.now()

        Most periods have a notion of state. So once they return True
        for ActivateP, they may return False for a while until conditions
        are such that they return True.
        """
        raise NotImplementedError

class NoPeriod(GenericPeriod):
    """Period for something that never happens.

>>> import Periodicity
>>> p = Periodicity.NoPeriod(None)
>>> p.ActivateP()
False
    """

    def __init__(self, periodStr):
        if (periodStr is None or periodStr.strip() in ['None','NONE','']):
            GenericPeriod.__init__(self, periodStr)
        else:
            raise Exception('The periodStr %s is not valid for NoPeriod.'
                            % str(periodStr))

    def ActivateP(self, now=None):
        "Never activated"

        _ignore = now
        
        return False

class ExactDateTime(GenericPeriod):
    """Period for an exact date/time.

>>> import Periodicity
>>> p = Periodicity.ExactDateTime('2005-01-01 05:06:07')
>>> p.ActivateP(datetime.datetime(2000,1,1,1,1))
False
>>> p.ActivateP(datetime.datetime(2009,1,1,1,1))
True
"""

    def __init__(self, periodStr):
        self.target = datetime.datetime.strptime(periodStr, '%Y-%m-%d %H:%M:%S')
        GenericPeriod.__init__(self, periodStr)

    def ActivateP(self, now=None):
        "Activate as soon as we pass target datetime."
        if (now is None): now = datetime.datetime.now()
        if (now > self.target):
            return True
        else:
            return False

class EveryDayAt(GenericPeriod):
    """Period for something that happens every day at a specified time.

>>> import Periodicity, datetime
>>> p = Periodicity.EveryDayAt('D=05:06:07')
>>> p.initTime = datetime.datetime(2001,1,1,0,0)
>>> p.ActivateP(datetime.datetime(2001,1,1,1,1))
False
>>> p.ActivateP(datetime.datetime(2001,1,1,8,8))
True
>>> p = Periodicity.EveryDayAt('D=05:06:07')
>>> p.initTime = datetime.datetime(2001,1,1,0,0)
>>> p.ActivateP(datetime.datetime(2001,1,1,1,1))
False
>>> p.ActivateP(datetime.datetime(2001,1,7,8,8,8))
False
>>> p.ActivateP(datetime.datetime(2001,1,5,1,1,1))
False
>>> p.ActivateP(datetime.datetime(2001,1,5,6,6,6))
True
    """

    def __init__(self, periodStr):

        self.typeChar, rest = periodStr.split('=')
        if (self.typeChar not in ['A','D']):
            raise Exception('Could not parse EveryDayAt periodicity from %s.'
                            % periodStr)
        self.timeTarget = datetime.datetime.strptime(rest,'%H:%M:%S')
        self.initTime = datetime.datetime.now()
        GenericPeriod.__init__(self, periodStr)

    def ActivateP(self, now=None):
        """Activate if we are past the target time on the given day.

        We don't activate if we had passed target time when this instance
        was created.
        """
        if (now is None): now = datetime.datetime.now()
        result = False
        
        if (self.typeChar == 'A' or now.weekday() < 5):
            timeTarget = self.timeTarget.replace(
                year=now.year, month=now.month, day=now.day)
            if (now >= timeTarget and timeTarget >= self.initTime):
                result = True
                self.initTime = now
            
        return result

class SomeDaysAt(GenericPeriod):
    """Period for things happening at a specified time on specified days.

>>> import Periodicity, datetime
>>> p = Periodicity.SomeDaysAt('2/4=05:06:07')
>>> p.initTime = datetime.datetime(2001,1,1,0,0)
>>> datetime.date(2001,1,1).weekday()
0
>>> p.ActivateP(datetime.datetime(2001,1,3,1,1))
False
>>> p.ActivateP(datetime.datetime(2001,1,3,8,8))
True
>>> p.ActivateP(datetime.datetime(2001,1,3,8,8)) #initTime moved so not True now
False
    """

    def __init__(self, periodStr):

        self.initTime = datetime.datetime.now()
        self.days, rest = periodStr.split('=')
        self.days = map(int, self.days.split('/'))
        for d in self.days:
            if (d < 0 or d > 6):
                raise Exception('Invalid day %i in days in periodStr %s' % (
                    d, periodStr))
        self.timeTarget = datetime.datetime.strptime(rest,'%H:%M:%S')
        GenericPeriod.__init__(self, periodStr)
        

    def ActivateP(self, now=None):
        """Activate if we are past the target time on the given day.

        We don't activate if we had passed target time when this instance
        was created.
        """
        if (now is None): now = datetime.datetime.now()
        result = False
        
        if (now.weekday() in self.days):
            timeTarget = self.timeTarget.replace(
                year=now.year, month=now.month, day=now.day)
            if (now >= timeTarget and timeTarget >= self.initTime):
                result = True
                self.initTime = now
            
        return result

class ModMinutes(GenericPeriod):
    """Period for things happening at when time is 0 mod the given minutes.

>>> import Periodicity, datetime
>>> p = Periodicity.ModMinutes('M=10',now=datetime.datetime(2001,1,3,1,15))
>>> p.ActivateP(datetime.datetime(2001,1,3,1,15))
False
>>> p.ActivateP(datetime.datetime(2001,1,3,1,10))
False
>>> p.ActivateP(datetime.datetime(2001,1,3,1,20))
True
>>> p.ActivateP(datetime.datetime(2001,1,3,1,20)) # already passed this point
False
>>> p.ActivateP(datetime.datetime(2001,1,3,1,39))
True
>>> p.ActivateP(datetime.datetime(2001,1,3,1,40))
True
    """

    def __init__(self, periodStr, now=None):

        if (now is None): now = datetime.datetime.now()
        letter, minutes = periodStr.split('=')
        if (letter != 'M'):
            raise Exception('Invalid periodStr %s for ModMinutes.' % str(
                periodStr))
        self.minutes = int(minutes)
        if (self.minutes < 0 or self.minutes > 60):
            raise Exception('Invalid minutes in periodStr %s for ModMinutes.'
                            % str(periodStr))
        self.adder = datetime.timedelta(minutes=1)
        self.nextHit = now + self.adder
        while (self.nextHit.minute % self.minutes):
            self.nextHit += self.adder
        GenericPeriod.__init__(self, periodStr)
        

    def ActivateP(self, now=None):
        """Activate if we are past the target time on the given day.
        """
        if (now is None): now = datetime.datetime.now()
        if (now >= self.nextHit):
            self.nextHit = now + self.adder
            while (self.nextHit.minute % self.minutes):
                self.nextHit += self.adder
            return True
        else:
            return False


def ParsePeriod(periodStr, failureMsgPrefix=''):
    """Parse period from string and return GenericPeriod instance.
    
    INPUTS:
    
    -- periodStr:        String that can be parsed as a generic period.

    You can provide the following types of input:

      'None' or ''                       : Never.
      year-month-day hour:minute:second  : Event at single exact date and time.
      A=hour:minute:second               : Time only; every day at this time.
      D=hour:minute:second               : Time only; weekdays at this time.
      <N_1>/<N_2>/.../<N_k>=hour:min:sec : On given days of week at given time.
                                           Monday == 0 ... Sunday == 6.
      M=<M>                              : Whenever minutes mod M == 0.

    -------------------------------------------------------
    
    RETURNS:    Appropriate GenericPeriod instance.
    
    """
    exceptions = []
    classes = [NoPeriod, ExactDateTime, EveryDayAt, SomeDaysAt, ModMinutes]
    for c in classes:
        try:
            return c(periodStr)
        except Exception, e:
            exceptions.append((c,e))
    raise Exception(failureMsgPrefix + '''
    Could not parse periodStr %s. Attempts shown below:\n%s\n
    ''' % (periodStr, '\n'.join(['%s : %s' % (c.__name__, str(e))
                                 for (c, e) in zip(classes, exceptions)])))
    
        

def _test():
    "Test docstrings"
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
    print 'Test finished.'
