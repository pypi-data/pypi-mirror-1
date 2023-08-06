##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.i18nmessageid

from z3c.form import widget

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form import widget
from z3c.form import validator
from z3c.form import converter
from z3c.form.browser import text

from p01.widget.password import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class PasswordConfirmationWidget(text.TextWidget):
    """Input type password widget implementation."""
    zope.interface.implementsOnly(interfaces.IPasswordConfirmationWidget)

    css = u'passwordWidget'


@zope.component.adapter(zope.schema.interfaces.IPassword, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def PasswordConfirmationFieldWidget(field, request):
    """IFieldWidget factory for PasswordConfirmationWidget."""
    return widget.FieldWidget(field, PasswordConfirmationWidget(request))


class PasswordRequiredValue(object):
    """Knows if input is required or not."""

    zope.interface.implements(IValue)
    zope.component.adapts(zope.interface.Interface, zope.interface.Interface,
        zope.interface.Interface, zope.schema.interfaces.IPassword, 
        interfaces.IPasswordConfirmationWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def get(self):
        """Returns the value for the required field."""
        if self.field.required == True and \
            self.widget.value != self.field.missing_value:
            # change the required flag at the field
            self.field.required = False
        return self.field.required


class PasswordComparsionError(zope.schema.ValidationError):
    __doc__ = _("""Password doesn't compare with confirmation value""")


class PasswordConfirmationDataConverter(converter.FieldDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    zope.component.adapts(
        zope.schema.interfaces.IFromUnicode, 
        interfaces.IPasswordConfirmationWidget)
    zope.interface.implements(IDataConverter)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        # check for empty form input
        confirm = self.widget.request.get(self.widget.name + '.confirm', None)
        if value == u'' and confirm == u'' and self.field.required == False:
            # if there is a empty value, we return the field value if widget 
            # was set to required = False by the PasswordRequiredValue adapter
            return self.field.query(self.widget.context)
        return self.field.fromUnicode(value)


class PasswordConfirmationValidator(validator.SimpleFieldValidator):
    """Simple Field Validator"""
    zope.interface.implements(IValidator)
    zope.component.adapts(
        zope.interface.Interface,
        zope.interface.Interface,
        zope.interface.Interface,
        zope.schema.interfaces.IPassword,
        interfaces.IPasswordConfirmationWidget)

    def validate(self, value):
        """See interfaces.IValidator"""
        # we get a value if the password is equal to the confirmation value or
        # if password and confirmation is empty, we get the existing value 
        # stored in the field

        # don't validate emtpy value if widget was set to required = False by 
        # the PasswordRequiredValue adapter
        requestValue = self.request.get(self.widget.name, 1)
        confirmValue = self.request.get(self.widget.name + '.confirm', 2)
        if confirmValue == u'' and requestValue == u'' and \
            self.field.required == False:
            return

        # compare both field values with each others
        if requestValue != confirmValue:
            raise PasswordComparsionError

        # default validation if we not allready get done
        field = self.field
        if self.context is not None:
            field = field.bind(self.context)
        return field.validate(value)
