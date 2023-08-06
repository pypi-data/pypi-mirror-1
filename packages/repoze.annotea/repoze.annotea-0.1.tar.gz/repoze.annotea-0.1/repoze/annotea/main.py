from repoze.zodbconn.finder import PersistentApplicationFinder

from repoze.bfg.router import make_app

def appmaker(root,
             transaction=None # parameterized only to serve unit tests
            ):
    if transaction is None:
        import transaction
    if not root.has_key('annotations'):
        from repoze.annotea.models import AnnotationService
        site = root['annotations'] = AnnotationService()
        transaction.commit()
    return root['annotations']

def asbool(s):
    s = str(s).strip()
    return s.lower() in ('t', 'true', 'y', 'yes', 'on', '1')

def get_options(kw):
    from repoze.bfg.registry import get_options
    options = get_options(kw)
    options['evolve_at_startup'] = asbool(kw.get('evolve_at_startup', ''))
    return options

def main(global_config, **kw):
    import repoze.annotea
    zodb_uri = kw.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')
    get_root = PersistentApplicationFinder(zodb_uri, appmaker)
    app = make_app(get_root, repoze.annotea, options=get_options(kw))
    return app
