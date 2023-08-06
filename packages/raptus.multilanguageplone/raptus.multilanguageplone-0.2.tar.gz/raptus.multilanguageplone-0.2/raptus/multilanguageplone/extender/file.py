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
        fields.FileField('file',
            required=True,
            searchable=True,
            languageIndependent=True,
            storage = AnnotationStorage(migrate=True),
            widget = widgets.FileWidget(
                description = '',
                label=_(u'label_file', default=u'File'),
                show_content_type = False,
            )
        ),
    ]