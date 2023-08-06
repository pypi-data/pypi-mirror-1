import docutils.core
import subprocess
from webob import Response

class Graphviz(object):
    def __init__(self, content):
        """create a Graphviz object"""
        process = subprocess.Popen(['dot', '-Tpng'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        self.image, _ = process.communicate(content)

    def __call__(self, environ, start_response):
        """return a WSGI response"""
        return Response(content_type='image/png', body=self.image)(environ, start_response)   

class RestructuredText(object):
    settings = { 'report_level': 5 }

    def __init__(self, content):
        """template: genshi(?) template to use (???)"""
        self.html = docutils.core.publish_string(content,
                                                 writer_name='html',
                                                 settings_overrides=self.settings)

    def __call__(self, environ, start_response):
        """return a WSGI response"""
        return Response(content_type='text/html', body=self.html)(environ, start_response)
