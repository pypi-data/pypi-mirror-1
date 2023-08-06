import os
from zope.interface import Interface, Attribute, implements
from zope.component import queryUtility
from zope.component import getMultiAdapter
from zope.component import ComponentLookupError
from repoze.bfg.threadlocal import get_current_registry
from webob import Response
from webob.exc import HTTPFound
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.path import caller_package
from repoze.bfg.templating import renderer_from_cache
from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
from repoze.bfg.chameleon_zpt import _auto_reload
#from repoze.bfg.security import ViewPermissionFactory
from repoze.bfg.security import has_permission

class ITile(Interface):
    """returns on call some HTML snippet."""
    
    def __call__(model, request):
        """Renders the tile.
        
        It's intended to work this way: First it calls its own prepare method, 
        then it checks its own show attribute. If this returns True it renders 
        the template in the context of the ITile implementing class instance.  
        """
        
    def prepare():
        """Prepares the tile.
        
        I.e. fetch data to display ... 
        """
        
    show = Attribute("""Render this tile?""")
    
def _update_kw(**kw):
    if not ('request' in kw and 'model' in kw):
        raise ValueError, "Eexpected kwargs missing: model, request."
    kw.update({'tile': TileRenderer(kw['model'], kw['request'])})    
    return kw

def _redirect(kw):
    if kw['request'].environ.get('redirect'):
        return True
    return False
    
def render_template(path, **kw):
    kw = _update_kw(**kw)
    if _redirect(kw):
        return u''
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer(**kw)    
    
def render_template_to_response(path, **kw):
    kw = _update_kw(**kw)
    kw['request'].environ['redirect'] = None
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload)
    result = renderer(**kw)
    if _redirect(kw):
        return HTTPFound(location=kw['request'].environ['redirect'])
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
    
class Tile(object):
    implements(ITile)
    
    def __init__(self, path, attribute):
        self.path = path
        self.attribute = attribute

    def __call__(self, model, request):
        self.model = model
        self.request = request
        self.prepare() # XXX maybe remove.
        if not self.show:
            return u''
        if self.path:
            try:
                # XXX: do not catch exception.
                return render_template(self.path, request=request,
                                       model=model, context=self)
            except Exception, e:
                return u"Error:<br /><pre>%s</pre>" % e
        renderer = getattr(self, self.attribute)
        result = renderer()
        return result
    
    @property
    def show(self): 
        return True
    
    def prepare(self): 
        pass
    
    def render(self):
        return u''
    
    def redirect(self, url):
        self.request.environ['redirect'] = url
    
    @property
    def nodeurl(self):
        relpath = [p for p in self.model.path if p is not None]
        return '/'.join([self.request.application_url] + relpath)

class TileRenderer(object):
    
    def __init__(self, model, request):
        self.model, self.request = model, request
    
    def __call__(self, name):
        registry = get_current_registry()
        # XXX fix me. new API in repoze.bfg
        #secured = not not registry.queryUtility(IAuthenticationPolicy)
        #if secured:
        #    permitted = registry.getMultiAdapter((self.model, self.request),
        #                                         IViewPermission,
        #                                         name=name)
        #    if not permitted:
        #        return u'permission denied'
        try:
            tile = getMultiAdapter((self.model, self.request), ITile, name=name)
        except ComponentLookupError, e:
            return u"Tile with name '%s' not found:<br /><pre>%s</pre>" % \
                   (name, e)
        return tile

# Registration        
def registerTile(name, path=None, attribute='render',
                 interface=Interface, _class=Tile, permission='view'):
    if isinstance(interface, basestring):
        pass # XXX: lookup
    if path:
        if not (':' in path or os.path.isabs(path)): 
            caller = caller_package(level=1)
            path = '%s:%s' % (caller.__name__, path)
    factory = _class(path, attribute)
    registry = get_current_registry()
    registry.registerAdapter(factory, [interface, IRequest],
                             ITile, name, event=False)
    # XXX fix me. new API in repoze.bfg
    #if permission:
    #    factory = ViewPermissionFactory(permission)
    #    registry.registerAdapter(factory, [interface, IRequest],
    #                             IViewPermission, name)
    
class tile(object):
    """Tile decorator.
    """
    
    def __init__(self, name, path=None, attribute='render',
                 interface=Interface, permission='view', level=2):
        """name to register as, path to template, interface adapting to.
        level is a special to make doctests pass the magic path-detection.
        you should never need latter. 
        """
        self.name = name
        self.path = path
        if path:
            if not (':' in path or os.path.isabs(path)): 
                caller = caller_package(level)
                self.path = '%s:%s' % (caller.__name__, path)
        self.attribute = attribute
        self.interface = interface
        self.permission = permission

    def __call__(self, ob):
        registerTile(self.name,
                     self.path,
                     self.attribute,
                     interface=self.interface,
                     _class=ob,
                     permission=self.permission)
        return ob