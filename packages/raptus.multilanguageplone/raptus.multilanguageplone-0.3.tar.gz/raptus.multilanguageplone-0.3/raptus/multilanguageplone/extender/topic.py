from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.topic import ATTopic

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class TopicExtender(DefaultExtender):
    adapts(ATTopic)

    fields = DefaultExtender.fields + [
        fields.TextField('text',
                  required=False,
                  searchable=True,
                  storage = AnnotationStorage(migrate=True),
                  default_output_type = 'text/x-html-safe',
                  widget = widgets.RichWidget(
                            description = '',
                            label = _(u'label_body_text', default=u'Body Text'),
                            rows = 25,
                            allow_file_upload = zconf.ATDocument.allow_document_upload),
        ),
    ]