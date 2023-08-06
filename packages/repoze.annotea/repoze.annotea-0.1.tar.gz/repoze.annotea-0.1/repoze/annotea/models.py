from uuid import uuid1

from zope.interface import implements

from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.folder import Folder

from repoze.annotea.interfaces import IAnnotation
from repoze.annotea.interfaces import IAnnotationService
from repoze.annotea.interfaces import ANNOTEA_TYPE

class Annotation(object):
    implements(IAnnotation)

    # Defaults
    __name__ = None
    __parent__ = None

    types = (ANNOTEA_TYPE,)
    annotates = None
    context = None
    title = u''
    creator = u''
    created = None
    modified = None
    body_uri = None
    body_text = ''

class AnnotationService(Folder):
    implements(IAnnotationService)

    __name__ = None
    __parent__ = None

    def __init__(self):
        super(AnnotationService, self).__init__()
        cat = self.catalog = Catalog()
        cat['types'] = CatalogKeywordIndex(get_annotation_types)
        cat['annotates'] = CatalogFieldIndex(get_annotates)
        self.document_map = DocumentMap()

    def add(self, annotation):
        """ See IAnnotationService.
        """
        if not IAnnotation.providedBy(annotation):
            raise ValueError('Not an IAnnotation: %s' % annotation)
        uuid = annotation.__name__ = str(uuid1())
        annotation.__parent__ = self
        self[uuid] = annotation
        docid = self.document_map.add(uuid)
        self.catalog.index_doc(docid, annotation)
        return uuid

    def replace(self, uuid, annotation):
        """ See IAnnotationService.
        """
        if not IAnnotation.providedBy(annotation):
            raise ValueError('Not an IAnnotation: %s' % annotation)
        annotation.__name__ = uuid
        annotation.__parent__ = self
        self[uuid] = annotation
        docid = self.document_map.docid_for_address(uuid)
        self.catalog.index_doc(docid, annotation)

    def search(self, types=None, annotates=None):
        """ See IAnnotationService.
        """
        query = {}
        if types is not None:
            query['types'] = types
        if annotates is not None:
            query['annotates'] = (annotates, annotates) # stupid field index
        count, results = self.catalog.search(**query)
        found_ids = map(self.document_map.address_for_docid, results)
        return [self[x] for x in found_ids]

    def remove(self, annotation_or_uuid):
        """ See IAnnotationService.
        """
        if IAnnotation.providedBy(annotation_or_uuid):
            uuid = annotation_or_uuid.__name__
        else:
            uuid = annotation_or_uuid
        docid = self.document_map.docid_for_address(uuid)
        if docid is None:
            raise KeyError(uuid)
        del self[uuid]
        self.catalog.unindex_doc(docid)

def get_annotation_types(object, default):
    if IAnnotation.providedBy(object):
        return object.types
    return default

def get_annotates(object, default):
    if IAnnotation.providedBy(object):
        return object.annotates
    return default
