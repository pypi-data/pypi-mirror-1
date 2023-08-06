import docutils.core
import subprocess
from webob import Request, Response

class Transformer(object):
    """abstract base class for transformer objects"""
    def __init__(self, content):
        self.content = content

    def transform(self, request):
        """returns a tuple of (body, content-type)"""
        raise NotImplementedError

    def __call__(self, environ, start_response):
        request = Request(environ)
        content_type, body = self.transform(request)
        return Response(content_type=content_type, body=body)(environ, start_response)

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
