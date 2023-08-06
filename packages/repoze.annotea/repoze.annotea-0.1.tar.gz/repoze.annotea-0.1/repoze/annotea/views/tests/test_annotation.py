import unittest

class _Base:

    def _now(self):
        from datetime import datetime
        return datetime(2008, 11, 24, 14, 30, 00, 0)

    def _makeAnnotation(self, target=None):
        from rdflib import URIRef
        from rdflib import Literal
        from repoze.annotea.interfaces import ANNOTEA_TYPE
        if target is None:
            target = URIRef('http://example.com/resource')

        class DummyAnnotation:

            types = (ANNOTEA_TYPE,)
            annotates = target
            context = None
            title = u'Dummy Annotation'
            creator = 'Phred'
            created = self._now()
            modified = self._now()
            body_uri = URIRef('http://example.com/folder/page.html')
            body_text = ''

        annotation = DummyAnnotation()
        annotation.__parent__ = DummyService()
        annotation.__name__ = 'dummy'

        return annotation

class Test_get_annotation(unittest.TestCase, _Base):

    def _callFUT(self, context, request):
        from repoze.annotea.views.annotation import get_annotation
        return get_annotation(context, request)

    def test_defaults(self):
        from StringIO import StringIO
        from rdflib import URIRef
        from rdflib.Graph import Graph
        from repoze.annotea.interfaces import ANNOTEA_ANNOTATES
        from repoze.annotea.interfaces import ANNOTEA_BODY
        from repoze.annotea.interfaces import ANNOTEA_CONTEXT
        from repoze.annotea.interfaces import ANNOTEA_CREATED
        from repoze.annotea.interfaces import DC_TITLE
        from repoze.annotea.interfaces import DC_CREATOR
        from repoze.annotea.interfaces import DC_DATE
        from repoze.annotea.views.utils import TIME_FMT_HH_MM_ZONE
        context = self._makeAnnotation()
        request = DummyRequest()

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)
        graph = Graph()
        graph.parse(StringIO(response.body))

        subject, = list(set(graph.subjects())) # "there can be only one..."
        self.assertEqual(subject,
                         URIRef('http://example.com/annotation/dummy/'))
        self.assertEqual(graph.value(subject=subject,
                                     predicate=ANNOTEA_ANNOTATES),
                         URIRef('http://example.com/resource'))
        self.assertEqual(graph.value(subject=subject,
                                     predicate=ANNOTEA_BODY),
                         URIRef('http://example.com/folder/page.html'))
        self.assertEqual(graph.value(subject=subject,
                                     predicate=ANNOTEA_CONTEXT), None)
        self.assertEqual(graph.value(subject=subject,
                                     predicate=ANNOTEA_CREATED),
                         self._now().strftime(TIME_FMT_HH_MM_ZONE))
        self.assertEqual(graph.value(subject=subject,
                                     predicate=DC_TITLE), 'Dummy Annotation')
        self.assertEqual(graph.value(subject=subject,
                                     predicate=DC_CREATOR), 'Phred')
        self.assertEqual(graph.value(subject=subject,
                                     predicate=DC_DATE),
                         self._now().strftime(TIME_FMT_HH_MM_ZONE))

class Test_get_body(unittest.TestCase, _Base):

    def _callFUT(self, context, request):
        from repoze.annotea.views.annotation import get_body
        return get_body(context, request)

    def test_body_uri_not_None_redirects(self):
        context = self._makeAnnotation()
        request = DummyRequest()
        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 301)
        self.assertEqual(response.location,
                         'http://example.com/folder/page.html')

    def test_body_uri_None_returns_body(self):
        FOUND_IT = '<html><body><h1>FOUND IT</h1></body></html>'
        context = self._makeAnnotation()
        context.body_uri = None
        context.body_text = FOUND_IT
        request = DummyRequest()

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, FOUND_IT)

