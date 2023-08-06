from dm.ioc import *
from dm.exceptions import KforgeCommandError
from dm.webkit import ValidationError
from dm.webkit import Manipulator
from dm.webkit import htmlescape
from dm.webkit import webkitName, webkitVersion
if webkitName == 'django' and webkitVersion == '1.0':
    from dm.webkit import SortedDict
import re
import dm.webkit

class BaseManipulator(Manipulator):
    "Supertype for domain model manipulators."

    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    commands   = RequiredFeature('CommandSet')
    logger     = RequiredFeature('Logger')
    webkit     = dm.webkit

    sizeSelectMultiple = 4

    base_fields = []  # Django 1.0.

    def getValidationErrors(self, data):
            if webkitName == 'django' and webkitVersion == '1.0':
                self._errors = None
                self.data = data
                self.is_bound = True
                return self.errors
            else:
                try:
                    return self.get_validation_errors(data)
                except Exception, inst:
                    msg = "Exception in 'getValidationErrors' with data %s: %s" % (
                        data, inst
                    )
                    self.logger.error(msg)
                    raise

    def decodeHtml(self, data):
        if webkitName == 'django' and webkitVersion == '0.96':
            return self.do_html2python(data)

    def isTwoCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 2)

    def isThreeCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 3)

    def isFourCharsMin(self, field_data, all_data):
        self.isTooShort(field_data, 4)

    def isFifteenCharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 15)

    def isTwentyCharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 20)

    def is255CharsMax(self, field_data, all_data):
        self.isTooLong(field_data, 255)
  
    def isTooLong(self, field_data, limit):
        if (len(field_data.strip()) > limit):
            raise ValidationError("This field is too long.")
  
    def isTooShort(self, field_data, limit):
        if (len(field_data.strip()) < limit):
            raise ValidationError("This field is too short.")


