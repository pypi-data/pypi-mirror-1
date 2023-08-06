import os
import sys
import logging
import inspect

from twisted.web import resource, server

from broadwick.web.utils import isexposedfunc, hasexposed

class Page(resource.Resource):
    modifiedtime = {}
    autoreload = True

    def __init__(self, view, request_adapters=None):
        resource.Resource.__init__(self)
        self.view = view
        self.request_adapters = request_adapters if request_adapters is not None else []

        if self.autoreload and Page.reloadObjectModule(view):
            self.view = self.reloadView(view)

    def reloadView(self, view):
        # We can 
        cls = getattr(inspect.getmodule(self.view), view.__class__.__name__)
        try:
            return cls()
        except Exception:
            logging.warning('Unable to reload view')
            return view

    @classmethod
    def reloadObjectModule(cls, obj):
        reloaded = False
        for objectcls in inspect.getmro(obj.__class__)[::-1]:
            if objectcls.__module__.startswith('__'):
                continue

            module = inspect.getmodule(objectcls)
            filename = inspect.getsourcefile(module)
            modified = os.stat(filename).st_mtime

            cls.modifiedtime.setdefault(filename, modified)
            # logging.debug('%s modified at %s' % (filename, modified))

            if reloaded or cls.modifiedtime[filename] < modified:
                logging.info('Reloading module %s' % module.__name__)
                # The module may not be in sys.modules if a previous reload attempt failed
                try:
                    sys.modules[module.__name__]
                except KeyError:
                    import module.__name__
                else:
                    reload(module)
                reloaded = True
                cls.modifiedtime[filename] = modified
        return reloaded

    def getChild(self, path, request):
        logging.debug('getChild %r, %r' % (path, request.postpath))


        if request.postpath == []:
            if not path:
                path = 'index.html'
            else:
                root, ext = os.path.splitext(path)
                root_split = root.split('.')
                if len(root_split) > 1:
                    value = getattr(self.view, root_split[0], None)
                    if value is not None:
                        request.postpath = ['.'.join(root_split[1:]) + ext]
                        page = Page(value, self.request_adapters)
                        setattr(self.view, root_split[0], page.view)
                        return page
                    return None
        
        root, ext = os.path.splitext(path)
        value = getattr(self.view, root, None)

        if value is not None:
            if isexposedfunc(value):
                res = value._resources.get(ext)
                if res is not None:
                    res.request_adapters = self.request_adapters
                    res.func = value # Let the resource know the bound version of its func
                    return res
            elif hasexposed(value):
                return Page(value, self.request_adapters)
            elif isinstance(value, resource.Resource):
                return value

        return resource.Resource.getChild(self, path, request)

class Site(server.Site):
    def __init__(self, view, logPath=None, timeout=60*60*12, *args, **kwargs):
        server.Site.__init__(self, Page(view, *args, **kwargs), logPath, timeout)
        self.view = view
        self.args = args
        self.kwargs = kwargs 

    def getResourceFor(self, request):
        self.resource = Page(self.view, *self.args, **self.kwargs)
        # Page may have reloaded the view's module and cloned the view
        # In that case we need to update the view pointer otherwise the next
        # render will result in the old view being used
        self.view = self.resource.view
        return server.Site.getResourceFor(self, request)        

def website(view, *args, **kwargs):
    return Site(view, *args, **kwargs)

