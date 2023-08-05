from dm.ioc import *
from dm.exceptions import KforgeCommandError
from django import forms as djangoforms
from django.core import validators as djangovalidators
from django.utils.html import escape

import re

class BaseManipulator(djangoforms.Manipulator):
    "Supertype for domain model manipulators."

    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    commands   = RequiredFeature('CommandSet')
    logger     = RequiredFeature('Logger')

    def getValidationErrors(self, data):
        return self.get_validation_errors(data)

    def decodeHtml(self, data):
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
            raise djangovalidators.ValidationError("This field is too long.")
  
    def isTooShort(self, field_data, limit):
        if (len(field_data.strip()) < limit):
            raise djangovalidators.ValidationError("This field is too short.")


class DomainObjectManipulator(BaseManipulator):
    "Supertype for domain object manipulators."

    def __init__(self, objectRegister, domainObject=None, fieldNames=[]):
        self.objectRegister = objectRegister
        self.metaObject = self.objectRegister.getDomainClassMeta()
        self.domainObject = domainObject
        self.fieldNames = fieldNames
        self.fields = []
        self.buildFields()

    def buildFields(self):
        msg = "Building manipulator fields for %s manipulator." % (
            self.__class__.__name__
        )
        self.logger.debug(msg)
        if self.fieldNames:
            msg = "Building manipulator fields from fieldNames..."
            self.logger.debug(msg)
            for fieldName in self.fieldNames:
                for metaAttr in self.metaObject.attributes:
                    if metaAttr.name == fieldName:
                        self.buildField(metaAttr)
        else:
            msg = "Building manipulator fields from meta attributes..."
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
            if countChoices <= 50:
                choices = metaAttr.getAllChoices(self.domainObject)
                field = djangoforms.SelectMultipleField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                    choices=choices,
                    size=4,
                )
            else:
                field = djangoforms.TextField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
        elif metaAttr.isDomainObjectRef:
            countChoices = metaAttr.countChoices(self.domainObject)
            if countChoices <= 50:
                choices = metaAttr.getAllChoices(self.domainObject)
                choices = [('', '-- select option --')] + choices
                field = djangoforms.SelectField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                    choices=choices,
                )
            else:
                field = djangoforms.TextField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
        elif metaAttr.isValueObject():
            if metaAttr.typeName == 'Text':
                field = djangoforms.LargeTextField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif metaAttr.typeName == 'Password':
                field = djangoforms.PasswordField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif metaAttr.typeName == 'Integer':
                field = djangoforms.IntegerField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif metaAttr.typeName == 'Url':
                field = djangoforms.URLField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif metaAttr.typeName == 'DateTime':
                field = djangoforms.DatetimeField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            elif metaAttr.typeName == 'Date':
                field = djangoforms.DateField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
            else:
                field = djangoforms.TextField(
                    field_name=metaAttr.name,
                    is_required=isFieldRequired,
                )
        if field:
            field.metaAttr = metaAttr
            field.field_comment = metaAttr.comment
            self.fields.append(field)
        else:
            message = "No form field for meta attribute: %s" % metaAttr
            self.logger.critical(message)
            raise message

    def create(self, data):
        # todo: rename 'data'
        self.data = data
        self.createObjectKwds()
        self.createDomainObject()
        self.setAssociateListAttributes()
        
    def createObjectKwds(self):
        self.objectKwds = {}
        for metaAttr in self.metaObject.attributes:
            if not metaAttr.isAssociateList:
                if self.data.has_key(metaAttr.name):
                    attrValue = metaAttr.makeValueFromMultiValueDict(
                        self.data
                    )
                    if not attrValue == None:
                        self.objectKwds[metaAttr.name] = attrValue

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
            raise "Create command did not produce an object."
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

    def setAssociateListAttributes(self):
        for metaAttr in self.metaObject.attributes:
            if metaAttr.isAssociateList:
                self.setAssociateListAttribute(metaAttr)
           
    def setAssociateListAttribute(self, metaAttr):
        if self.data.has_key(metaAttr.name):
            metaAttr.setAttributeFromMultiValueDict(
                self.domainObject, self.data
            )

    def update(self, data):
        self.data = data
        self.setNonAssociateListAttributes()
        self.setAssociateListAttributes()

    def setNonAssociateListAttributes(self):
        for metaAttr in self.metaObject.attributes:
            if not metaAttr.isAssociateList:
                if self.data.has_key(metaAttr.name):
                    metaAttr.setAttributeFromMultiValueDict(
                        self.domainObject, self.data
                    )
        self.domainObject.save()
        
    def getAttributeField(self, attrName):
        for field in self.fields:
            if attrName == field.field_name:
                return field
        return None


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
            indicateRequired = ""
            if pluginField.is_required:
                indicateRequired = "<strong>*</strong>"
            wrappedField = "<label for=\"id_%s\">%s %s</label><br />" % (pluginField.field_name, pluginField.field_title, indicateRequired)
            wrappedField += "%s <br />" % self[pluginField.field_name]
            wrappedField += "<p class=\"desc\">%s</p>" % pluginField.field_comment
            wrappedFields.append(wrappedField)

        return wrappedFields

    def __getitem__(self, key):
        for field in self.manipulator.fields:
            if field.field_name == key:
                if hasattr(field, 'requires_data_list') and hasattr(self.data, 'getlist'):
                    data = self.data.getlist(field.field_name)
                else:
                    data = self.data.get(field.field_name, None)
                if data is None:
                    data = ''
                return FormFieldWrapper(field, data, self.error_dict.get(field.field_name, []))
        raise KeyError

    def has_errors(self):
        return self.error_dict != {}

class FormFieldWrapper(object):
    "A bridge between the template system and an individual form field. Used by FormWrapper."
    
    def __init__(self, formfield, data, error_list):
        self.formfield, self.data, self.error_list = formfield, data, error_list
        self.field_name = self.formfield.field_name
        if hasattr(self.formfield, 'field_title'):
            self.field_title = self.formfield.field_title
        if hasattr(self.formfield, 'field_comment'):
            self.field_comment = self.formfield.field_comment
        self.error = self.makeErrorMessage()

    def makeErrorMessage(self):
        if len(self.error_list):
            message =  escape(self.error_list[0])
            thisFieldPattern = re.compile('This field')
            confirmationPattern = re.compile('confirmation')
            underscorePattern = re.compile('_')
            fieldName = self.field_name
            message = thisFieldPattern.sub(fieldName.capitalize(), message)
            message = confirmationPattern.sub(' confirmation', message)
            message = underscorePattern.sub(' ', message)
            return message
        else:
            return ''

    def __str__(self):
        "Renders the field"
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
        if self.errors():
            return '<ul class="errorlist"><li>%s</li></ul>' % '</li><li>'.join([escape(e) for e in self.errors()])
        else: 
            return ''
                    
