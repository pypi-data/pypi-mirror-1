import unittest

class AnnotationTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.annotea.models import Annotation
        return Annotation

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_IAnnotation(self):
        from zope.interface.verify import verifyClass
        from repoze.annotea.interfaces import IAnnotation
        verifyClass(IAnnotation, self._getTargetClass())

    def test_class_conforms_to_ILocation(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ILocation
        verifyClass(ILocation, self._getTargetClass())

    def test_instance_conforms_to_IAnnotation(self):
        from zope.interface.verify import verifyObject
        from repoze.annotea.interfaces import IAnnotation
        verifyObject(IAnnotation, self._makeOne())

    def test_instance_conforms_to_ILocation(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ILocation
        verifyObject(ILocation, self._makeOne())

class AnnotationServiceTests(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.annotea.models import AnnotationService
        return AnnotationService

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeAnnotation(self):
        from zope.interface import implements
        from repoze.annotea.interfaces import IAnnotation
        class DummyAnnotation:
            implements(IAnnotation)
            types = ('%s/type#AAA' % EXAMPLE_COM,
                     '%s/type#BBB' % EXAMPLE_COM,
                    )
            annotates = EXAMPLE_COM
        return DummyAnnotation()

    def test_class_conforms_to_IAnnotationService(self):
        from zope.interface.verify import verifyClass
        from repoze.annotea.interfaces import IAnnotationService
        verifyClass(IAnnotationService, self._getTargetClass())

    def test_class_conforms_to_ILocation(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ILocation
        verifyClass(ILocation, self._getTargetClass())

    def test_instance_conforms_to_IAnnotationService(self):
        from zope.interface.verify import verifyObject
        from repoze.annotea.interfaces import IAnnotationService
        verifyObject(IAnnotationService, self._makeOne())

    def test_instance_conforms_to_ILocation(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ILocation
        verifyObject(ILocation, self._makeOne())

    def test_empty_search(self):
        service = self._makeOne()

        results = service.search(annotates=EXAMPLE_COM)
        self.assertEqual(len(results), 0)

        results = service.search(types=['%s/type#AAA' % EXAMPLE_COM])
        self.assertEqual(len(results), 0)

    def test_add_non_IAnnotation_raises_ValueError(self):
        service = self._makeOne()
        self.assertRaises(ValueError, service.add, object())

    def test_add_returns_UUID_key(self):
        service = self._makeOne()
        annotation = self._makeAnnotation()
        uuid = service.add(annotation)
        self.assertEqual(uuid, annotation.__name__)
        self.failUnless(annotation.__parent__ is service)
        self.failUnless(service[uuid] is annotation)

    def test_add_indexes_annotation(self):
        service = self._makeOne()
        annotation = self._makeAnnotation()
        uuid = service.add(annotation)

        results = service.search(annotates=EXAMPLE_COM)
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation)

        results = service.search(types=['%s/type#AAA' % EXAMPLE_COM])
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation)

    def test_replace_indexes_annotation(self):
        service = self._makeOne()
        annotation = self._makeAnnotation()
        annotation.annotates = 'http://other.example.com/'
        uuid = service.add(annotation)

        annotation2 = self._makeAnnotation()
        service.replace(uuid, annotation2)

        results = service.search(annotates=EXAMPLE_COM)
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation2)

        results = service.search(types=['%s/type#AAA' % EXAMPLE_COM])
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation2)

    def test_remove_nonesuch_annotation(self):
        service = self._makeOne()
        annotation = self._makeAnnotation()
        annotation.__name__ = 'ABCD'
        self.assertRaises(KeyError, service.remove, annotation)

    def test_remove_nonesuch_uuid(self):
        service = self._makeOne()
        self.assertRaises(KeyError, service.remove, 'ABCDEF')

    def test_remove_w_annotation_unindexes_annotation(self):
        service = self._makeOne()
        annotation1 = self._makeAnnotation()
        uuid1 = service.add(annotation1)
        annotation2 = self._makeAnnotation()
        uuid2 = service.add(annotation2)

        service.remove(annotation1)

        results = service.search(annotates=EXAMPLE_COM)
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation2)

        results = service.search(types=['%s/type#AAA' % EXAMPLE_COM])
        self.assertEqual(len(results), 1)
        self.failUnless(results[0] is annotation2)

    def test_remove_w_uuid_unindexes_annotation(self):
        service = self._makeOne()
        annotation1 = self._makeAnnotation()
        uuid1 = service.add(annotation1)
        annotation2 = self._makeAnnotation()
        uuid2 = service.add(annotation2)

        service.remove(uuid1)

        count, results = service.catalog.search(
                                annotates=(EXAMPLE_COM, EXAMPLE_COM))
        self.assertEqual(count, 1)
        found = service.document_map.address_for_docid(results[0])
        self.assertEqual(found, uuid2)

        count, results = service.catalog.search(
                                types='%s/type#AAA' % EXAMPLE_COM)
        self.assertEqual(count, 1)
        found = service.document_map.address_for_docid(results[0])
        self.assertEqual(found, uuid2)

EXAMPLE_COM = 'http://example.com/'
