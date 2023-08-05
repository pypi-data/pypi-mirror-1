import mx.DateTime
import datetime

class DateTimeConvertor(object):  
    "Converts between HTML (string) and python (mx.DateTime.DateTime)."
        
    def fromHTML(self, dateTimeString):
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
        return "%s-%s-%s %s:%s:%s" % (
            str(dateTimeObject.year).zfill(4),
            str(dateTimeObject.month).zfill(2),
            str(dateTimeObject.day).zfill(2),
            str(dateTimeObject.hour).zfill(2),
            str(dateTimeObject.minute).zfill(2),
            str(int(dateTimeObject.second)).zfill(2),
        )

