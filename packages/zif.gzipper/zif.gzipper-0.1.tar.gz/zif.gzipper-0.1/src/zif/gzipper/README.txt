zif.gzipper

    This is a wsgi middleware application intended for use with paste.deploy,
    zope.paste, and zope3.

    It serves as a wsgi filter to gzip output from a zope3 application.

Dependencies

    for zope3, zif.gzipper requires Sidnei da Silva's zope.paste

    zope.paste is available at http://svn.zope.org/zope.paste/trunk/

    ::

        cd [path.to.zope3.src.directory]/zope
        svn co http://svn.zope.org/zope.paste/trunk/ paste
        
    zope.paste is also available at "the cheese shop":http://cheeseshop.python.org/pypi/zope.paste .

    Instructions for zope.paste are at  "http://awkly.org/2006/01/25/zopepaste-wsgi-applications-in-zope-3-using-pastedeploy/":http://awkly.org/2006/01/25/zopepaste-wsgi-applications-in-zope-3-using-pastedeploy/

    zope.paste requires paste.deploy.  paste.deploy may be obtained from "the 
    cheese shop":http://cheeseshop.python.org/pypi/PasteDeploy .  Presuming you have setuptools installed,

    ::

        sudo easy_install.py PasteDeploy

    This (zif.gzipper) package can be unzipped and installed anywhere on the Python 
        path.

    Setup

        Follow Sidnei's instructions for setting up zope.paste.  It involves putting the
        usual zope.paste-configure.zcml file in [zope3 instance]/etc/site-packages.
        There is also a parameter to change in [zope3 instance]/etc/zope.conf.
        The new twist is a paste.ini file in [zope3 instance]/etc

        My paste.ini file looks like:

    ::

        [pipeline:Paste.Main]
        pipeline = gzipper jsmin main

        [app:main]
        paste.app_factory = zope.paste.application:zope_publisher_app_factory

        [filter:gzipper]
        paste.filter_factory=zif.gzipper.gzipper:filter_factory
        compress_level=6
        exclude=localimages
        nocompress=jp gz zip png
        tempfile=1048576

        [filter:jsmin]
        paste.filter_factory=zif.jsmin.jsmin:filter_factory
        compress_level=safe

Configuration

    gzipper should be the first filter in the pipeline.  Other filters will
    have a hard time reading compressed data output from this filter.

    The paste.ini file above shows examples of the configuration options for gzipper
.

    - *compress_level* is the level of compression for the gzip function. 6 is the
    default.  9 is max.  3 is often good enough.  Higher numbers use more
    processor, but compress smaller.

    - *exclude* is a sequence of strings that appear in the a **filename or path**
    you wish to exclude from gzipping.  If any of these strings appears in the
    path or filename, gzipper will not gzip the file.

    - *nocompress* is a sequence of strings that appear in **content-types** you wish to
    exclude from gzipping.  If the string appears
    anywhere in the content-type, items with that content-type will
    not be gzipped.  "jp" will exclude "image/jpg" and "image/jpeg".
    "application" will exclude any content-type with the word "application" in
    it.

    - *tempfile* is the file size above which gzipper will send the gzipped data to
    a tempfile on disk. This may help memory usage. It may not.  *tempfile=0*
    means do not use temporary file.  Default is 1 megabyte (1048576).
