'''\
The css compressor uses the 3rdparty packer module
that is taken from Plone's ResourceRegistries.
'''

from thirdparty.packer import CSSPacker
# Packer needs to be created for each packing

def compress(data, compress_level):
    if compress_level == "safe":
        csspacker_safe = CSSPacker('safe')
        return csspacker_safe.pack(data)
    elif compress_level == "full":
        csspacker_full = CSSPacker('full')
        return csspacker_full.pack(data)
    else:
        # none
        return data
