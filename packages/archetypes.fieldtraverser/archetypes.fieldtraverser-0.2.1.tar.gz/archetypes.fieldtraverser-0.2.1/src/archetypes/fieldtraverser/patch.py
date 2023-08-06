from Products.Archetypes.Field import ImageField
from Products.Archetypes.Widget import ImageWidget

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

logger.info('REBINDING Products.Archetypes.Widget.ImageWidget._properties.update')
ImageWidget._properties.update({
        'macro' : "widget-image-fieldtraverser",
        })
