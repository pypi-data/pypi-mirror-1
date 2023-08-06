
import time

from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.dublincore.interfaces import ICMFDublinCore

try:
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    raise Exception, "Five's ViewPageTemplateFile doesn't work with named templating"
except:
    from zope.app.pagetemplate import ViewPageTemplateFile

from zope.interface import implements
from zope.publisher.browser import BrowserPage
from zope.formlib.namedtemplate import NamedTemplate
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.component import getMultiAdapter

from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.kml.interfaces import IFeature, IPlacemark, IContainer


def coords_to_kml(geom):
    gtype = geom.type
    if gtype == 'Point':
        coords = (geom.coordinates,)
    elif gtype == 'Polygon':
        coords = geom.coordinates[0]
    else:
        coords = geom.coordinates
    if len(coords[0]) == 2:
        tuples = ('%f,%f,0.0' % tuple(c) for c in coords)
    elif len(coords[0]) == 3:
        tuples = ('%f,%f,%f' % tuple(c) for c in coords)
    else:
        raise ValueError, "Invalid dimensions"
    return ' '.join(tuples)

def rfc3339(date):
    # Convert ISO or RFC 3339 datetime strings to RFC 3339
    # Zope's ZDCAnnotatableAdapter gives RFC 3339. Lose the seconds precision
    if str(date).find('T') == 10:
        s = date.split('.')[0]
    # Plone's AT content types give ISO
    else:
        t = time.strptime(date, '%Y-%m-%d %H:%M:%S')
        s =  time.strftime('%Y-%m-%dT%H:%M:%S', t)
    tz = '%03d:00' % -int(time.timezone/3600)
    return s + tz

def absoluteURL(ob, request):
    return getMultiAdapter((ob, request), IAbsoluteURL)()


class NullGeometry(object):
    type = None
    coordinates = None


class Feature(BrowserPage):

    """Not to be instantiated.
    """
    implements(IFeature)

    @property
    def id(self):
        return '%s/@@%s' % (absoluteURL(self.context, self.request), self.__name__)

    @property
    def name(self):
        return self.dc.Title()

    @property
    def description(self):
        return self.dc.Description()

    @property
    def author(self):
        return {
            'name': self.dc.Creator(),
            'uri': '',
            'email': ''
            }

    @property
    def alternate_link(self):
        return absoluteURL(self.context, self.request)

    
class Placemark(Feature):

    implements(IPlacemark)
    __name__ = 'kml-placemark'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)
        try:
            self.geom = IGeoreferenced(self.context)
        except:
            self.geom = NullGeometry()

    @property
    def hasPoint(self):
        return int(self.geom.type == 'Point')

    @property
    def hasLineString(self):
        return int(self.geom.type == 'LineString')

    @property
    def hasPolygon(self):
        return int(self.geom.type == 'Polygon')

    @property
    def coords_kml(self):
        return coords_to_kml(self.geom)

    def __call__(self):
        return self.template().encode('utf-8')


class Folder(Feature):
    
    implements(IContainer)
    __name__ = 'kml-folder'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)

    @property
    def features(self):
        for item in self.context.values():
            yield Placemark(item, self.request)

    

class Document(Feature):

    implements(IContainer)
    __name__ = 'kml-document'
    template = NamedTemplate('template-kml-document')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dc = ICMFDublinCore(self.context)

    @property
    def features(self):
        for item in self.context.values():
            yield getMultiAdapter((item, self.request), IFeature)

    def __call__(self):
        return self.template().encode('utf-8')


document_template = NamedTemplateImplementation(
    ViewPageTemplateFile('kml_document.pt')
    )
