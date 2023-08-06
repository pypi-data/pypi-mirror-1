from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi
from Products.CMFPlone import PloneMessageFactory as _

class ExtendedBooleanField(ExtensionField, atapi.BooleanField):
    """ """

class SchemaExtender(object):
    """ Extend a file to add the 'Auto-translate checkbox' """
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    _fields = [
            ExtendedBooleanField('cleanWordPastedText',
                schemata='settings',
                languageIndependent=True,
                default=True,
                widget=atapi.BooleanWidget(
                    label = _(
                        u'label_clean_word_pasted_text', 
                        default=u'Automatically clean MSWord pasted text?',
                    ),
                    description=_(
                        u'description_clean_word_pasted_text', 
                        default=u"Choose this option if you want the "
                        "HTML of this object's Rich-Text fields to be "
                        "cleaned up. <br/> WARNING: This may result in loss "
                        "of text formatting."
                    ),
                ),
            ),
            ]

    def getFields(self):
        """ get fields """
        return self._fields


