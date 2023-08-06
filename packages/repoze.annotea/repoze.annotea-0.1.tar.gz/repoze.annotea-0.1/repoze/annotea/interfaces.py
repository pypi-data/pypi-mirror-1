from rdflib import URIRef
from zope.interface import Attribute
from repoze.bfg.interfaces import ILocation
from repoze.folder.interfaces import IFolder

# RDF Namespaces / tokens
RDF_TYPE = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
ANNOTEA_TYPE = URIRef('http://www.w3.org/2000/10/annotation-ns#Annotation')
ANNOTEA_ANNOTATES = URIRef('http://www.w3.org/2000/10/annotation-ns#annotates')
ANNOTEA_BODY = URIRef('http://www.w3.org/2000/10/annotation-ns#body')
ANNOTEA_CREATED = URIRef('http://www.w3.org/2000/10/annotation-ns#created')
ANNOTEA_CONTEXT = URIRef('http://www.w3.org/2000/10/annotation-ns#context')
DC_TITLE = URIRef('http://purl.org/dc/elements/1.1/title')
DC_CREATOR = URIRef('http://purl.org/dc/elements/1.1/creator')
DC_DATE = URIRef('http://purl.org/dc/elements/1.1/date')
HTML_BODY = URIRef('http://www.w3.org/1999/xx/http#Body')

class IAnnotation(ILocation):
    """ Annotations represent externally-specified metadata about a resource.

    - Each annotation targets a specific resource, via its URI.

    - The body of an annotation may be stored within the annotation or
      referenced via an external URI.
    """
    types = Attribute(u'What types apply to this annotation?\n\n'
                      'A sequece of RDF resource URIs.')
    annotates = Attribute(u'Target resource for the annotation.\n\n'
                        'An RDF resource URI.')
    title = Attribute(u'Title for the annotation.')
    context = Attribute(u'Sub-element of the annotated resource.\n\n'
                         'Must be an XPointer expression, if present')
    creator = Attribute(u'Entity responsible for creating the Annotation.')
    created = Attribute(u'Date the annotation was created.')
    modified = Attribute(u'Date the annotation was last modified.')
    body_uri = Attribute(u"External URI of the annotation body.\n\n"
                          "If None, then 'body_text' holds the body.")
    body_text = Attribute(u'The annotation body, as XHTML.')


class IAnnotationService(IFolder, ILocation):
    """ Container for annotation objects.
    """
    def add(annotation):
        """ Add an annotation to the container, and index it.

        o 'annotation' must be an IAnnotation;  otherwise, raise ValueError.
        
        o Compute a new UUID for the annotation, and set its '__name__' and
          '__parent__'.

        o Return the UUID of the annotation, which is also its key
          within the container.
        """

    def search(types=None, annotates=None):
        """ Enumerate annotations matching supplied criteria.

        o 'types', if supplied, must be a sequence of URIRefs pointing
          to RDF type URIs.

        o 'annotates', if supplied, must be a single URIRef pointing to
          the annotated resource.

        o Return a sequence of IAnnotation objects.
        """

    def replace(uuid, annotation):
        """ Replace an existing annotation with a new one.

        o 'uuid' should be the UUID of a previously-added annotation.

        o 'annotation' must be an IAnnotation;  otherwise, raise ValueError.
        """

    def remove(annotation_or_uuid):
        """ Remove an annotation from the container.

        o 'annotation_or_uuid' must be either an IAnnotation or its UUID.

        o Raise KeyError if the annotation is not currently contained.
        """
