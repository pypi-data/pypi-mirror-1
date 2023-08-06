# Todo: Make this switch between Django, Pylons, etc.
from dm.exceptions import WebkitError
from dm.dictionarywords import WEBKIT_NAME
from dm.ioc import RequiredFeature

dictionary = RequiredFeature('SystemDictionary')
webkitName = dictionary[WEBKIT_NAME]

if not webkitName:
    pass
elif webkitName == 'django':
    import django
    from django.utils.html import escape as htmlescape
    from django.forms import validators
    from django.forms import Manipulator
    from django.forms import SelectField, SelectMultipleField, TextField
    from django.forms import TextField, LargeTextField
    from django.forms import PasswordField, IntegerField, SmallIntegerField
    from django.forms import PositiveIntegerField, URLField, CheckboxField
    from django.forms import DatetimeField, DateField, TimeField
    from django.forms import FileUploadField, EmailField, RadioSelectField
    from django.core.validators import ValidationError
    from django.template import Context
    from django.core import template_loader
    from django.http import HttpRequest
    from django.http import HttpResponse
    from django.http import HttpResponseRedirect

elif webkitName == 'pylons':
    import pylons
    from webhelpers import *
    from cgi import escape as htmlescape
    class Manipulator(object): pass
    SelectField = select
    SelectMultipleField = None
    TextField = text_field
    LargeTextField = text_area
    PasswordField = text_field
    IntegerField = text_field
    class URLField(object): pass
    class CheckboxField(object): pass
    class DatetimeField(object): pass
    class DateField(object): pass
    class FileUploadField(object): pass
    EmailField = text_field
    class ValidationError(object): pass
    class HttpRequest(object): pass
    class HttpResponse(object): pass
    class HttpResponseRedirect(object): pass
    class Context(object): pass
    class template_loader(object): pass

else:
    raise WebkitError, "No support available for '%s' webkit." % webkitName




## Django extensions, without a home. Perhaps push back into ScanBooker?
#

if webkitName == 'django':

    import sre
    _rdatere = r'((?:0?[1-9])|(?:[12][0-9])|(?:3[0-1]))-((?:0?[1-9])|(?:1[0-2]))-(19|2\d)\d{2}'
    ransi_date_re = sre.compile('^%s$' % _rdatere)

    class RDateField(DateField):
        """Automatically converts its data to a datetime.date object.
        The data should be in the format DD-MM-YYYY"""
    
        def isValidDate(self, field_data, all_data):
            try:
                if not ransi_date_re.search(field_data):
                    raise ValidationError(
                        'Enter a valid date in DD-MM-YYYY format.'
                    )
            except ValidationError, e:
                raise validators.CriticalValidationError, e.messages
    
        def html2python(data):
            "Converts the field into a datetime.date object"
            import time, datetime
            try:
                t = time.strptime(data, '%d-%m-%Y')
                return datetime.date(t[0], t[1], t[2])
            except (ValueError, TypeError):
                return None
                
        html2python = staticmethod(html2python)

