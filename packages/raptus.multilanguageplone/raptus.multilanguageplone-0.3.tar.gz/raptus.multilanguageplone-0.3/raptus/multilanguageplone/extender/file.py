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