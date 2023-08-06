from Products.Archetypes.Field import ImageField
from Products.Archetypes.Widget import ImageWidget
from Products.Archetypes.Widget import FileWidget
from Products.Archetypes.Widget import RichWidget

from cgi import escape

import logging
logger = logging.getLogger('archetypes.fieldtraverser')

def tag_fieldtraverser(self, instance, scale=None, height=None, width=None, alt=None,
        css_class=None, title=None, **kwargs):
    """Create a tag including scale
    """
    image = self.getScale(instance, scale=scale)
    if image:
        img_width, img_height = self.getSize(instance, scale=scale)
    else:
        img_height=0
        img_width=0

    if height is None:
        height=img_height
    if width is None:
        width=img_width

    url = instance.absolute_url()

    # use the new field traverser instead to construct url to images
    if scale:
        url+= '/' + '++atfield++' + self.getName() + '-' + scale
    else:
        url+= '/' + '++atfield++' + self.getName()

    values = {'src' : url,
              'alt' : escape(alt and alt or instance.Title(), 1),
              'title' : escape(title and title or instance.Title(), 1),
              'height' : height,
              'width' : width,
             }

    result = '<img src="%(src)s" alt="%(alt)s" title="%(title)s" '\
             'height="%(height)s" width="%(width)s"' % values

    if css_class is not None:
        result = '%s class="%s"' % (result, css_class)

    for key, value in kwargs.items():
        if value:
            result = '%s %s="%s"' % (result, key, value)

    return '%s />' % result

logger.info('REBINDING Products.Archetypes.Field.ImageField.tag')
ImageField.tag = tag_fieldtraverser

logger.info('UPDATING Products.Archetypes.Widget.ImageWidget._properties')
ImageWidget._properties.update({
        'macro' : "widget-image-fieldtraverser",
        })

logger.info('UPDATING Products.Archetypes.Widget.FileWidget._properties')
FileWidget._properties.update({
        'macro' : "widget-file-fieldtraverser",
        })

logger.info('UPDATING Products.Archetypes.Widget.RichWidget._properties')
RichWidget._properties.update({
        'macro' : "widget-rich-fieldtraverser",
        })

""" Reload ATContentTypes which rely on image and file widgets.
    This step should not be necessary when ATContentTypes are loaded
    AFTER archetypes.fieldtraverser.
    BUT their namespace is Products.ATContentTypes,
    their path is in pythons os.path and
    the Zope2 loading mechanism recognizes them as normal products
    (although they are eggs in Plone3.2) and so they are loaded BEFORE
    archetypes.fieldtraverser despite the definiton of zcml loading order
    in buildout / etc/package-includes.
    So, thats why we have to load ATContentTypes here again.

    Any other ContentTypes which are defined in traditional Products OR in eggs
    with "Product" namespace should also be reloaded after the
    archetypes.fieldtraverser patch is applied.
"""
from Products.ATContentTypes.content import file as atfile
from Products.ATContentTypes.content import image as atimage
from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import topic
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes import ATCTMessageFactory as _

atfile.ATFileSchema['file'].widget.macro = "widget-file-fieldtraverser"
atimage.ATImageSchema['image'].widget.macro = "widget-image-fieldtraverser"
newsitem.ATNewsItemSchema['image'].widget.macro = "widget-image-fieldtraverser"
newsitem.ATNewsItemSchema['text'].widget.macro = "widget-rich-fieldtraverser"
document.ATDocumentSchema['text'].widget.macro = "widget-rich-fieldtraverser"
event.ATEventSchema['text'].widget.macro = "widget-rich-fieldtraverser"
topic.ATTopicSchema['text'].widget.macro = "widget-rich-fieldtraverser"


"""
reload(atfile) # FileWidget
reload(atimage) # ImageWidget
reload(newsitem) # ImageWidget, RichWidget
reload(document) # RichWidget
reload(event) # RichWidget
reload(topic) # RichWidget
"""