"""
mopowg
======

mopowg is an easy to install, cross-platform doc generator which is based on docutils.

mopowg could generate full documents with figures, styles, and syntax highlighting blocks.

fredlin 2007, gasolin+mopowg@gmail.com

    - Scanner
    - Generator
        - Convertor
            - Formater
                - high_lighter
        - Processor
            - Templater (genshi)
            - Saver
                - css_writer

----

doc processing
--------------

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

----

doc hosting[1]
--------------

Runner is the build in server which host the documents;

Plugins:

Interpreter is the crunchy interpreter that allow you to execute the demo codes on doc;

Commenter is append fields for comment

Diagram::

    ___________
    |         |
    |  files  |
    |         |
    |_________|
         |
  ----------------
  |doc processing|
  ----------------
         |
       Runner - plugins
                   |
                   |- Interpreter
                   |
                   |_ Commenter

----

doc collaborative [1]
---------------------

Diagram::

    ___________
    |         |
    |  files  |--hg repository
    |         |
    |_________|
         |
  ----------------
  |doc processing|
  ----------------
         |         
  ----------------
  | doc hosting  |
  ----------------
         |
       wikier

----

[1]: not implemented yet

"""
import os
    
def proc_dir(file_list, dirName, files):
    """
    The callback function of os.path.walk() to get the list of scanned
    files.
    """
    for i in files:
        fn = os.path.join(dirName, i)
        if os.path.isdir(fn):
            continue
        elif os.path.isfile(fn):
            file_list.append(fn)

def scanner(path=None):
    """scan a folder
    
    scanner is a preprocess class to collect files
    
    scanner currently allow single layer only
    """
    if path:
        if os.path.isdir(path):
            #search dir recursively
            #os.listdir(path)
            pass
        else:
            path = os.path.join(os.getcwd,path)
    else:
        path = os.getcwd()
    
    file_list = []
    os.path.walk(path, proc_dir, file_list)
    return file_list

