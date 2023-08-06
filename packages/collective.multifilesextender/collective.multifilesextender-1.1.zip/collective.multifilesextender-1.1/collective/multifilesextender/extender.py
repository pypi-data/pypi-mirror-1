from Products.Archetypes.atapi import AnnotationStorage

from archetypes.schemaextender.field import ExtensionField

from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender

from archetypes.multifile.MultiFileField import MultiFileField
from archetypes.multifile.MultiFileWidget import MultiFileWidget

from collective.multifilesextender import multiMessageFactory as _

from collective.multifilesextender.interfaces import IMultiFileLayer, IMultiFileExtendable

class ExMultiFileField(ExtensionField, MultiFileField):
    """ A multifile field """

class MultiFileExtender(object):
    adapts(IMultiFileExtendable)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IMultiFileLayer

    fields = [
        ExMultiFileField('multifile',
                  languageIndependent=True,
                  storage = AnnotationStorage(migrate=True),
                  widget = MultiFileWidget(
                            description = _(u"Select the file to be added by clicking the 'Browse' button."),
                            label= _(u"Attachments"),
                            show_content_type = False,))
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields