version = "0.2.1.1"
author = "Fred Lin"
email = "gasolin@gmail.com"
copyright = "Copyright 2007 Fred Lin and contributors"
license = "MIT <http://www.opensource.org/licenses/mit-license.php>"
description="Doc generator with styles, and syntax highlighting blocks"
long_description = """mopowg is an easy to install, cross-platform doc generator which is based on docutils.

mopowg could generate full documents with figures, styles, and syntax highlighting blocks.

It includes a command line tool and will provide the web front-end.

Install mopowg
--------------

You could use easy_install command to install mopowg::


    $ easy_install mopowg

or you could install mopowg from sourse

First download the source::

    $ hg clone http://hg.python.org.tw/mopowg

then::

    $ python setup.py install

Usage
-----

Run as a command
----------------

::

  $ mopowg -i docs

Run as a single file
--------------------

You could embeded mopowg into your project with a single file.

put mopowg.py to a document folder. run mopowg.py::


    $ python mopowg.py -i docs
    
Run as a module
---------------

You could import mopowg module in your program::

    import os
    from mopowg import mopowg

    path = os.path.join(os.getcwd(), 'docs')
    ld = mopowg.scanner(path)
    mopowg.generator(input=ld)

ChangeLog
----------

  * Add license information (MIT)
  * Add '--preview' option
  * customable wiki pattern for convertor
  * customable file extension for saver
  * Web front end example: Turbogears 2 toolbox plugin: wikidoki http://trac.turbogears.org/browser/projects/ToolBox2/trunk/toolbox/controllers/wikidoki.py
  * wikipattern cause command not work fixed

"""