# default css style
default_style="""body {
    margin: 0;
    padding: 0;
    font-family: Verdana, "Lucida Grande", sans-serif;
    text-align: left; 
    /*text-align: center;*/
    line-height: 1.3em;
    color: #333;
    background: #fff;
    padding: 20px 20px 0 20px;
}
.literal-block { background: #fff0f0; border: solid 1px #ccc;
padding:2px 2px 2px 10px; margin: 5px 5px 5px 5px; line-height:1.2em; }  /* Block */
.note { background: #f0ff00; border: solid 1px #ccc;
padding:2px 2px 2px 10px; margin: 5px 5px 5px 5px; line-height:1.2em; }  /* Notes */
.highlight  { background: #f0f0f0; border: solid 1px #ccc;
padding:2px 2px 2px 10px; margin: 5px 5px 5px 5px; line-height:1.2em; }
.highlight .c { color: #60a0b0; font-style: italic } /* Comment */
.highlight .err { border: 1px solid #FF0000 } /* Error */
.highlight .k { color: #007020; font-weight: bold } /* Keyword */
.highlight .o { color: #666666 } /* Operator */
.highlight .cm { color: #60a0b0; font-style: italic } /* Comment.Multiline */
.highlight .cp { color: #007020 } /* Comment.Preproc */
.highlight .c1 { color: #60a0b0; font-style: italic } /* Comment.Single */
.highlight .cs { color: #60a0b0; background-color: #fff0f0 } /* Comment.Special */
.highlight .gd { color: #A00000 } /* Generic.Deleted */
.highlight .ge { font-style: italic } /* Generic.Emph */
.highlight .gr { color: #FF0000 } /* Generic.Error */
.highlight .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.highlight .gi { color: #00A000 } /* Generic.Inserted */
.highlight .go { color: #808080 } /* Generic.Output */
.highlight .gp { color: #c65d09; font-weight: bold } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.highlight .gt { color: #0040D0 } /* Generic.Traceback */
.highlight .kc { color: #007020; font-weight: bold } /* Keyword.Constant */
.highlight .kd { color: #007020; font-weight: bold } /* Keyword.Declaration */
.highlight .kp { color: #007020 } /* Keyword.Pseudo */
.highlight .kr { color: #007020; font-weight: bold } /* Keyword.Reserved */
.highlight .kt { color: #007020; font-weight: bold } /* Keyword.Type */
.highlight .m { color: #40a070 } /* Literal.Number */
.highlight .s { color: #4070a0 } /* Literal.String */
.highlight .na { color: #4070a0 } /* Name.Attribute */
.highlight .nb { color: #007020 } /* Name.Builtin */
.highlight .nc { color: #0e84b5; font-weight: bold } /* Name.Class */
.highlight .no { color: #60add5 } /* Name.Constant */
.highlight .nd { color: #555555; font-weight: bold } /* Name.Decorator */
.highlight .ni { color: #d55537; font-weight: bold } /* Name.Entity */
.highlight .ne { color: #007020 } /* Name.Exception */
.highlight .nf { color: #06287e } /* Name.Function */
.highlight .nl { color: #002070; font-weight: bold } /* Name.Label */
.highlight .nn { color: #0e84b5; font-weight: bold } /* Name.Namespace */
.highlight .nt { color: #062873; font-weight: bold } /* Name.Tag */
.highlight .nv { color: #bb60d5 } /* Name.Variable */
.highlight .ow { color: #007020; font-weight: bold } /* Operator.Word */
.highlight .mf { color: #40a070 } /* Literal.Number.Float */
.highlight .mh { color: #40a070 } /* Literal.Number.Hex */
.highlight .mi { color: #40a070 } /* Literal.Number.Integer */
.highlight .mo { color: #40a070 } /* Literal.Number.Oct */
.highlight .sb { color: #4070a0 } /* Literal.String.Backtick */
.highlight .sc { color: #4070a0 } /* Literal.String.Char */
.highlight .sd { color: #4070a0; font-style: italic } /* Literal.String.Doc */
.highlight .s2 { color: #4070a0 } /* Literal.String.Double */
.highlight .se { color: #4070a0; font-weight: bold } /* Literal.String.Escape */
.highlight .sh { color: #4070a0 } /* Literal.String.Heredoc */
.highlight .si { color: #70a0d0; font-style: italic } /* Literal.String.Interpol */
.highlight .sx { color: #c65d09 } /* Literal.String.Other */
.highlight .sr { color: #235388 } /* Literal.String.Regex */
.highlight .s1 { color: #4070a0 } /* Literal.String.Single */
.highlight .ss { color: #517918 } /* Literal.String.Symbol */
.highlight .bp { color: #007020 } /* Name.Builtin.Pseudo */
.highlight .vc { color: #bb60d5 } /* Name.Variable.Class */
.highlight .vg { color: #bb60d5 } /* Name.Variable.Global */
.highlight .vi { color: #bb60d5 } /* Name.Variable.Instance */
.highlight .il { color: #40a070 } /* Literal.Number.Integer.Long */
"""

def css_writer(output, style):
    """write css"""
    outpath = os.path.join(output,'style.css')
    if not os.path.exists(outpath):
        print 'saved to %s'%outpath
        fd = file(outpath, 'w')
        fd.write(style)
        fd.close()

def saver(path, content, output, style):
    """save content to file
    
    output: dir

    saver is the processor which is used to store contents to actual files;
    """
    filename = os.path.splitext(os.path.split(path)[1])[0]+'.html'
    
    if not output:
        output = os.path.split(path)[0]

    if not os.path.exists(output):
        os.mkdir(output)

    sav = os.path.join(output, filename)
    print "saved to %s"%sav
    fd = file(sav, 'w')
    fd.write(content)
    fd.close()
    
    if (os.path.exists(os.path.join(path,style)) or os.path.exists(style)):
        fd = file(style, 'r')
        style = fd.read()
        fd.close()
    
    css_writer(output, style)


