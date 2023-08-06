from genshi.template import TemplateLoader
from pkg_resources import resource_filename
from webob import Response

class GenshiView(object):
    template = None

    def __init__(self, app, request):
        self.request = request
        self.data = { 'request': request }

        # template loader : this should probably move up the chain
        self.loader = app.loader


    @classmethod
    def match(self, request):
        raise NotImplementedError

    def __call__(self):
        # sanity check
        if not self.template:
            raise NotImplementedError

        # render the template
        template = self.loader.load(self.template)
        return Response(content_type='text/html', body=template.generate(**self.data).render())

class Index(GenshiView):
    template = 'index.html'

class BlogSpace(GenshiView):
    pass
