# -*- coding: utf-8 -*-

from prettytimedelta.core import PrettyTimedelta

class PolishPrettyTimedelta(PrettyTimedelta):
    day = (u"dzień", u"dni", u"dni")
    hour = (u"godzina", u"godziny", u"godzin", )
    minute = (u"minuta", u"minuty", u"minut")
    second = (u"sekunda", u"sekundy", u"sekund")


    def _declination(self, name, n):
        if n == 1:
            d = 0
        elif n%10>=2 and n%10<=4 and (n%100<10 or n%100>=20):
            d = 1
        else:
            d = 2
        return "%d %s" % (n, name[d])

    def toWords(self):
        words = []

        # Don't let the first item to be 0, eg. "0 days 12 hours"
        if self.days > 0:
            words.append(self._declination(self.day, self.days))
        if self.hours > 0 or len(words) > 0:
            words.append(self._declination(self.hour, self.hours))
        if self.minutes > 0 or len(words) > 0:
            words.append(self._declination(self.minute, self.minutes))

        # Always display number of seconds, even if it's zero
        words.append(self._declination(self.second, self.seconds))
        return ' '.join(words)