# default template
default_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/"
      xmlns:xi="http://www.w3.org/2001/XInclude">
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <title>Doc generated by mopowg</title>
    <link rel="stylesheet" type="text/css" media="screen" href="style.css" />
</head>
<body>
<div id="content" py:content="Markup(content)">
hello world
</div>
</body>
</html>
"""

def templater(input, content, template):
    """
    generate with genshi template
    """
    from genshi.template import MarkupTemplate
   
    if (os.path.exists(os.path.join(input,template)) or os.path.exists(template)):
        fd = file(style, 'r')
        template = fd.read()
        fd.close()
        
    tmpl = MarkupTemplate(template)
    stream = tmpl.generate(content=content)
    data = stream.render('html')
    return data

def processor(input, content, output, template, style):
    """process the content
    """
    content = templater(input, content, template)
    saver(input, content, output, style)

#====================
#Formater
from docutils import nodes
from docutils.parsers.rst import directives
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

#reg the high_lighter
high_lighter = HtmlFormatter()#linenos=True

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    """register the docutils highlight function"""
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = get_lexer_by_name('text')
    #formatter = ('linenos' in options) and lineno_fmter or normal_fmter
    formater = high_lighter
    parsed = highlight(u'\n'.join(content), lexer, formater)
    return [nodes.raw('', parsed, format='html')]
pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
directives.register_directive('code', pygments_directive)
#====================

import re
#match wiki word to url
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

def convertor(path, *arg, **kw):
    """
    Convert file to target format, include syntax highlight function

    input: path
    output: content
    
    support features:
    rich(rich content), wikiword
    """
    try:
        from docutils.core import publish_parts
        import pygments
        #from pygments.lexers import get_lexer_by_name
 
    except ImportError, e:
        print e    
    
    fd = file(path, 'r')
    data = fd.read()
    fd.close()
    
    if kw.get('rich', False):#kw['rich']
        #docutil
        content = publish_parts(data,writer_name="html")['html_body']
        if kw.get('wikiword', False):#kw['wikiword']
            #wiki links
            content = wikiwords.sub(r'<a href="%s\1.html">\1</a>' % '', content)
    else:
        content = data

    return content

def generator(input, filter = ['.rst','.txt'], output=None, 
              rich=True, wikiword=True, 
              template=default_template, style=default_style):
    """generate docs
    
    generator is used to generate docs;
    """
    for i in input:
        if os.path.isfile(i) and os.path.splitext(i)[-1] in filter:
            #print i
            content = convertor(path=i, rich=rich, wikiword=wikiword)
            processor(i, content, output, template, style)

def cmdtool():
    from optparse import OptionParser
    print "Please use --help to get more information"
    #allow command args    
    parser = OptionParser(
            usage="mopowg [input] [output]")
    parser.add_option("-i", "--input", 
            help="speficy the input folder",
            dest="input")
    parser.add_option("-o", "--output", 
            help="speficy the output folder",
            dest="output")
    parser.add_option("-r", "--rich",
            help="use rich content",
            action="store_true", dest="rich", default = True)
    parser.add_option("-w", "--wikiword",
            help="Convert WikiWord to Urls",
            action="store_true", dest="wikiword", default = True)
    parser.add_option("-t", "--template", 
            help="speficy a custom template",
            dest="template", default = default_template)
    parser.add_option("-s", "--style", 
            help="speficy a custom css style",
            dest="style", default = default_style)
    (options, args) = parser.parse_args()
    #print "options:"+str(options)
    ld = scanner(path=options.input)
    #import profile
    #profile.run("generator(ld, rich=rich, wikiword=wikiword)", 'myapp.prof')
    generator(input=ld, output=options.output, 
              rich=options.rich, wikiword=options.wikiword,
              template=options.template, style=options.style)
    #import pstats
    #p = pstats.Stats('myapp.prof')# Cumulative time sort top 25
    #p.sort_stats('cumulative').print_stats(25)
    # Also may find time top 25 useful
    #p.sort_stats('time').print_stats(25)

    
if __name__=="__main__":
    #import sys
    cmdtool()
    
