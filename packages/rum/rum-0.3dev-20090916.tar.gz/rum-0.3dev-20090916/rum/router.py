import logging
from itertools import count

from peak.util.decorators import decorate_assignment, decorate_class
import routes

from rum.genericfunctions import generic
from rum.util import adapt_call, safe_issubclass
from rum.wsgiutil import RumRequest
from rum import app

__all__ = ["RumRouter", "resource_action", "get_resource_actions"]


log = logging.getLogger(__name__)

class DefaultController(object):
    def __call__(self, environ, start_response):

        next_app = adapt_call(app.controllerfactory, **app.request.routes)
        return next_app(environ, start_response)

# XXX: the router is *very* messy, *must* be cleaned up sometime soon and
#      optimized since it's a very hot path
class RumRouter(object):
    _route_args = frozenset(["parent", "resource", "remote_name", "prefix"])
    def __init__(self, always_scan=True):
        self._controllers = {} # str -> args
        self._controller_keys = {} # args -> str
        self._resource_reg = {}
        self._serial = count(0)
        self.mapper = routes.Mapper(
            register=True,
            always_scan=always_scan,
            controller_scan = self._controllers.keys
            )


    def connect(self, *args, **kw):
        log.debug("Connect called with: %r", locals())
        if len(args) == 1:
            name, route = None, args[0]
        elif len(args) == 2:
            name, route = args
        if kw.get('remote_name') is not None:
            assert 'parent' in kw
            self._resource_reg[(kw['parent'], kw['remote_name'])] = kw['resource']
        args = self._extract_args(kw)
        args['controller'] = kw.pop('controller', DefaultController)
        key = self._add_controller_key(args)
        log.debug("Connect produced key %r", key)
        self.mapper.connect(name, route, controller=key, **kw)
        log.debug("mapper.connect(%r, controller=%r, **%r)", route, key, kw)
        return key

    def _get_resource_actions(self, typ, resource, parent, prefix, remote_name):
        controller_cls = app.controllerfactory.get(
            resource, parent, remote_name, None, prefix, {}
            )
        return get_resource_actions(controller_cls, typ)

    def resource(self, resource, parent=None, prefix=None, remote_name=None):
        # Provide some sane defaults...
        names_for_resource = app.names_for_resource
        plural = remote_name or names_for_resource(resource)[1]
        if parent is not None:
            parent_plural = names_for_resource(parent)[1]

        member = self._get_resource_actions('member', resource, parent,
                                            prefix, remote_name)
        collection = self._get_resource_actions('collection', resource,
                                                parent, prefix,
                                                remote_name)

        connect_args = dict((k,v) for (k,v) in locals().iteritems()
                            if k in self._route_args)
        if parent:
            if prefix:
                prefix = '%s/%s/:(parent_id)' % (prefix, parent_plural)
            else:
                prefix = '%s/:(parent_id)' % parent_plural

        if prefix:
            route_base = prefix + '/' + plural
        else:
            route_base = plural


        def route_args(dct, action, **kw):
            args = dict(conditions=dict(method=[dct[action]]), action=action)
            args.update(connect_args)
            args.update(kw)
            return args

        # Connect collection which their action is in the url
        #
        args = lambda action, **kw: route_args(collection, action, **kw)
        # Connect 'index' when it is implicit
        if 'index' in collection:
            self.connect(route_base + '.:(lang).:(format)', **args('index'))
            self.connect(route_base + '.:(format)', **args('index'))
            self.connect(route_base, **args('index'))
        for action in collection.iterkeys():
            route = '%s/%s' % (route_base, action)
            self.connect(route + '.:(lang).:(format)', **args(action))
            self.connect(route + '.:(format)', **args(action))
            self.connect(route, **args(action))

        # Connect member wich their action is in the url
        #
        args = lambda action, **kw: route_args(member,
                                               action,
                                               requirements={'id': '[^\/]+'},
                                               **kw)
        # Connect 'show' when it is implicit
        if 'show' in member:
            route = route_base + '/:(id)'
            self.connect(route + '.:(lang).:(format)', **args('show'))
            self.connect(route + '.:(format)', **args('show'))
            self.connect(route, **args('show'))
        # Connect '/resource/id/delete' to 'confirm_delete'
        if 'confirm_delete' in member:
            route = route_base + '/:(id)/delete'
            self.connect(route + '.:(lang).:(format)', **args('confirm_delete'))
            self.connect(route + '.:(format)', **args('confirm_delete'))
            self.connect(route, **args('confirm_delete'))
        for action in member.iterkeys():
            route = '%s/:(id)/%s' % (route_base, action)
            self.connect(route + '.:(lang).:(format)', **args(action))
            self.connect(route + '.:(format)', **args(action))
            self.connect(route, **args(action))


        # Connect collection methods which their action is not in the url
        args = dict(conditions=dict(method=['POST']),
                    action='create', **connect_args)
        self.connect(route_base + '.:(lang).:(format)', **args)
        self.connect(route_base + '.:(format)', **args)
        self.connect(route_base, **args)

        # Connect member methods which their action is not in the url
        route = route_base + '/:(id)' 
        args = dict(conditions=dict(method=['PUT']),
                    action='update', **connect_args)
        self.connect(route, **args)
        args = dict(conditions=dict(method=['DELETE']),
                    action='delete', **connect_args)
        self.connect(route, **args)







    def url_for(self, *args, **kw):
        if len(args)>0:
            args=list(args)
            if isinstance(args[0], unicode):
                args[0] = args[0].encode('ascii')
        if len(args) == 1:
            args = list(args)
            arg = args.pop(0)
            if isinstance(arg, basestring):
                # handle external urls
                if 'http' in arg:
                    return arg
                return routes.url_for(arg)
            kw['resource'] = arg

        obj = kw.pop('obj', None)
        if obj:
            kw['resource'] = obj.__class__
            kw['id'] = app.repositoryfactory.get_id(obj)
            kw.setdefault('action', 'show')

        parent_obj = kw.pop('parent_obj', None)
        if parent_obj:
            kw['parent'] = parent_obj.__class__
            kw['parent_id'] = app.repositoryfactory.get_id(parent_obj)

        orig_kw = kw.copy()
        if kw.get('remote_name') and not kw.get('resource'):
            assert 'parent' in kw
            kw['resource'] = self._resource_reg[(kw['parent'],
                                                 kw['remote_name'])]
        config = self.request_config
        use_memory = kw.pop('_memory', True)
        mapper_dict = getattr(config, 'mapper_dict', None)
        if mapper_dict:
            # Propagate lang and format regardless of use_memory
            for k in 'lang', 'format':
                if mapper_dict.get(k) is not None:
                    kw[k] = mapper_dict[k]
            if use_memory:
                # emulate route memory for our special route args
                kw.update((k,v) for (k,v) in mapper_dict.iteritems()
                                if k not in kw and k in self._route_args)
                if 'controller' in mapper_dict.keys():
                    kw.setdefault('controller', mapper_dict['controller'])
                if 'lang' in mapper_dict and mapper_dict['lang'] is None:
                    del mapper_dict['lang']
        if 'id' in kw:
            kw.setdefault('action', 'show')
        c_args = self._extract_args(kw)
        c_args['controller'] = kw.pop('controller', DefaultController)
        try:
            key = self._get_controller_key(c_args)
        except KeyError, e:
            # Try using the DefaultController in case we're being called
            # from another controller and routes memory is screwing up
            controller = c_args['controller']
            if safe_issubclass(controller, DefaultController):
                raise routes.util.RoutesException(str(e))
            orig_kw['controller'] = DefaultController
            return self.url_for(*args, **orig_kw)
        if not use_memory:
            key = '/'+key
        kw['controller'] = key
        # Grab updated resource as left by _get_controller_key
        kw['resource'] = c_args['resource']
        log.debug("routes.url_for(*%r, **%r)", args, kw)
        url = routes.url_for(*args, **kw)
        if hasattr(config, 'environ'):
            url = config.environ['SCRIPT_NAME'] + url
        return url


    @property
    def request_config(self):
        config = routes.request_config()
        assert config.mapper is self.mapper, "Router has not been activaed!"
        return config

    def activate(self, app=None):
        config = routes.request_config()
        if hasattr(config, 'using_request_local'):
            log.debug('Setting request_local')
            request_local = _RumReqLocal()
            config.request_local = lambda: request_local
            config = routes.request_config()
            config.mapper = self.mapper
        return config
        
    def deactivate(self, app=None):
        orig_config = routes.request_config(original=True)
        try:
            del orig_config.request_local
            log.debug('Cleared request_local')
        except AttributeError:
            log.debug('No need to clear request_local')
            pass

    def dispatch(self, environ):
        request = RumRequest(environ)
        new_method = request.params.get('_method')
        if new_method:
            request.method = new_method.upper()
        config = self.request_config
        self.mapper.environ = environ
        result = self.mapper.routematch(request.path_info)
        if result is not None:
            config.mapper_dict, config.route = result[:2]
            self._extend_match(config.mapper_dict)
        else:
            config.mapper_dict, config.route = None, None
        return config.mapper_dict
        
    def _extend_match(self, match):
        if match:
            self._inject_args(match, match['controller'])
            match.setdefault('lang', None)

    def match(self, url):
        match = self.mapper.match(url)
        self._extend_match(match)
        return match



    def _get_controller_key(self, args):
        resource = args['resource']
        # lookup all base classes
        if resource is not None: 
            for klass in resource.__mro__:
                args['resource'] = klass
                try:
                    return self._controller_keys[dct_key(args)]
                except KeyError:
                    pass
            raise KeyError(dct_key(args))
        else:
            return self._controller_keys[dct_key(args)]

    def _add_controller_key(self, args):
        args_key = dct_key(args)
        if args_key in self._controller_keys:
            return self._controller_keys[args_key]
        controller_key = '__auto%d' % self._serial.next() 
        self._controllers[controller_key] = args_key
        self._controller_keys[args_key] = controller_key
        return controller_key

    def _extract_args(self, dct, meth=dict.get):
        return dict((k, meth(dct, k, None)) for k in self._route_args)

    def _inject_args(self, route_dct, controller_key):
        args = self._controllers[controller_key]
        route_dct.update(args) #XXX safe update?