class DomainObjectManipulator(BaseManipulator):
    "Supertype for domain object manipulators."

    def __init__(self, objectRegister,
            domainObject=None, fieldNames=[], client=None):
        if webkitName == 'django' and webkitVersion == '1.0':
            super(DomainObjectManipulator, self).__init__()
        self.client = client
        self.objectRegister = objectRegister
        self.metaObject = self.objectRegister.getDomainClassMeta()
        self.domainObject = domainObject
        self.fieldNames = fieldNames
        if self.fieldNames == None:
            self.fieldNames = []
        if webkitName == 'django' and webkitVersion == '1.0':
            self.fields = SortedDict()
        else:
            self.fields = []
        msg = "Building manipulator fields for %s..." % (
            self.__class__.__name__
        )
        self.logger.debug(msg)
        self.buildFields()
        if self.fieldNames == []:
            if webkitName == 'django' and webkitVersion == '1.0':
                self.fieldNames = self.fields.keys()
            else:
                self.fieldNames = [field.field_name for field in self.fields]
        msg = "Built '%s' manipulator with field names: %s" % (
            self.__class__.__name__, ", ".join(self.fieldNames)
        )
        self.logger.debug(msg)

    def buildFields(self):
        if self.fieldNames:
            msg = "Building manipulator field objects from fieldNames"
            msg = "%s (%s)." % (msg, ", ".join(self.fieldNames))
            self.logger.debug(msg)
            for fieldName in self.fieldNames:
                metaAttr = self.metaObject.attributeNames[fieldName]
                self.buildField(metaAttr)
        else:
            self.fieldNames = []
            msg = "Manipulator building fields from domain object meta..."
            self.logger.debug(msg)
            for metaAttr in self.metaObject.attributes:
                if not self.isAttrExcluded(metaAttr):
                    self.buildField(metaAttr)

    def isAttrExcluded(self, metaAttr):
        if self.isAttrNameExcluded(metaAttr.name):
            return True
        if not metaAttr.isEditable:
            return True
        return False

    def isAttrNameExcluded(self, attrName):
        if self.fieldNames and not attrName in self.fieldNames:
            return True
        return False
    
    def buildField(self, metaAttr):
        field = None
        isFieldRequired = metaAttr.isRequired
        self.logger.debug("Building manipulator field: %s" % metaAttr.name)

        if metaAttr.isAssociateList:
            countChoices = metaAttr.countChoices(self.domainObject)
            choices = metaAttr.getAllChoices(self.domainObject)
            if webkitName == 'django' and webkitVersion == '1.0':
                field = self.webkit.ChoiceField(
                    required=isFieldRequired,
                    choices=choices,
                )
            elif webkitName == 'django' and webkitVersion == '0.96':
                field = self.webkit.SelectMultipleField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                    choices=choices,
                    size=self.sizeSelectMultiple,
                )
            elif webkitName == 'pylons':
                field = self.webkit.SelectField(
                    metaAttr.name,
                    multiple=True,
                )
        elif metaAttr.isDomainObjectRef:
            countChoices = metaAttr.countChoices(self.domainObject)
            # Todo: Revert this 'True', and introduce Ajax auto-completion
            # instead of drop-down when more than count limit.
            if True or countChoices <= 50:
                choices = metaAttr.getAllChoices(self.domainObject)
                choices = [('', '-- select option --')] + choices
                if webkitName == 'django' and webkitVersion == '1.0':
                    field = self.webkit.ChoiceField(
                        required=isFieldRequired,
                        choices=choices,
                    )
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.SelectField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                        choices=choices,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.SelectField(
                        metaAttr.name,
                    )
            else:  # need to find a way to only do this for string keys
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.TextField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
        elif metaAttr.isValueObject():
            if metaAttr.typeName == 'String':
                if metaAttr.name[0:5] == 'email':
                    if webkitName == 'django' and webkitVersion == '1.0':
                        field = self.webkit.EmailField(
                            required=isFieldRequired,
                        )
                    elif webkitName == 'django' and webkitVersion == '0.96':
                        field = self.webkit.EmailField(
                            field_name=metaAttr.name,
                            is_required=isFieldRequired,
                            length=35
                        )
                    elif webkitName == 'pylons':
                        field = self.webkit.TextField(
                            metaAttr.name,
                            size=36
                        )
                else:
                    if webkitName == 'django' and webkitVersion == '1.0':
                        field = self.webkit.Field(
                            required=isFieldRequired,
                        )
                    elif webkitName == 'django' and webkitVersion == '0.96':
                        field = self.webkit.TextField(
                            field_name=metaAttr.name,
                            is_required=isFieldRequired,
                        )
                    elif webkitName == 'pylons':
                        field = self.webkit.TextField(
                            metaAttr.name,
                            size=40
                        )
                
            elif metaAttr.typeName == 'Text':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.LargeTextField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                        cols=30,
                        rows=8,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'MarkdownText':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.LargeTextField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                        cols=30,
                        rows=8,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'Password':
                if webkitName == 'django' and webkitVersion == '1.0':
                    field = self.webkit.Field(
                        required=isFieldRequired,
                        widget=dm.webkit.widgets.PasswordInput,
                    )
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.PasswordField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'Integer':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.IntegerField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'Boolean':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.CheckboxField(
                        field_name=metaAttr.name
                        # doesn't accept 'is_required' parameter
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'Url':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.URLField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'DateTime':
                if webkitName == 'django' and webkitVersion == '1.0':
                    field = self.webkit.DateTimeField(
                        required=isFieldRequired,
                    )
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.DatetimeField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'Date':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.DateField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            elif metaAttr.typeName == 'RDate':
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.RDateField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
            else:
                if webkitName == 'django' and webkitVersion == '1.0':
                    raise Exception("No field yet.")
                elif webkitName == 'django' and webkitVersion == '0.96':
                    field = self.webkit.TextField(
                        field_name=metaAttr.name,
                        is_required=isFieldRequired,
                    )
                elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
        elif metaAttr.typeName == 'ImageFile':
            if webkitName == 'django' and webkitVersion == '1.0':
                raise Exception("No field yet.")
            elif webkitName == 'django' and webkitVersion == '0.96':
                field = self.webkit.FileUploadField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif webkitName == 'pylons':
                    field = self.webkit.TextField(
                        metaAttr.name,
                        size=40
                    )
        if field:
            if webkitName == 'django' and webkitVersion == '1.0':
                field.metaAttr = metaAttr
                field.field_name = metaAttr.name
                field.field_title = metaAttr.calcTitle()
                field.field_comment = metaAttr.comment
                self.fields[metaAttr.name] = field
            elif webkitName == 'django' and webkitVersion == '0.96':
                field.metaAttr = metaAttr
                field.field_title = metaAttr.calcTitle()
                field.field_comment = metaAttr.comment
                self.fields.append(field)
            elif webkitName == 'pylons':
                self.fields.append(field)
        else:
            message = "No form field for meta attribute: %s" % metaAttr
            self.logger.critical(message)
            raise Exception, message

    def create(self, data):
        # todo: rename 'data'
        self.data = data
        self.createObjectKwds()
        self.createDomainObject()
        self.setAssociateListAttributes()
        
    def createObjectKwds(self):
        self.objectKwds = {}
        fieldedAttrs = self.getFieldedMetaAttrs()
        domValues = self.presentationToDomainValues(self.data, fieldedAttrs)
        for (attrName, domValue) in domValues.items():
            if not domValue == None:
                self.objectKwds[attrName] = domValue

    def createDomainObject(self):
        commandClass = self.getCreateCommandClass()
        if commandClass:
            objectKwds = self.objectKwds
            command = commandClass(**objectKwds)
        else:
            commandClass = self.getCommandClass('DomainObjectCreate')
            commandKwds = {}
            commandKwds['typeName'] = self.metaObject.name
            commandKwds['objectKwds'] = self.objectKwds
            command = commandClass(**commandKwds)
        command.execute()
        if not command.object:
            raise Exception, "Create command did not produce an object."
        self.domainObject = command.object

    def getCreateCommandClass(self):
        return self.getDomainObjectCommandClass('Create')
        
    def getDomainObjectCommandClass(self, actionName):
        domainClassName = self.metaObject.name
        commandClassName = domainClassName + actionName
        return self.getCommandClass(commandClassName)
        
    def getCommandClass(self, className):
        if className in self.commands:
            return self.commands[className]
        return None

    def getFieldedMetaAttrs(self):
        metaAttrs = {}
        for metaAttr in self.metaObject.attributes:
            if not metaAttr.isAssociateList:
                if metaAttr.name in self.fieldNames:
                    if metaAttr.name in self.data:
                        metaAttrs[metaAttr.name] = metaAttr
        return metaAttrs

    # Todo: Rename MultiValueDict as PresentationObject.
    def presentationToDomainValues(self, multiValueDict, fieldedAttrs):
        domValues = {}
        for (attrName, metaAttr) in fieldedAttrs.items():
            try:
                domValue = metaAttr.makeValueFromMultiValueDict(multiValueDict)
                domValues[attrName] = domValue
            except Exception, inst:
                msg = "Can't make '%s' value from multi-value dict: %s" % (
                    attrName, multiValueDict
                )
                self.logger.error(msg)
                raise
        return domValues

    def update(self, data):
        self.data = data
        self.setNonAssociateListAttributes()
        self.setAssociateListAttributes()

    def setNonAssociateListAttributes(self):
        self.setAttributesFromMultiValueDict(self.domainObject, self.data)
        self.domainObject.save()
       
    def setAttributesFromMultiValueDict(self, domainObject, multiValueDict):
        fieldedAttrs = self.getFieldedMetaAttrs()
        attrValues = self.presentationToDomainValues(multiValueDict, fieldedAttrs)
        for attrName in fieldedAttrs:
            metaAttr = fieldedAttrs[attrName]
            attrValue = attrValues[attrName]
            if attrValue != metaAttr.getAttributeValue(domainObject):
                msg = "Setting '%s' attribute to '%s'." % (attrName, attrValue)
                self.logger.debug(msg)
                metaAttr.setAttributeValue(domainObject, attrValue)

    def setAssociateListAttributes(self):
        for metaAttr in self.metaObject.attributes:
            if metaAttr.isAssociateList:
                self.setAssociateListAttribute(metaAttr)
           
    def setAssociateListAttribute(self, metaAttr):
        if metaAttr.name in self.fieldNames:
            if self.data.has_key(metaAttr.name):
                metaAttr.setAttributeFromMultiValueDict(
                    self.domainObject, self.data
                )

    def getAttributeField(self, attrName):
        for field in self.fields:
            if attrName == field.field_name:
                return field
        return None

    def getUpdateParams(self):
        initialParams = self.domainObject.asRequestParams()
        if webkitName == 'django' and webkitVersion == '1.0':
            self.initial = initialParams
        return initialParams


class HasManyManipulator(DomainObjectManipulator):
    "Domain object 'HasMany' attribute manipulator."

    def isAttrExcluded(self, metaAttr):
        if DomainObjectManipulator.isAttrExcluded(self, metaAttr):
            return True 
        if metaAttr.isAssociateList:
            return True
        return False

    def isAttrNameExcluded(self, attrName):
        if attrName == self.objectRegister.ownerName:
            return True
        if attrName == self.objectRegister.ownerName2:
            return True
        if attrName == 'state':
            return True
        return False
    
    def createDomainObject(self):
        objectKwds = self.objectKwds
        self.domainObject = self.objectRegister.create(**objectKwds)


class FormWrapper(object):
    """
    A wrapper linking a Manipulator to the template system.
    This allows dictionary-style lookups of formfields. It also handles feeding
    prepopulated data and validation error messages to the formfield objects.
    """
    
    def __init__(self, manipulator, data, error_dict): 
        self.manipulator = manipulator
        self.data = data
        self.error_dict = error_dict
        self.fields = self.wrapManipulatorFields()
#        self.plugin_fields = self.wrapPluginFields()

    def __repr__(self):
        return repr(self.data)

    def wrapManipulatorFields(self):
        wrappedFields = []
        if webkitName == 'django' and webkitVersion == '1.0':
            for fieldName in self.manipulator.fields.keys():
                boundField = self.manipulator.__getitem__(fieldName)
                wrappedField = self.wrapField(fieldName, boundField)
                wrappedFields.append(wrappedField)
        elif webkitName == 'django' and webkitVersion == '0.96':
            for field in self.manipulator.fields:
                if hasattr(field, 'requires_data_list') and hasattr(self.data, 'getlist'):
                    data = self.data.getlist(field.field_name)
                else:
                    data = self.data.get(field.field_name, None)
                if data is None:
                    data = ''
                wrappedField = FormFieldWrapper(field, data, self.error_dict.get(field.field_name, []))
                wrappedFields.append(wrappedField)
        return wrappedFields

    def wrapPluginFields(self):
        wrappedFields = []
        if not hasattr(self.manipulator, 'pluginFields'):
            return wrappedFields
        for pluginField in self.manipulator.pluginFields:
            indication = ""
            if pluginField.is_required:
                indication = "<strong>*</strong>"
            wrappedField = "<label for=\"id_%s\">%s %s</label><br />" % (
                pluginField.field_name,
                pluginField.field_title,
                indication
            )
            wrappedField += "%s <br />" % self[pluginField.field_name]
            wrappedField += "<p class=\"desc\">%s</p>" % pluginField.field_comment
            wrappedFields.append(wrappedField)

        return wrappedFields

    def wrapField(self, fieldName, field): 
        field.field_name = fieldName
        data = self.data.get(fieldName, None)
        if data is None:
            data = ''
        error_list = self.error_dict.get(fieldName, [])
        return FormFieldWrapper(field, data, error_list)

    def __getitem__(self, key):
        if webkitName == 'django' and webkitVersion == '1.0':
            fieldName = key
            boundField = self.manipulator.__getitem__(fieldName)
            return self.wrapField(fieldName, boundField)
        elif webkitName == 'django' and webkitVersion == '0.96':
            for field in self.manipulator.fields:
                if field.field_name == key:
                    if hasattr(field, 'requires_data_list') and hasattr(self.data, 'getlist'):
                        data = self.data.getlist(field.field_name)
                    else:
                        data = self.data.get(field.field_name, None)
                    if data is None:
                        data = ''
                    error_list = self.error_dict.get(field.field_name, [])
                    return FormFieldWrapper(field, data, error_list)
        raise KeyError

    def has_errors(self):
        return self.error_dict != {}


class FormFieldWrapper(object):
    "A bridge between the template system and an individual form field. Used by FormWrapper."
    
    def __init__(self, formfield, data, error_list):
        self.formfield, self.data, self.error_list = formfield, data, error_list
        self.field_name = self.formfield.field_name
        if webkitName == 'django' and webkitVersion == '1.0':
            if hasattr(self.formfield.field, 'field_title'):
                self.field_title = self.formfield.field.field_title
            if hasattr(self.formfield.field, 'field_comment'):
                self.field_comment = self.formfield.field.field_comment
        elif webkitName == 'django' and webkitVersion == '0.96':
            if hasattr(self.formfield, 'field_title'):
                self.field_title = self.formfield.field_title
            if hasattr(self.formfield, 'field_comment'):
                self.field_comment = self.formfield.field_comment
        self.error = self.makeErrorMessage()

    def makeErrorMessage(self):
        message = ''
        if webkitName == 'django' and webkitVersion == '1.0':
            if len(self.error_list):
                from django.utils.html import conditional_escape
                from django.utils.encoding import force_unicode
                from django.utils.safestring import mark_safe
                message = mark_safe(conditional_escape(force_unicode(self.error_list[0])))
        elif webkitName == 'django' and webkitVersion == '0.96':
            if len(self.error_list):
                message =  htmlescape(self.error_list[0])
        thisFieldPattern = re.compile('This field')
        thisValuePattern = re.compile('this value')
        validValuePattern = re.compile('valid value')
        confirmationPattern = re.compile('confirmation')
        underscorePattern = re.compile('_')
        fieldName = self.field_name
        message = thisFieldPattern.sub(fieldName.capitalize(), message)
        message = thisValuePattern.sub(fieldName, message)
        message = validValuePattern.sub('valid '+fieldName, message)
        message = confirmationPattern.sub(' confirmation', message)
        message = underscorePattern.sub(' ', message)
        return message

    def __unicode__(self):
        if webkitName == 'django' and webkitVersion == '1.0':
            from django.utils.html import conditional_escape
            from django.utils.encoding import force_unicode
            from django.utils.safestring import mark_safe
            html = (force_unicode(self.formfield))
            if self.error_list:
                html = u'<div class="field-with-error">' + html + u'</div>'
            return mark_safe(html)
        elif webkitName == 'django' and webkitVersion == '0.96':
            return self.__str__()

    def __str__(self):
        "Renders the field"
        if webkitName == 'django' and webkitVersion == '1.0':
            return self.__unicode__()
        elif webkitName == 'django' and webkitVersion == '0.96':
            html = str(self.formfield.render(self.data))
            if self.error_list:
                return '<div class="field-with-error">' + html + '</div>'
            else:
                return html

    def __repr__(self):
        return '<FormFieldWrapper for "%s">' % self.formfield.field_name
    
    def field_list(self):
        """
        Like __str__(), but returns a list. Use this when the field's render()
        method returns a list.
        """
        return self.formfield.render(self.data)

    def errors(self):
        return self.error_list

    def html_error_list(self):
        if webkitName == 'django' and webkitVersion == '1.0':
            return self.errors_list.as_ul()
        elif webkitName == 'django' and webkitVersion == '0.96':
            if self.errors_list:
                return '<ul class="errorlist"><li>%s</li></ul>' % '</li><li>'.join([htmlescape(e) for e in self.errors_list])
            else: 
                return ''

