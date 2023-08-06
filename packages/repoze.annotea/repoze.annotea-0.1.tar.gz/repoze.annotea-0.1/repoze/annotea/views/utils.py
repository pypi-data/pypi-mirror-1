import datetime
from rdflib import BNode
from rdflib import Literal
from rdflib import URIRef
from rdflib.Graph import Graph
from rdflib.util import parse_date_time
from repoze.bfg.traversal import model_url

from repoze.annotea.interfaces import RDF_TYPE
from repoze.annotea.interfaces import ANNOTEA_TYPE
from repoze.annotea.interfaces import ANNOTEA_ANNOTATES
from repoze.annotea.interfaces import ANNOTEA_BODY
from repoze.annotea.interfaces import ANNOTEA_CREATED
from repoze.annotea.interfaces import ANNOTEA_CONTEXT
from repoze.annotea.interfaces import DC_TITLE
from repoze.annotea.interfaces import DC_CREATOR
from repoze.annotea.interfaces import DC_DATE
from repoze.annotea.interfaces import HTML_BODY

TIME_FMT_HH_MM_ZONE = '%Y-%m-%dT%H:%M:%S%Z'
TIME_FMT_HH_MM = '%Y-%m-%dT%H:%M'
TIME_FMT_HH_MMZ = '%Y-%m-%dT%H:%MZ'

def _convertDatetimeString(x):
    try:
        return datetime.datetime.utcfromtimestamp(parse_date_time(x))
    except ValueError:
        pass
    for fmt in (TIME_FMT_HH_MM_ZONE,
                TIME_FMT_HH_MM,
                TIME_FMT_HH_MMZ,
               ):
        try:
            return datetime.datetime.strptime(x, fmt)
        except ValueError:
            pass
    return _now()

def _now(): # hookable for testing
    return datetime.datetime.now()

def _getAnnotationTriples(annotation, request):
    triples = []
    a_url = model_url(annotation, request)
    a_ref = URIRef(a_url)

    for type in annotation.types:
        triples.append((a_ref, RDF_TYPE, type))

    triples.append((a_ref, ANNOTEA_ANNOTATES, annotation.annotates))

    if not isinstance(annotation.title, URIRef):
        title = Literal(annotation.title)
    else:
        title = annotation.title
    triples.append((a_ref, DC_TITLE, title))

    if annotation.context is not None:
        triples.append((a_ref, ANNOTEA_CONTEXT, annotation.context))

    if not isinstance(annotation.creator, URIRef):
        creator = Literal(annotation.creator)
    else:
        creator = annotation.creator
    triples.append((a_ref, DC_CREATOR, creator))

    triples.append((a_ref, ANNOTEA_CREATED,
                    Literal(annotation.created.isoformat())))

    triples.append((a_ref, DC_DATE,
                    Literal(annotation.modified.isoformat())))

    if annotation.body_uri is not None:
        b_ref = annotation.body_uri
    else:
        b_ref = URIRef('%sbody.html' % a_url)
    triples.append((a_ref, ANNOTEA_BODY, b_ref))

    return triples

def _annotationFromRequest(request):
    from repoze.annotea.models import Annotation # avoid cycles

    ct = request.headers['Content-Type']
    if not ct.startswith('application/xml'):
        raise ValueError("Content-type must be 'application/xml'.")
    graph = Graph()

    try:
        graph.parse(request.body_file)
    except Exception, e:
        raise ValueError("Not well-formed XML.")

    subjects = list(graph.subjects(predicate=RDF_TYPE))
    subject = subjects[0]

    types = list(graph.objects(subject=subject, predicate=RDF_TYPE))

    if ANNOTEA_TYPE not in types:
        raise ValueError("No Annotatea resource type provided.")

    annotates = graph.value(subject=subject, predicate=ANNOTEA_ANNOTATES)
    if annotates is None:
        raise ValueError("No 'annotates' target provided.")

    body_triples = list(graph.subject_objects(predicate=ANNOTEA_BODY))
    if len(body_triples) < 1:
        raise ValueError("No body URI / content provided.")
    if len(body_triples) > 1:
        raise ValueError("Multiple body URI / content provided.")

    body = body_triples[0][1]

    now = _now()
    ctx = graph.value(subject=subject, predicate=ANNOTEA_CONTEXT)
    title = graph.value(subject=subject, predicate=DC_TITLE, default=u'')
    creator = graph.value(subject=subject, predicate=DC_CREATOR)
    if creator is None:
        creator = u''

    created = graph.value(subject=subject, predicate=ANNOTEA_CREATED)
    if created is None:
        created = now
    else:
        created = _convertDatetimeString(created)

    modified = graph.value(subject=subject, predicate=DC_DATE)
    if modified is None:
        modified = now
    else:
        modified = _convertDatetimeString(modified)

    annotation = Annotation()
    annotation.types = types
    annotation.annotates = annotates
    annotation.context = ctx and ctx.strip()
    annotation.title = title
    annotation.creator = creator
    annotation.created = created
    annotation.modified = modified

    if isinstance(body, URIRef):
        annotation.body_uri = body
        annotation.body_text = u''
    else:
        annotation.body_uri = None
        text = graph.value(subject=body, predicate=HTML_BODY)
        annotation.body_text = '\n'.join([x.strip()
                                            for x in text.splitlines()]
                                        ).strip()

    return annotation
