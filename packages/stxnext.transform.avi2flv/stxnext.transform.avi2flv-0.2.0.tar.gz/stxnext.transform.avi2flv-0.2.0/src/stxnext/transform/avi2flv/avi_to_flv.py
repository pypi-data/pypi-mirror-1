from Products.PortalTransforms.interfaces import itransform

from avi2flv import converter, FFMPEG_OPTS


class Avi2Flv(object):
    """
    Transform which converts from AVI fo FLV.
    """
    __implements__ = itransform

    __name__ = 'avi_to_flv'
    output = 'video/x-flv'

    def __init__(self, name=None, inputs=('video/x-avi', 'video/x-msvideo'), ffmpeg_opts=FFMPEG_OPTS):
        self.config = {
            'inputs' : inputs,
            'ffmpeg_opts': ffmpeg_opts,
        }
        self.config_metadata = {
            'inputs': ('list',
                       'Inputs',
                       'Input(s) MIME type. Change with care.'),
            'ffmpeg_opts': ('string',
                            'FFmpeg options',
                            'FFmpeg convert options'),
            }
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, avi_data, data, **kwargs):
        flv_data = converter(avi_data, self.config.get('ffmpeg_opts', FFMPEG_OPTS))
        data.setData(flv_data)
        return data


def register():
    return Avi2Flv()
