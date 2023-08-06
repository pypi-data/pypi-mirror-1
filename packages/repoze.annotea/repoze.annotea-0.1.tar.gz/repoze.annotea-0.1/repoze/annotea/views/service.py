# repoze.annotea view functions

import datetime
from rdflib.Graph import Graph
from rdflib import URIRef
from webob import Response
from webob.exc import HTTPBadRequest

from repoze.bfg.traversal import model_url

from repoze.annotea.interfaces import ANNOTEA_TYPE
from repoze.annotea.views.utils import _annotationFromRequest
from repoze.annotea.views.utils import _convertDatetimeString
from repoze.annotea.views.utils import _getAnnotationTriples

def search_annotations(context, request):
    target = request.GET.get('w3c_annotates')
    if target is None:
        return HTTPBadRequest("No 'w3c_annotates' passed in query string.")
    graph = Graph()
    kw = {}
    if target != '':
        kw['annotates'] = URIRef(target)
    else:
        kw['types'] = ANNOTEA_TYPE
    for annotation in context.search(**kw):
        for triple in _getAnnotationTriples(annotation, request):
            graph.set(triple)

    headers = [('Content-type', 'application/xml')]
    return Response(body=graph.serialize(),
                    headerlist=headers,
                   )

def dispatch_POST(context, request):
    if 'replace_source' in request.GET:
        return replace_annotation_via_POST(context, request)
    return create_annotation(context, request)

def create_annotation(context, request):

    try:
        annotation = _annotationFromRequest(request)
    except ValueError, e:
        return HTTPBadRequest(e.message)

    uuid = context.add(annotation)
    new_url = model_url(annotation, request)
    new_ref = URIRef(new_url)

    r_graph = Graph()
    for triple in _getAnnotationTriples(annotation, request):
        r_graph.set(triple)
    serialized = r_graph.serialize()

    headers = [('Location', new_url)]
    return Response(body=serialized,
                    status='201 Created',
                    headerlist=headers,
                   )

def replace_annotation_via_POST(context, request):
    try:
        replacement = _annotationFromRequest(request)
    except ValueError, e:
        return HTTPBadRequest(e.message)

    this_url = model_url(context, request)
    target_url = request.GET['replace_source']
    uuid = target_url[len(this_url):] # XXX slash?
    if uuid.endswith('/'):
        uuid = uuid[:-1]

    replacement.__parent__ = context
    replacement.__name__ = uuid
    context.replace(uuid, replacement)

    r_graph = Graph()
    for triple in _getAnnotationTriples(replacement, request):
        r_graph.set(triple)
    serialized = r_graph.serialize()

    return Response(body=serialized,
                    status='200 OK',
                   )
