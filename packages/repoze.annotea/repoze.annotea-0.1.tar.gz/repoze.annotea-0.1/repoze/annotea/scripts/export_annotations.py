"""\
 bin/export_annotations <options>* 

Export annotations to an RDF file.

'OPTIONS' can include:

--verbose (-v)    Emit more output.

--quiet (-q)      Emit no non-essential output.

--zodb-uri (-z)   ZODB URI to use (default is file:///`pwd`/Data.fs).

--base-url (-u)   Base URL for the annotation service (default is
                  'http://localhost:8080/').

--help            Print this help message.

"""
import getopt
import os
import sys

class AnnotationDumper:

    verbose = 1
    zodb_uri = None
    base_url = None

    def __init__(self, argv):
        self.argv = argv
        self.parseOptions(argv)
        self.wsgi_environ = {}

    def usage(self, message=None, rc=1):
        print __doc__
        if message is not None:
            print ''
            print message
            print ''
        sys.exit(rc)

    def parseOptions(self, argv):
        try:
            options, arguments = getopt.gnu_getopt(argv[1:],
                                                   'vqz:u:h?',
                                                   ['verbose',
                                                    'quiet',
                                                    'zodb-url=',
                                                    'base-url=',
                                                    'help',
                                                   ])
        except getopt.GetoptError, e:
            self.usage(str(e))

        for k, v in options:

            if k in ('-v', '--verbose'):
                self.verbose += 1

            elif k in ('-q', '--quiet'):
                self.verbose = 0

            elif k in ('-z', '--zodb-uri'):
                self.zodb_uri = v

            elif k in ('-u', '--base-uri'):
                self.base_url = v

            elif k in ('-h', '-?', '--help'):
                self.usage(rc=2)

            else:
                self.usage('Unknown option: %s' % k)

        if self.base_url is None:
            self.base_url = 'http://localhost:8080/'

        if self.zodb_uri is None:
            self.zodb_uri = 'file://%s/Data.fs' % os.getcwd()


    def getService(self):
        from repoze.zodbconn.finder import PersistentApplicationFinder
        from repoze.annotea.main import appmaker
        get_root = PersistentApplicationFinder(self.zodb_uri, appmaker)
        return get_root(self.wsgi_environ)


    def getGraph(self):
        from rdflib import Namespace
        from rdflib.Graph import ConjunctiveGraph
        graph = ConjunctiveGraph()
        for prefix, url in NS.items():
            graph.namespace_manager.bind(prefix, Namespace(url))

        return graph

    def do_dump(self):
        from repoze.annotea.views.utils import _getAnnotationTriples
        service = self.getService()
        request = FauxRequest(self.base_url)
        graph = self.getGraph()

        for uuid, annotation in service.items():
            for triple in _getAnnotationTriples(annotation, request):
                graph.set(triple)

        graph.serialize(sys.stdout)

    def __call__(self):

        if self.verbose > 0:
            print >> sys.stderr, '=' * 78
            print >> sys.stderr, 'Exporting Annotations'
            print >> sys.stderr, '=' * 78

            print >> sys.stderr, 'Base URL : ', self.base_url
            print >> sys.stderr, 'ZODB URI : ', self.zodb_uri

        self.do_dump()

        if self.verbose:
            print

NS = {
    'annotea': 'http://www.w3.org/2000/10/annotation-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'http': 'http://www.w3.org/1999/xx/http#',
}

class FauxRequest:

    def __init__(self, application_url):
        self.application_url = application_url

def main(argv=sys.argv):
    dumper = AnnotationDumper(argv)
    dumper()

if __name__ == '__main__':
    main()
