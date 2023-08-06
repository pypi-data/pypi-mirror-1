from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.newsitem import ATNewsItem

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class NewsItemExtender(DefaultExtender):
    adapts(ATNewsItem)

    fields = DefaultExtender.fields + [
        fields.TextField('text',
            required = False,
            searchable = True,
            primary = True,
            storage = AnnotationStorage(migrate=True),
            default_output_type = 'text/x-html-safe',
            widget = widgets.RichWidget(
                description = '',
                label = _(u'label_body_text', u'Body Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload
            ),
            schemata='default',
        ),
        fields.ImageField('image',
            required = False,
            storage = AnnotationStorage(migrate=True),
            languageIndependent = True,
            max_size = zconf.ATNewsItem.max_image_dimension,
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                   },
            widget = widgets.ImageWidget(
                description = _(u'help_news_image', default=u'Will be shown in the news listing, and in the news item itself. Image will be scaled to a sensible size.'),
                label= _(u'label_news_image', default=u'Image'),
                show_content_type = False
            )
        ),
        fields.StringField('imageCaption',
            required = False,
            searchable = True,
            widget = widgets.StringWidget(
                description = '',
                label = _(u'label_image_caption', default=u'Image Caption'),
                size = 40
            )
        ),
    ]