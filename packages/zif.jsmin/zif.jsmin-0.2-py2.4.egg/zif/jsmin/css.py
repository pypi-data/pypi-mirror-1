'''\
The css compressor uses the 3rdparty packer module
that is taken from Plone's ResourceRegistries.
'''

from thirdparty.packer import CSSPacker

csspacker_safe = CSSPacker('safe')
csspacker_full = CSSPacker('full')

def compress(data, compress_level):
    if compress_level == "safe":
        return csspacker_safe.pack(data)
    elif compress_level == "full":
        return csspacker_full.pack(data)
    else:
        # none
        return data
