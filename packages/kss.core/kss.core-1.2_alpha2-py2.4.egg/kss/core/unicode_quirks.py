
class AzaxUnicodeError(RuntimeError):
    pass

def force_unicode(value, encoding='ascii'):
    'Force value to be unicode - allow also value in a specific encoding (by default, ascii).'
    if isinstance(value, str):
        try:
            value = unicode(value, encoding)
        except UnicodeDecodeError, exc:
            raise AzaxUnicodeError, 'Content must be unicode or ascii string, original exception: %s' % (exc, )
    else:
        assert isinstance(value, unicode)
    return value
