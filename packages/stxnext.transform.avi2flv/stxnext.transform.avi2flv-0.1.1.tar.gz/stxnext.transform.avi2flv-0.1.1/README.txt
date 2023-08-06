=========================
stxnext.transform.avi2flv
=========================

Overview
========

Converts clips from AVI format to FLV during upload to Plone.


Requirements
============

This package uses FFmpeg. You need to install it in you system.

On Ubuntu 9.04 you have to execute::
    
    sudo apt-get install ffmpeg libavcodec-unstripped-52

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


References
==========

.. Plone: http://plone.org



Author & Contact
================

:Author:
    Wojciech Lichota <``wojciech.lichota@stxnext.pl``>

.. image:: http://stxnext.pl/open-source/files/stx-next-logo

**STX Next** Sp. z o.o.

http://stxnext.pl

info@stxnext.pl
