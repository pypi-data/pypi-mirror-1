import mx.DateTime
import datetime

class DateTimeConvertor(object):  
    "Converts between HTML (string) and python (mx.DateTime.DateTime)."
        
    def fromHTML(self, dateTimeString):
        if dateTimeString in ['', None]:
            return None
        if dateTimeString.__class__ == datetime.datetime:
            dateTimeString = str(dateTimeString)
        (date, time) = dateTimeString.split()
        (year, month, day) = date.split('-')
        (hour, min, sec) = time.split(':')
        return mx.DateTime.DateTime(
            int(year), int(month), int(day),
            int(hour), int(min), int(sec)
        )

    def toHTML(self, dateTimeObject):
        if dateTimeObject in ['', None]:
            return ''
        return "%s-%s-%s %s:%s:%s" % (
            str(dateTimeObject.year).zfill(4),
            str(dateTimeObject.month).zfill(2),
            str(dateTimeObject.day).zfill(2),
            str(dateTimeObject.hour).zfill(2),
            str(dateTimeObject.minute).zfill(2),
            str(int(dateTimeObject.second)).zfill(2),
        )

class DateConvertor(object):  
    "Converts between HTML (string) and python (mx.DateTime.Date)."
        
    def fromHTML(self, dateString):
        if dateString in ['', None]:
            return None
        if dateString.__class__ == datetime.date:
            dateString = str(dateString)
        (yearString, monthString, dayString) = dateString.split('-')
        return mx.DateTime.Date(
            int(yearString), int(monthString), int(dayString),
        )

    def toHTML(self, dateObject):
        if dateObject in ['', None]:
            return ''
        return "%s-%s-%s" % (
            str(dateObject.year).zfill(4),
            str(dateObject.month).zfill(2),
            str(dateObject.day).zfill(2),
        )

