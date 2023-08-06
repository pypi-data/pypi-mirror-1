import docutils.core
import subprocess
from webob import Request, Response

class Transformer(object):
    """abstract base class for transformer objects"""
    def __init__(self, content, content_type):
        self.content = content
        self.content_type = content_type

    def transform(self, request):
        """returns a tuple of (body, content-type)"""
        raise NotImplementedError

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.get_response(request)
        return response(environ, start_response)

    def get_response(self, request):
        if request.GET.get('format') == 'raw':
            return Response(content_type=self.content_type, body=self.content)
        content_type, body = self.transform(request)
        return Response(content_type=content_type, body=body)
        

class Graphviz(Transformer):
    def transform(self, request):
        """create a Graphviz object"""
        process = subprocess.Popen(['dot', '-Tpng'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        image, _ = process.communicate(self.content)
        return ('image/png', image)

class RestructuredText(Transformer):
    settings = { 'report_level': 5 }

    def transform(self, request):
        """template: genshi(?) template to use (???)"""
        html = docutils.core.publish_string(self.content,
                                            writer_name='html',
                                            settings_overrides=self.settings)
        return ('text/html', html)
