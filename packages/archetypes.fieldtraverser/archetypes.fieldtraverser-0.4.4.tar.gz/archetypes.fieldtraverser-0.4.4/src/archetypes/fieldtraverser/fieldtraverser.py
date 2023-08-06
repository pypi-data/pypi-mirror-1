from AccessControl import Unauthorized
from Acquisition import Implicit
from OFS.SimpleItem import Item
from zope.interface import implements
from zope.interface import providedBy
from zope.interface import Interface
from zope.interface import Attribute
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserPublisher
from Products.Five.browser import BrowserView
from Products.Archetypes.interfaces import IBaseUnit
from OFS.Image import File

class IFieldContent(Interface):
    content = Attribute(u"returns the content of the at-fields storage")


class FieldContent(Implicit, Item):

    implements(IFieldContent, IBrowserPublisher)

    def __init__(self, context, request, field, storage):
        self.context = context
        self.request = request
        self.field = field
        self.storage = storage

    def browserDefault(self, request):
        return self, ('@@view',)

    @property
    def content(self):

        if not self.field.checkPermission('r', self.context):
            raise Unauthorized, \
                  'Your not allowed to access the requested field %s.' % \
                  self.field.getName()

        try:
            value = self.field.getStorage(self.context).get(self.storage,
                                                            self.context)
        except AttributeError:
            return None

        if IBaseUnit.providedBy(value) or isinstance(value, File):
            # for IBaseUnit wrapped fields, i.e. metadata-fields, file- and
            # image objects
            return value.index_html(self.request, self.request.response)

         # TODO: check if theres some other special cases

         # TODO: adapter which transforms fields to values. e.g. Lines Field ->
         # 1 entry per Line; DataGrid Field -> CSV table

        return str(value)


class FieldContentView(BrowserView):
    def __call__(self):
        return self.context.content


class FieldTraverser(object):
    """Used to traverse to an Archetypes field and access its storage.

    Use Cases:
         - Access to images or other binary data via AnnotationStorage instead
           of traditional AttributeStorage. archetypes.fieldtraverser eliminates
           the need to hack the __bobo__ traverser for this.
           Advantage: When accessing objects with binary data stored in an
           AttributeStorage, much binary data chunks are loaded regardless if
           they are used. When doing this quite often the ZODB is unnecessarily
           stressed.

         - You can use archetypes.fieldtraverser for simple Web Services which
           return just the content of Archetypes fields without the HTML
           rendered by widgets

         - You may also use archetypes.fieldtraverser to impress your friends.

    Usage: In an URL this traverser can be used to access a fields data by use of
           the fieldname and the storage variant if needed (such as image sizes)

           Usage:       obj/++atfield++FIELDNAME
           or:          obj/++atfield++FIELDNAME-STORAGENAME

    Example: To access an original site image from a field named 'photo':
               obj/++atfield++photo

             To access its thumbnail with size name thumb:
               obj/++atfield++photo-thumb
    """
    implements(ITraversable)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):

        if '-' in name:
            fieldname, storage = name.split('-')
            storage = '%s_%s' % (fieldname, storage)
        else:
            fieldname, storage = name, name
        field = self.context.Schema().get(fieldname, None)
        if field is None:
            return None
        return FieldContent(self.context, self.request, field, storage).__of__(self.context)
