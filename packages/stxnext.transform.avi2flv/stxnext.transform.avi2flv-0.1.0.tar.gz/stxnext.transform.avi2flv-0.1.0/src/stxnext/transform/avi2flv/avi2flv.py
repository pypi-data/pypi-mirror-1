import os, subprocess, signal, tempfile

FFMPEG_OPTS = '-y -b 1024k -r 25 -acodec libmp3lame -ar 44100'

def converter(avi_data, ffmpeg_opts=None):
    """
    Execute ffmpeg and return FLV file data.
    
    Function operates on temporary files instead of pipes,
    pipes are constantly raising "broken pipe" exceptions
    because of weird python implementation.
    """
    if not ffmpeg_opts:
        ffmpeg_opts = FFMPEG_OPTS
    ffmpeg_cmd = 'ffmpeg -i "%%s" %s "%%s"' % ffmpeg_opts

    in_name = tempfile.mkstemp(suffix='.avi')[1]
    in_file = open(in_name, 'wb')
    in_file.write(avi_data)
    in_file.close()
    out_name = tempfile.mkstemp(suffix='.flv')[1]

    ps = subprocess.Popen(ffmpeg_cmd % (in_name , out_name),
                          bufsize= -1,
                          stderr=open('/dev/null', 'w'),
                          preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL),
                          shell=True)
    ps.communicate()

    out_file = open(out_name)
    flv_data = out_file.read()
    out_file.close()

    os.remove(in_name)
    os.remove(out_name)

    return flv_data

