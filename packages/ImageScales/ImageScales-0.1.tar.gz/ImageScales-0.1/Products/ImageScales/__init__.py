# Patch ATImage's schema to use a method, rather than a literal
# to set image scales.
# Our replacement method will look for properties that may be
# used to override the old scales. If it finds them, it returns
# them. If not, it uses the original scales.


import logging

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content import image

old_sizes = image.ATImageSchema['image'].sizes


def sizes_override(self):
    """
        return custom scales, if available, or old_sizes if not.

        Kupu's support code retrieves scales up to 7 times per
        request, so we'll use the request to cache the computer value.
    """

    cached_scales = getattr(self.REQUEST, '_imageScales', None)
    if cached_scales is not None:
        return cached_scales
    properties_tool = getToolByName(self, 'portal_properties')
    imagescales_properties = getattr(properties_tool, 'imaging_properties', None)
    if imagescales_properties is not None:
        raw_scales = getattr(imagescales_properties, 'allowed_sizes', None)
        if raw_scales is not None:
            myscales = {}
            for line in raw_scales:
                # line format should be "name horiz:vert"
                line = line.strip()
                if line:
                    splits = line.split(' ')
                    if len(splits) == 2:
                        name = splits[0].strip()
                        dims = splits[1].split(':')
                        if len(dims) == 2:
                            try:
                                myscales[name] = tuple(map(int, dims))
                            except ValueError:
                                pass
            self.REQUEST['_imageScales'] = myscales
            return myscales

    return old_sizes


# Apply patch if appropriate
if type(old_sizes) is type({}):
    logging.getLogger("ImageScales").info('Patching ATImage scales')         

    image.ATImage.sizes_override = sizes_override
    image.ATImageSchema['image'].sizes = 'sizes_override'
else:
    logging.getLogger("ImageScales").warning('ATImage scales is not a dict; unable to patch.')         
