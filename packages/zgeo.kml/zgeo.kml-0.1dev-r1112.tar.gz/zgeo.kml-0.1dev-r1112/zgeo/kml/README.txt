zgeo.atom Package Readme
=========================

Objects that provide IGeoItem can be represented as Atom entries using this
package's link entry view.

    >>> from zgeo.geographer.interfaces import IGeoreferenced
    
Let's create a placemark mock:
    
    >>> from zope.interface import implements, Interface
    >>> from zope.component import provideAdapter
    >>> from zope.dublincore.interfaces import ICMFDublinCore
    >>> from zope.traversing.browser.interfaces import IAbsoluteURL
    >>> from zope.publisher.interfaces.browser import IBrowserRequest

    >>> class Mock(object):
    ...     implements((IGeoreferenced, ICMFDublinCore))
    ...     def __init__(self, id, summary, long, lat):
    ...         self.id = id
    ...         self.summary = summary
    ...         self.type = 'Point'
    ...         self.coordinates = (long, lat)
    ...     def absolute_url(self):
    ...         return 'http://example.com/%s' % self.id
    ...     def Title(self):
    ...         return self.id.capitalize()
    ...     def Description(self):
    ...         return self.summary
    ...     def CreationDate(self):
    ...         return '2007-12-07 12:00:00'
    ...     def ModificationDate(self):
    ...         return '2007-12-07 12:01:00'

We also need a view to provide IAbsoluteURL

    >>> class AbsoluteURL(object):
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...     def __call__(self):
    ...         return self.context.absolute_url()

    >>> provideAdapter(AbsoluteURL, adapts=(Interface, IBrowserRequest), provides=IAbsoluteURL)

Create a placemark instance

    >>> placemark = Mock('a', "Place marked 'A'", -105.08, 40.59)

Confirm that it directly provides IGeoreferenced

    >>> IGeoreferenced(placemark) == placemark
    True
    >>> IGeoreferenced(placemark).coordinates
    (-105.08, 40.590000000000003)

Test the KML Placemark view of the placemark

    >>> from zgeo.kml.browser import Placemark
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = Placemark(placemark, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.kml.browser.Placemark object at ...>
    
    >>> view.id
    'http://example.com/a/@@kml-placemark'
    >>> view.name
    'A'
    >>> view.description
    "Place marked 'A'"
    >>> view.alternate_link
    'http://example.com/a'

    >>> view.hasPolygon
    0
    >>> view.hasLineString
    0
    >>> view.hasPoint
    1
    >>> view.coords_kml
    '-105.080000,40.590000,0.0'

Test the feed view

    >>> class Collection(dict):
    ...     implements(ICMFDublinCore)
    ...     def absolute_url(self):
    ...         return 'http://example.com/collection'
    ...     def Title(self):
    ...         return 'Test Collection'
    ...     def Description(self):
    ...         return 'A collection for testing'
    ...     def ModificationDate(self):
    ...         return '2007-12-07 12:01:00'
    ...     def __call__(self):
    ...         return 'http://example.com/collection'

    >>> collection = Collection()
    >>> collection['a'] = placemark
    >>> from zgeo.kml.browser import Document
    >>> view = Document(collection, request)
    >>> view # doctest: +ELLIPSIS
    <zgeo.kml.browser.Document object at ...>
    >>> view.name
    'Test Collection'
    >>> view.alternate_link
    'http://example.com/collection'
    >>> view.features # doctest: +ELLIPSIS
    <generator object at ...>
    >>> [e for e in view.features][0] # doctest: +ELLIPSIS
    <zgeo.kml.browser.Placemark object at ...>

