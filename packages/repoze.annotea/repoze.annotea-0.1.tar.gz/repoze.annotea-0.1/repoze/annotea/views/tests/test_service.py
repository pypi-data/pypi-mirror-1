import unittest

class Test_search_annotations(unittest.TestCase):

    def _callFUT(self, context, request):
        from repoze.annotea.views.service import search_annotations
        return search_annotations(context, request)

    def _now(self):
        from datetime import datetime
        return datetime(2008, 11, 24, 14, 30, 00, 0)

    def _makeAnnotation(self, target=None):
        from rdflib import URIRef
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
            body_uri = URIRef('http://example.com/annotation/body.html')
            body_text = ''

        return DummyAnnotation()

    def test_no_QUERY_STRING_returns_BadRequest(self):
        context = DummyService()
        request = DummyRequest()

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail,
                         "No 'w3c_annotates' passed in query string.")

    def test_nonesuch_returns_empty_result(self):
        from rdflib.Graph import Graph
        from rdflib import URIRef
        from StringIO import StringIO
        from repoze.annotea.interfaces import ANNOTEA_ANNOTATES
        context = DummyService()
        request = DummyRequest(w3c_annotates='http://example.com/nonesuch')

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)
        graph = Graph()
        graph.parse(StringIO(response.body))
        found = list(
            graph.subjects(predicate=ANNOTEA_ANNOTATES,
                           object=URIRef('http://example.com/nonesuch')
                          ))
        self.assertEqual(len(found), 0)

    def test_empty_target_returns_all_annotations(self):
        from rdflib.Graph import Graph
        from rdflib import URIRef
        from StringIO import StringIO
        from repoze.annotea.interfaces import ANNOTEA_ANNOTATES
        context = DummyService()
        annotation1 = self._makeAnnotation('http://example.com/resource1')
        annotation1.__parent__ = context
        annotation1.__name__ = 'a1'
        annotation2 = self._makeAnnotation('http://example.com/resource2')
        annotation2.__parent__ = context
        annotation2.__name__ = 'a2'
        annotation3 = self._makeAnnotation('http://example.com/resource3')
        annotation3.__parent__ = context
        annotation3.__name__ = 'a3'
        context._search_results = (annotation1, annotation2, annotation3,)
        request = DummyRequest(w3c_annotates='')

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)
        graph = Graph()
        graph.parse(StringIO(response.body))
        found = list(graph.subject_objects(predicate=ANNOTEA_ANNOTATES))
        self.assertEqual(len(found), 3)
        self.failUnless((URIRef('http://example.com/annotation/a1/'),
                         URIRef('http://example.com/resource1')) in found)
        self.failUnless((URIRef('http://example.com/annotation/a2/'),
                         URIRef('http://example.com/resource2')) in found)
        self.failUnless((URIRef('http://example.com/annotation/a3/'),
                         URIRef('http://example.com/resource3')) in found)

    def test_found_returns_nonempty_result(self):
        from rdflib.Graph import Graph
        from rdflib import URIRef
        from StringIO import StringIO
        from repoze.annotea.interfaces import ANNOTEA_ANNOTATES
        context = DummyService()
        annotation = self._makeAnnotation()
        annotation.__parent__ = context
        annotation.__name__ = 'dummy'
        context._search_results = (annotation,)
        request = DummyRequest(w3c_annotates='http://example.com/resource')

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 200)
        graph = Graph()
        graph.parse(StringIO(response.body))
        found = list(
            graph.subjects(predicate=ANNOTEA_ANNOTATES,
                           object=URIRef('http://example.com/resource')
                          ))
        self.assertEqual(len(found), 1)
        self.failUnless(
                URIRef('http://example.com/annotation/dummy/') in found)

