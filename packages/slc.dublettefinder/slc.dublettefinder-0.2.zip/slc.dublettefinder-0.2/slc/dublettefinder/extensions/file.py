import logging

from zope.interface import implements

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import ISchema
from Products.validation.chain import ValidationChain

from slc.dublettefinder.interfaces import IDubletteFinderLayer

log = logging.getLogger('slc.dublettefinder.extensions.file.py')

FILE_FIELD_TYPES = ['file','image','blob']

class ExtendedComputedField(ExtensionField, atapi.ComputedField):
    """ """
    def getFileNames(self, obj):
        names = []
        fields = ISchema(obj).fields()
        for f in fields:
            if f.type in FILE_FIELD_TYPES:
                file = f.get(obj)
                if file:
                    names.append(file.filename)
        return names

    def getFileSizes(self, obj):
        sizes = []
        fields = ISchema(obj).fields()
        for f in fields:
            if f.type in FILE_FIELD_TYPES:
                file = f.get(obj)
                if file:
                    sizes.append(file.get_size())
        return sizes


class FileDubletteExtender(object):
    """ Add ignore flags and validators for all file fields.
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IDubletteFinderLayer

    fields = [
        ExtendedComputedField(
            name='fileNames',
            expression="context.Schema().get('fileNames').getFileNames(context)",
            widget=atapi.ComputedField._properties['widget'](
                visible={'edit' : 'hidden', 'view':'invisible'},
                label='File Name',
                label_msgid='dublettefinder_label_fileNames',
                i18n_domain='slc.dublettefinder',
            )
        ),
        ExtendedComputedField(
            name='fileSizes',
            expression="context.Schema().get('fileSizes').getFileSizes(context)",
            widget=atapi.ComputedField._properties['widget'](
                visible={'edit' : 'hidden', 'view':'invisible'},
                label='File Size',
                label_msgid='dublettefinder_label_fileSizes',
                i18n_domain='slc.dublettefinder',
            )
        ),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class ValidatorModifer(object):
    """ This is a schema modifier that adds the dublette validators to the file
        fields of an object.
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IDubletteFinderLayer

    def __init__(self, context):
        self.context = context
    
    def fiddle(self, schema):
        """Fiddle the schema.

        This is a copy of the class' schema, with any ISchemaExtender-provided
        fields added. The schema may be modified in-place: there is no
        need to return a value.

        In general, it will be a bad idea to delete or materially change
        fields, since other components may depend on these ones.

        If you change any fields, then you are responsible for making a copy of
        them first and place the copy in the schema.
        """
        fields = schema.fields()
        file_fields = [f for f in fields if f.type in FILE_FIELD_TYPES]
        for f in file_fields:
            field = f.copy()

            field.widget.macro = 'dublettefinder_file'

            validator_names = [v[0].name for v in field.validators]
            if 'isUniqueFileName' not in validator_names:
                field.validators.append('isUniqueFileName')

            if 'isUniqueFileSize' not in validator_names:
                field.validators.append('isUniqueFileSize')

            schema[field.__name__] = field

        field = schema.get('title').copy()
        if type(field.validators) == tuple:
            # Why is the validators attr for title field a tuple?
            field.validators = ValidationChain(field.validators)

        validator_names = [v[0].name for v in field.validators]
        if 'isUniqueObjectName' not in validator_names:
            field.validators.append('isUniqueObjectName')
            field.widget.macro = 'dublettefinder_string'

        schema['title'] = field



