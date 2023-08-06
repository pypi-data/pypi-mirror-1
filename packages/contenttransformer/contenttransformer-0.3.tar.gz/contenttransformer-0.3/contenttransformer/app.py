import os
import sys
from fnmatch import fnmatch
from mimetypes import guess_type
from paste.fileapp import FileApp
from pkg_resources import iter_entry_points

class FileTypeTransformer(object):

    def __init__(self, *types, **kwargs):
        """types is a list of two-tuples: glob pattern (string), transformer name (string, name of entry point)"""
        self.types = types

        # intended to be arguments to the xformers
        # XXX unused
        self.kwargs = kwargs

        self.transformers = transformers()
        for pattern, transformer_name in self.types:
            assert transformer_name in self.transformers

    def __call__(self, path): 
        """this should return something that is callable with (environ, start_response) to return a response; the transformer thing"""
        filename = os.path.basename(path)
        for pattern, transformer_name in self.types:
            if fnmatch(filename, pattern):
                content_type, _ = guess_type(filename)
                content = file(path).read()
                return self.transformers[transformer_name](content, content_type)
        return FileApp(path)


def transformers():
    transformers = {} # XXX could cache
    for entry_point in iter_entry_points('content_transformers'):
        try:
            transformers[entry_point.name] = entry_point.load()
        except:
            raise # XXX
    return transformers
        
