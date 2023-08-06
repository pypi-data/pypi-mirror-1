from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.image import ATImage

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class ImageExtender(DefaultExtender):
    adapts(ATImage)

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
        fields.ImageField('image',
            required=True,
            primary=True,
            languageIndependent=False,
            storage = AnnotationStorage(migrate=True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            max_size = zconf.ATImage.max_image_dimension,
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                    },
            widget = widgets.ImageWidget(
                description = '',
                label= _(u'label_image', default=u'Image'),
                show_content_type = False,
            )
        ),
    ]