class Test_create_annotation(unittest.TestCase):

    _old_now = None

    def tearDown(self):
        if self._old_now is not None:
            self._setNowFunc(self._old_now)

    def _callFUT(self, context, request):
        from repoze.annotea.views.service import create_annotation
        return create_annotation(context, request)

    def _setNowFunc(self, callable):
        from repoze.annotea.views import utils
        if self._old_now is None:
            self._old_now = utils._now
        utils._now = callable

    def test_not_XML_returns_BadRequest(self):
        context = DummyService()
        request = DummyRequest()
        request.headers['Content-Type'] = 'text/plain'

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail,
                         "Content-type must be 'application/xml'.")

    def test_malformed_xml_returns_BadRequest(self):
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        request.body_file = StringIO(MALFORMED_XML)

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail, "Not well-formed XML.")

    def test_invalid_type_returns_BadRequest(self):
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(INVALID_TYPE)

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail,
                         "No Annotatea resource type provided.")

    def test_missing_annotates_returns_BadRequest(self):
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(MISSING_ANNOTATES)

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail,
                         "No 'annotates' target provided.")

    def test_missing_body_returns_BadRequest(self):
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(MISSING_BODY)

        response = self._callFUT(context, request)

        self.assertEqual(response.code, 400)
        self.assertEqual(response.detail,
                         "No body URI / content provided.")

    def test_minimal_ok(self):
        import datetime
        from rdflib.Graph import Graph
        from rdflib import URIRef
        from StringIO import StringIO
        NOW = lambda: datetime.datetime(2008, 11, 23, 16, 45, 0)
        self._setNowFunc(NOW)
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(MINIMAL_OK)

        response = self._callFUT(context, request)

        annotation = context._items['abcd']
        self.assertEqual(annotation.__name__, 'abcd')
        self.failUnless(annotation.__parent__ is context)
        self.assertEqual(annotation.title, u'')
        self.assertEqual(annotation.context, None)
        self.assertEqual(annotation.creator, u'')
        self.assertEqual(annotation.created, NOW())
        self.assertEqual(annotation.modified, NOW())

        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.location,
                         'http://example.com/annotation/abcd/')

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
                         URIRef('http://serv2.example.com/mycomment.html'))

    def test_metadata_plus_external_body_uri(self):
        from datetime import datetime
        from rdflib import URIRef
        from rdflib.Graph import Graph
        from rdflib.util import parse_date_time
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(METADATA_PLUS_EXTERNAL_BODY_URI)

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.location,
                         'http://example.com/annotation/abcd/')

        annotation = context._items['abcd']
        self.assertEqual(annotation.__name__, 'abcd')
        self.failUnless(annotation.__parent__ is context)
        self.assertEqual(annotation.title, 'Annotation of Sample Page')
        self.assertEqual(annotation.context,
                         'http://serv1.example.com/some/page.html'
                         '#xpointer(id("Main")/p[2])')
        self.assertEqual(annotation.creator, 'Ralph Swick')
        FIXED_DATE = datetime.utcfromtimestamp(
                        parse_date_time('1999-10-14T12:10:00Z'))
        self.assertEqual(annotation.created, FIXED_DATE)
        self.assertEqual(annotation.modified, FIXED_DATE)
        self.assertEqual(annotation.body_uri,
                         URIRef('http://serv2.example.com/mycomment.html'))
        self.assertEqual(annotation.body_text, u'')

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
                         URIRef('http://serv2.example.com/mycomment.html'))

    def test_metadata_plus_included_body_xhtml(self):
        from rdflib.Graph import Graph
        from rdflib import URIRef
        from StringIO import StringIO
        context = DummyService()
        request = DummyRequest()
        request.body_file = StringIO(METADATA_PLUS_INCLUDED_BODY_XHTML)

        response = self._callFUT(context, request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.location,
                         'http://example.com/annotation/abcd/')

        annotation = context._items['abcd']
        self.assertEqual(annotation.body_uri, None)
        self.assertEqual(annotation.body_text,
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

MALFORMED_XML = """\
<malformed>"""

RDF_PROLOG = """\
<?xml version="1.0" ?>
<r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:a="http://www.w3.org/2000/10/annotation-ns#"
       xmlns:d="http://purl.org/dc/elements/1.1/">
 <r:Description>
"""

RDF_EPILOG = """\
 </r:Description>
</r:RDF>"""

INVALID_TYPE = RDF_PROLOG + """\
  <r:type r:resource="http://example.com/some/other/resource/type"/>
  <a:annotates r:resource="http://serv1.example.com/some/page.html"/>
  <a:body r:resource="http://serv2.example.com/mycomment.html"/>
""" + RDF_EPILOG

MISSING_ANNOTATES = RDF_PROLOG + """\
  <r:type r:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
  <a:body r:resource="http://serv2.example.com/mycomment.html"/>
""" + RDF_EPILOG

MISSING_BODY = RDF_PROLOG + """\
  <r:type r:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
  <r:type r:resource="http://example.com/some/other/resource/type"/>
  <a:annotates r:resource="http://serv1.example.com/some/page.html"/>
""" + RDF_EPILOG

MINIMAL_OK = RDF_PROLOG + """\
  <r:type r:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
  <r:type r:resource="http://example.com/some/other/resource/type"/>
  <a:annotates r:resource="http://serv1.example.com/some/page.html"/>
  <a:body r:resource="http://serv2.example.com/mycomment.html"/>
""" + RDF_EPILOG

METADATA_PLUS_EXTERNAL_BODY_URI = RDF_PROLOG + """\
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
  <a:body r:resource="http://serv2.example.com/mycomment.html"/>
""" + RDF_EPILOG

METADATA_PLUS_INCLUDED_BODY_XHTML = """\
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

class DummyService:
    __parent__ = __name__ = None
    _search_criteria = None
    _search_results = ()

    def __init__(self):
        self._items = {}

    def add(self, annotation):
        self._items['abcd'] = annotation
        annotation.__name__ = 'abcd'
        annotation.__parent__ = self
        return 'abcd'

    def search(self, types=None, annotates=None):
        self._search_criteria = types, annotates
        return self._search_results

class DummyRequest:

    application_url = 'http://example.com/annotation/'

    def __init__(self, **kw):
        self.headers = {'Content-Type': 'application/xml'}
        self.GET = kw.copy()

