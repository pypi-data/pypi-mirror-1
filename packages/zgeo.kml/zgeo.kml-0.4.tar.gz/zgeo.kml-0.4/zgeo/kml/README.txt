zgeo.atom Package Readme
=========================

Objects that provide IGeoItem can be represented as Atom entries using this
package's link entry view.

Test the KML Placemark view of the placemark

    >>> from zgeo.kml.browser import Placemark
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = Placemark(placemark, request)
    >>> view
    <zgeo.kml.browser.Placemark object at ...>
    
    >>> view.id
    'http://127.0.0.1/places/a/@@kml-placemark'
    >>> view.name
    'A'
    >>> view.description
    "Place marked 'A'"
    >>> view.alternate_link
    'http://127.0.0.1/places/a'

    >>> view.hasPolygon
    0
    >>> view.hasLineString
    0
    >>> view.hasPoint
    1
    >>> view.coords_kml
    '-105.080000,40.590000,0.0'

Test the feed view

    >>> from zgeo.kml.browser import Document
    >>> view = Document(places, request)
    >>> view
    <zgeo.kml.browser.Document object at ...>
    >>> view.name
    'Places'
    >>> view.alternate_link
    'http://127.0.0.1/places'
    >>> view.features
    <generator object at ...>
    >>> [e for e in view.features][0]
    <zgeo.kml.browser.Placemark object at ...>

