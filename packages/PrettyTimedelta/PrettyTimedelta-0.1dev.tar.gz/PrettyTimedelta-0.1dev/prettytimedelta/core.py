class PrettyTimedelta(object):
    """
    Class for displaying timedelta in (more) readable, ie. human format
    
    """
    def __init__(self, td):
        days, hours, minutes, seconds = self._processTimedelta(td)
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def _processTimedelta(self, td):
        """
        Turns timedelta into tuple (days, hours, minutes, seconds)
        
        """
        minute = 60
        hour = minute * 60

        days = td.days
        seconds = td.seconds
        hours, seconds = divmod(seconds, hour)
        minutes, seconds = divmod(seconds, minute)
        return (days, hours, minutes, seconds)

    def __str__(self):
        return self.toString()

    def toString(self):
        """
        Return timedelta in string format
        
        """
        return "%dd%dh%dm%ds" % \
            (self.days, self.hours, self.minutes, self.seconds)

    def toWords(self):
        """
        Turn timedelta into readable string.

        Must be implemented in subclasses due to i18n.

        """
        return NotImplementedError
