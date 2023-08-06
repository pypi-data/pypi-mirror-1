env = Environment(loader=PackageLoader('nilo.webgallery', 'handler-templates'))

handler_registry = {}
ext_handlers = {}

def registerHandler(handler_instance):
    for_exts = handler_instance.for_exts
    handler_registry[for_exts] = handler_instance
    for ext in for_exts:
        if ext_handlers.has_key(ext):
            ext_handlers[ext].append(for_exts)
        else:
            ext_handlers[ext] = [for_exts]

def getHandler(ext):
    handlers = ext_handlers.get(ext, [])
    if len(handlers) > 1:
        raise ValueError, "more than one handlers found for %s" % ext
    if not handlers:
        return None
    return handler_registry.get(handlers[0])


class BaseHandler(object):
    def __init__(self, template_name, for_exts):
        self.template = env.get_template(template_name)
        self.for_exts = for_exts

    def prepare(self, item):
        pass

    def render(self, item):
        self.prepare(item)
        return self.template.render(context=self)

registerHandler(BaseHandler('base.html', []))


class ImageHandler(BaseHandler):

    def prepare(self, item):
        #create thumbnail...

registerHandler(ImageHandler('image.html', ['jpg', 'jpeg', 'gif', 'png']))

