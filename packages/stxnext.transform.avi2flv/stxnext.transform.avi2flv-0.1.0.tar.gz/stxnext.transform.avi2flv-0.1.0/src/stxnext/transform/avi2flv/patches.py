from Products.CMFCore.utils import getToolByName

def patched_setFile(self, value, **kwargs):
    """
    Convert AVI fo FLV if uploaded file has recognized content type.
    """
    if value:
        portal_transforms = getToolByName(self, 'portal_transforms')
        if 'avi_to_flv' in portal_transforms and value.headers.get('content-type') in portal_transforms.avi_to_flv.inputs:
            flv_data = portal_transforms.convert('avi_to_flv', value.read()).getData()

            open('/tmp/sample.flv', 'w').write(flv_data)

            ## replace AVI content with new FLV
            value.seek(0)
            value.truncate(0)
            value.write(flv_data)
            value.seek(0)

            ## update content type and filename
            value.headers['content-type'] = 'video/x-flv'
            if value.filename.endswith('AVI') or value.filename.endswith('avi'):
                value.filename = value.filename[:-3] + 'flv'

    self._setATCTFileContent(value, **kwargs)
