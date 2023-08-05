mopowg
==========

mopowg is an easy to install, cross-platform distributed collaborative documentation system 
which is based on docutils and mercurial.

mopowg could generate full documents with figures and code blocks.


Dependency
-----------

* python > 2.4
* docutils 0.4 (for document generation)
* mercurial 0.9.3 (for distributed version control)
* pygments 0.8 (for syntax highlighting)

Usage
------

1. put mopowg.py to the document folder. run mopowg.py and you got the docs.

2. use mopowg.py as a command line tool. for example, to generate all docs within mopowg folder, run:

.. code:: sh

    $ python mopowg/mopowg.py -i .

You could use help command to check the usage

.. code:: sh

    $ python mopowg/mopowg.py --help

The command options are::

	-i: input (None)
	
		speficy the input folder.
	
	-o: output (None)
	
		speficy the output folder.
		
	-r: rich (True|False)
	
		Use rich content.
		
	-w: wikiword (True|False)
	
		Convert WikiWord to Urls.

    -t: template (default_template)
    
    	Speficy a custom template.
    
    -s: style (css_style)
    
        Speficy a custom CSS style.
    
Architecture
--------------

Here are several elements for mopowg, each elements is independent to others.

doc processing
~~~~~~~~~~~~~~~

scanner is a preprocess class to collect files;
generator is used to generate docs, include syntax highlight function;
Processor is a factory for specific process;

Diagram::

    ___________
    |         |
    |  files  |
    |         |
   \|_________|/
    \         /
      Scanner  -> file_list
        |||
     Generator - Formater -> contents
        |||
     Processor   -> files (content, presentation)
        \|/
    ___________
    |         |
    |   docs  |
    |         |
    |_________|