class Test_replace_annotation(unittest.TestCase, _Base):

    def _callFUT(self, context, request):
        from repoze.annotea.views.annotation import replace_annotation
        return replace_annotation(context, request)

    def test_replace_updates_everything(self):
        from StringIO import StringIO
        from rdflib import URIRef
        from rdflib.Graph import Graph
        service = DummyService()
        service._items['abcd'] = context = self._makeAnnotation()
        context.__parent__ = service
        context.__name__ = 'abcd'
        request = DummyRequest()
        request.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        request.body_file = StringIO(REPLACEMENT_XML)

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)

        updated = service._items['abcd']
        self.assertEqual(updated.body_uri, None)
        self.assertEqual(updated.body_text,
                        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                        '<head>\n'
                        '<title>Ralph\'s Annotation</title>\n'
                        '</head>\n'
                        '<body>\n'
                        '<p>This is an <em>important</em> concept; see\n'
                        '<a href="http://serv1.example.com/other/page.html">'
                               'other page</a>.</p>\n'
                        '</body>\n'
                        '</html>')

        graph = Graph()
        graph.parse(StringIO(response.body))

        annotates = graph.value(
            subject=URIRef('http://example.com/annotation/abcd/'),
            predicate=URIRef('http://www.w3.org/2000/10/'
                             'annotation-ns#annotates'))
        self.assertEqual(annotates,
                         URIRef('http://serv1.example.com/some/page.html'))

        body = graph.value(
            subject=URIRef('http://example.com/annotation/abcd/'),
            predicate=URIRef('http://www.w3.org/2000/10/annotation-ns#body'))
        self.assertEqual(body,
                         URIRef('http://example.com/annotation/abcd/'
                                'body.html'))


class Test_remove_annotation(unittest.TestCase, _Base):

    def _callFUT(self, context, request):
        from repoze.annotea.views.annotation import remove_annotation
        return remove_annotation(context, request)

    def test_remove(self):
        service = DummyService()
        service._items['abcd'] = context = self._makeAnnotation()
        context.__parent__ = service
        context.__name__ = 'abcd'
        request = DummyRequest()

        self._callFUT(context, request)

        self.assertEqual(len(service._items), 0)

class DummyService:
    __parent__ = __name__ = None

    def __init__(self):
        self._items = {}

    def replace(self, key, value):
        self._items[key] = value
        value.__name__ = key
        value.__parent__ = self

    def remove(self, annotation_or_uuid):
        if annotation_or_uuid not in self._items:
            raise KeyError(annotation_or_uuid)
        del self._items[annotation_or_uuid]

class DummyRequest:

    application_url = 'http://example.com/annotation/'

    def __init__(self):
        self.headers = {}

REPLACEMENT_XML = """\
<?xml version="1.0" ?>
<r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:a="http://www.w3.org/2000/10/annotation-ns#"
       xmlns:d="http://purl.org/dc/elements/1.1/"
       xmlns:h="http://www.w3.org/1999/xx/http#">
 <r:Description>
  <r:type r:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
  <r:type r:resource="http://www.w3.org/2000/10/annotationType#Comment"/>
  <a:annotates r:resource="http://serv1.example.com/some/page.html"/>
  <a:context>
     http://serv1.example.com/some/page.html#xpointer(id("Main")/p[2])
  </a:context>
  <d:title>Annotation of Sample Page</d:title>
  <d:creator>Ralph Swick</d:creator>
  <a:created>1999-10-14T12:10:00Z</a:created>
  <d:date>1999-10-14T12:10:00Z</d:date>
  <a:body>
   <r:Description>
    <h:ContentType>text/html</h:ContentType>
    <h:ContentLength>289</h:ContentLength>
    <h:Body r:parseType="Literal">
     <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
       <title>Ralph's Annotation</title>
      </head>
      <body>
       <p>This is an <em>important</em> concept; see
       <a href="http://serv1.example.com/other/page.html">other page</a>.</p>
      </body>
     </html>
    </h:Body>
   </r:Description>
  </a:body>
 </r:Description>
</r:RDF>
"""
