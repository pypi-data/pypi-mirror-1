from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View
from Products.CMFCore.Expression import getExprContext
from Products.Archetypes.atapi import Schema
from Products.Archetypes.Field import StringField
from Products.Archetypes.Widget import StringWidget
from Products.ATContentTypes.content.base import registerATCT

from Products.TALESField import TALESString
from Products.PloneFormGen.content.fields import FGStringField
from Products.PloneFormGen.content.fieldsBase import finalizeFieldSchema

from quintagroup.ploneformgen.readonlystringfield.widget import ReadonlyStringWidget
from quintagroup.ploneformgen.readonlystringfield.config import PROJECTNAME

class FGReadonlyStringField(FGStringField):
    """ A string entry field """

    security  = ClassSecurityInfo()

    schema = FGStringField.schema.copy() + Schema((
        TALESString('editMode',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default='',
            widget=StringWidget(label="Edit Mode Expression",
                description="""
                    A TALES expression that will be evaluated when the form is displayed
                    to know whether or not to make field editable.
                    Leave empty if you need read only field in any case. Your expression
                    should evaluate as a string.
                    PLEASE NOTE: errors in the evaluation of this expression will cause
                    an error on form display.
                """,
                size=70,
                i18n_domain = "quintagroup.ploneformgen.readonlystringfield",
                label_msgid = "label_editmode_text",
                description_msgid = "help_editmode_text",
                ),
            ),
    ))

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormReadonlyStringField'
    archetype_name = 'Readonly String Field'
    content_icon = 'StringField.gif'
    typeDescription= 'A readonly string field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        super(FGReadonlyStringField, self).__init__(oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_string_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators=('isNotTooLong',),
            widget=ReadonlyStringWidget(),
            )

    def fgPrimeDefaults(self, request, contextObject=None):
        super(FGReadonlyStringField, self).fgPrimeDefaults(request,
            contextObject=contextObject)
        editable = self.isEditable(contextObject)
        if editable:
            request.set('%s_editable' % self.fgField.__name__, '1')

    def isEditable(self, context=None):
        if self.getRawEditMode():
            if context:
                value = self.getEditMode(
                    expression_context=getExprContext(self, context))
            else:
                value = self.getEditMode()
            return value
        return False

registerATCT(FGReadonlyStringField, PROJECTNAME)
