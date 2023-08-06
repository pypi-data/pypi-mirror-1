from zope.dublincore.interfaces import ICMFDublinCore
from zope.interface import implements
from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.kml.interfaces import IFeature, IPlacemark, IContainer
from zgeo.kml.browser import NullGeometry
from zgeo.kml.browser import Document, Placemark
from Products.CMFCore.utils import getToolByName


class Geometry(object):
    
    implements(IGeoreferenced)

    def __init__(self, type, coordinates):
        self.type = type
        self.coordinates = coordinates


class BrainPlacemark(Placemark):

    implements(IPlacemark)
    __name__ = 'kml-placemark'

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
        pt = getToolByName(self.context, 'portal_url')
        root_path = pt.getPhysicalPath()[1]
        return '%s%s/@@%s' % (pt().rstrip(root_path), self.context.getPath().lstrip('/'), self.__name__)

    @property
    def name(self):
        return self.context.Title

    @property
    def description(self):
        return self.context.Description

    @property
    def author(self):
        return {
            'name': self.context.Creator,
            'uri': '',
            'email': ''
            }

    @property
    def alternate_link(self):
        pt = getToolByName(self.context, 'portal_url')
        root_path = pt.getPhysicalPath()[1]
        return '%s%s' % (pt().rstrip(root_path), self.context.getPath().lstrip('/'))


class TopicDocument(Document):

    @property
    def features(self):
        for brain in self.context.queryCatalog():
            yield BrainPlacemark(brain, self.request)
