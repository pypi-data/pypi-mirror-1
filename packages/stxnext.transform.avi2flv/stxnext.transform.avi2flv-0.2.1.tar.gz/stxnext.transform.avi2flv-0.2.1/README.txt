=========================
stxnext.transform.avi2flv
=========================

Overview
========

Converts clips from AVI format to FLV during upload to `Plone`_.

It is fairly easy to turn on conversion from other video formats - more information in section "Configuration".


Requirements
============

This package uses FFmpeg. You need to install it in you system.

On Ubuntu 9.04 you have to execute::
    
    sudo apt-get install ffmpeg libavcodec-unstripped-52

On CentOS 5.3 command is even simpler::

    sudo yum install ffmpeg

On other linux system compile FFmpeg with flv and mp3 support.


Installation
============

If you are using zc.buildout to manage your project, you can do this:

* Add ``stxnext.transform.avi2flv`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        stxnext.transform.avi2flv
      
* Re-run buildout, e.g. with::

    $ ./bin/buildout
        
Finally go to 'Site Setup' -> 'Add/Remove Products' and install stxnext.transform.avi2flv.


Usage
=====

AVI clips will be automatically converted, so no special attention by editor is needed.


Configuration
=============

Options for FFmpeg that controls quality of output video can be configured via ZMI
(portal_transforms -> avi_to_flv).

With default configuration it will execute command similar to::

    ffmpeg -i "input.avi" -y -b 1024k -r 25 -acodec libmp3lame -ar 44100 'output.flv'

Description of these options and more control parameters you can find in `FFmpeg manual`_.

To turn on conversion from other video formats than "avi", you need to add more mimetypes into "Input" property of avi_to_flv transformation.

We made simple tests with formats:
 
 * video/x-ms-wmv
 * video/mpeg
 * video/quicktime


References
==========

.. _Plone: http://plone.org
.. _FFmpeg manual: http://ffmpeg.org/ffmpeg-doc.html


Author & Contact
================

:Author:
    Wojciech Lichota <``wojciech.lichota@stxnext.pl``>
    Maciej Zięba <``maciej.zieba@stxnext.pl``>

.. image:: http://stxnext.pl/open-source/files/stx-next-logo

**STX Next** Sp. z o.o.

http://stxnext.pl

info@stxnext.pl