def dct_key(dct):
    """Returns a hashable obj from a dict"""
    return frozenset(dct.iteritems())



def resource_action(typ, method='GET'):
    """
    Tags a controller action as being accesible by given HTTP `method` to
    handle a ``typ`` of either ``member`` or ``collection``.

    Example::

        >>> class DummyController(object):
        ...     @resource_action('collection', 'GET')
        ...     def index(self): pass
        ...     @resource_action('member', 'GET')
        ...     def show(self): pass
        ...     @resource_action('member', 'PUT')
        ...     def update(self): pass

        >>> get_resource_actions(DummyController, 'collection')
        {'index': 'GET'}
        >>> d = get_resource_actions(DummyController, 'member')
        >>> d['update']
        'PUT'
        >>> d['show']
        'GET'

    Actions are inheritted::

        >>> class SubDummyController(DummyController):
        ...     @resource_action('member', 'DELETE')
        ...     def delete(self): pass
        ...     @resource_action('collection', 'POST')
        ...     def index(self): pass

        >>> get_resource_actions(SubDummyController, 'collection')
        {'index': 'POST'}
        >>> d = get_resource_actions(SubDummyController, 'member')
        >>> d['update']
        'PUT'
        >>> d['show']
        'GET'
        >>> d['delete']
        'DELETE'
        
    """
    def callback(frame, name, func, old_locals):
        def register_controller_action(cls):
            methods = resource_action._registry.setdefault(cls, {})
            methods_for_typ = methods.setdefault(typ, {})
            methods_for_typ[name] = method
            return cls
        decorate_class(register_controller_action, frame=frame)
        return func
    return decorate_assignment(callback)
resource_action._registry = {}

def get_resource_actions(cls, typ):
    all = {}
    for c in cls.__mro__[1::-1]: # from base to sub skipping `object`
        all.update(resource_action._registry.get(c, {}).get(typ, {}))
    return all

class _RumReqLocal(object):
    """RumRouter's request local"""
    pass
