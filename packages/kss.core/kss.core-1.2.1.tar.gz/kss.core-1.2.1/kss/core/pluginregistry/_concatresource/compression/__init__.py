'''\
Preprocess resource files by applying compression on them
'''

__all__ = ('compress', )

from javascript import compress as compress_javascript
from css import compress as compress_css

compress_methods = {    
    'application/x-javascript': compress_javascript,
    'text/css': compress_css,
    }

default_compress_method = lambda text: text

def compress(data, content_type, compress_level):
    'Returns compressed text for a given content type'
    method = compress_methods.get(content_type, default_compress_method)
    return method(data, compress_level)
