from rdflib.Graph import Graph
from webob import Response
from webob.exc import HTTPBadRequest
from webob.exc import HTTPMovedPermanently

from repoze.annotea.views.utils import _annotationFromRequest
from repoze.annotea.views.utils import _getAnnotationTriples

def get_annotation(context, request):
    graph = Graph()
    for triple in _getAnnotationTriples(context, request):
        graph.set(triple)
    headers = [('Content-type', 'application/xml')]
    return Response(body=graph.serialize(),
                    headerlist=headers)

def get_body(context, request):
    if context.body_uri is not None:
        return HTTPMovedPermanently(location=str(context.body_uri))

    headers = [('Content-type', 'text/html; charset=UTF-8')]
    return Response(body=context.body_text,
                    headerlist=headers)

def replace_annotation(context, request):
    try:
        replacement = _annotationFromRequest(request)
    except ValueError, e:
        return HTTPBadRequest(e.message)

    service = context.__parent__
    uuid = context.__name__
    service.replace(uuid, replacement)

    r_graph = Graph()
    for triple in _getAnnotationTriples(replacement, request):
        r_graph.set(triple)
    serialized = r_graph.serialize()

    return Response(body=serialized,
                    status='200 OK',
                   )

def remove_annotation(context, request):
    uuid = context.__name__
    service = context.__parent__
    service.remove(uuid)

    return Response(status='200 OK',
                   )
