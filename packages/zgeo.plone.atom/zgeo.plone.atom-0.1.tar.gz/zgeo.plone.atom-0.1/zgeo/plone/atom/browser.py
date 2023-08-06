from zope.dublincore.interfaces import ICMFDublinCore
from zope.interface import implements
import zope.security.proxy
from Products.CMFCore.utils import getToolByName
from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.atom.interfaces import IWriteAtomMetadata
from zgeo.atom.browser import rfc3339, NullGeometry, LinkEntry, SubscriptionFeed


class Geometry(object):
    
    implements(IGeoreferenced)

    def __init__(self, type, coordinates):
        self.type = type
        self.coordinates = coordinates


class BrainLinkEntry(LinkEntry):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        try:
            g = self.context.zgeo_geometry
            self.geom = Geometry(g['type'], g['coordinates'])
        except:
            self.geom = NullGeometry()

    @property
    def id(self):
        return 'urn:uuid:%s' % self.context.UID

    @property
    def title(self):
        return self.context.Title

    @property
    def updated(self):
        return rfc3339(self.context.ModificationDate)


    @property
    def author(self):
        return {
            'name': self.context.Creator,
            'uri': '',
            'email': ''
            }

    @property
    def published(self):
        return rfc3339(self.context.CreationDate)

    @property
    def summary(self):
        return self.context.Description


    #@property
    #def links(self):
    #    items = {
    #        'alternate': Link(
    #            absoluteURL(self.context, self.request),
    #            rel='alternate',
    #            type='text/html')
    #        }
    #    if IAtomPublishable.providedBy(self.context):
    #        items['edit'] = Link(
    #            "%s/atom-entry" % absoluteURL(self.context, self.request),
    #            rel='edit',
    #            type='application/atom+xml;type=entry')
    #    return items


class TopicSubscriptionFeed(SubscriptionFeed):

    @property
    def updated(self):
        return rfc3339(self.context.CreationDate())

    @property
    def entries(self):
        for brain in self.context.queryCatalog():
            yield BrainLinkEntry(brain, self.request)
