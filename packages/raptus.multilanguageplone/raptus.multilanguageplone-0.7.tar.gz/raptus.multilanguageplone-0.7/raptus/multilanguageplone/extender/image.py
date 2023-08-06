from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.base import ATCTFileContent

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
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary marker here to have multilanguage images working
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

# monkeypatch to support access to multilanguage image scales
def __bobo_traverse__(self, REQUEST, name):
    """Transparent access to multilanguage image scales
    """
    if name.startswith('image'):
        field = self.getField('image')
        image = None
        if name == 'image':
            image = field.getScale(self)
        elif '___' in name:
            name, lang, scalename = name.split('___')
            if scalename:
                scalename = scalename[1:]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename, lang=lang)
            else:
                image = field.getScale(self, lang=lang)
        else:
            scalename = name[len('image_'):]
            if scalename in field.getAvailableSizes(self):
                image = field.getScale(self, scale=scalename)
        if image is not None and not isinstance(image, basestring):
            # image might be None or '' for empty images
            return image

    return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)
ATImage.__bobo_traverse__ = __bobo_traverse__