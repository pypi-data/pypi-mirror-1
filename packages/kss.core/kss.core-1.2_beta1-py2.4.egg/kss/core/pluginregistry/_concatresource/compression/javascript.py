'''\
The javascript compressor uses the 3rdparty packer module
that is taken from Plone's ResourceRegistries.'''

from thirdparty.packer import JavascriptPacker

jspacker_safe = JavascriptPacker('safe')
jspacker_full = JavascriptPacker('full')

def compress(data, compress_level):
    if compress_level == "safe":
        return jspacker_safe.pack(data)
    elif compress_level == "full":
        return jspacker_full.pack(data)
    else:
        # none
        return data
