from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content.file import ATFile

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class FileExtender(DefaultExtender):
    adapts(ATFile)

    fields = DefaultExtender.fields + [
        fields.StringField(
            name='title',
            required=False,
            searchable=True,
            default='',
            accessor='Title',
            widget=widgets.StringWidget(
                label_msgid='label_title',
                visible={'view' : 'invisible'},
                i18n_domain='plone',
            ),
        ),
        fields.FileField('file',
            required=True,
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary marker here to have multilanguage files working
            primary=True,
            searchable=True,
            languageIndependent=False,
            storage = AnnotationStorage(migrate=True),
            widget = widgets.FileWidget(
                description = '',
                label=_(u'label_file', default=u'File'),
                show_content_type = False,
            )
        ),
    ]