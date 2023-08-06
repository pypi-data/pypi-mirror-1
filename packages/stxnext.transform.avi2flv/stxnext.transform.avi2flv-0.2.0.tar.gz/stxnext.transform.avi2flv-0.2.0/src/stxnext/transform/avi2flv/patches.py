from os.path import splitext
from Products.CMFCore.utils import getToolByName

def convert_fileupload(value, context):
    if value:
        portal_transforms = getToolByName(context, 'portal_transforms')
        if 'avi_to_flv' in portal_transforms and value.headers.get('content-type') in portal_transforms.avi_to_flv.inputs:
            flv_data = portal_transforms.convert('avi_to_flv', value.read()).getData()

            ## replace AVI content with new FLV
            value.seek(0)
            value.truncate(0)
            value.write(flv_data)
            value.seek(0)

            ## update content type and filename
            value.headers['content-type'] = 'video/x-flv'
            name, ext = splitext(value.filename)
            value.filename = name + '.flv'

    return value

def patched_setFile(self, value, **kwargs):
    """
    Convert AVI fo FLV if uploaded file has recognized content type.
    """
    value = convert_fileupload(value, context=self)
    self._setATCTFileContent(value, **kwargs)
