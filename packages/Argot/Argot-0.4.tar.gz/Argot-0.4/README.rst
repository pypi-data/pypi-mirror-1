argot text markup -- a markdown dialect
=======================================

Argot is a small set of extensions on the markdown_ markup language designed
primarily for writing technical blog entries.  The extensions are not 
"proper" markdown extensions;  they are implemented as preprocessors that
compile down into markdown or html syntax.  In addition to markdown's regular 
syntax, which argot does not interfere with, argot provides these features:

* `moin-style highlighted code blocks`_
* `link target processors`_

You can fork argot `from its hg repository 
<http://dev.jmoiron.net/hg/argot/>`_.

.. _markdown: http://daringfireball.net/projects/markdown/

requirements
------------

`argot` requires markdown, pygments, and lxml.  lxml can be difficult to
install from pypi, so it is not listed as an installation requirement in
setup.py.  Please fulfill this requirement through lxml's OS bundles.

moin-style highlighted code blocks
----------------------------------

In markdown, code blocks are blocks of text one level of indentation removed
from the body text.  However, when dealing with more primative browser input
mechanisms, indenting lots of text can be problematic (as ``tab`` often shifts
input focus).  In addition to allowing for this convention, `argot` implements
moin/tracwiki style code blocks that feature syntax highlighting via pygments.

syntax
~~~~~~

The general syntax is '{{{' followed by an optional shebang and desired
pygments parser, followed by your code block, and bookended with '}}}'::

    {{{#!parser
        ... code ...
    }}}

By default, if no parser is provided, `argot` uses pygments to try and guess
what language is being used.  It falls back to the plain text lexer. 

link target processors
----------------------

Markdown links are in the style of ``[link text](url)``, but this will often
interrupt writing with digging around for urls that might be complex or even
unknown.  Rather than linking to urls, `argot` allows you to encode the
target information in customizable ways.

syntax
~~~~~~

Link processors are made up of the processor tag, followed by a colon, 
followed by a query for that processor.  For example::

    [Quick reStructured Text](google: restructured text quick ref)

This calls the link processor `google` with the query `restructured text
quick ref`.  By default, only the link processor `google` is enabled.  There
is an `amazon` link processor that can be enabled, but it is suggested that
for stable queries you append 'amazon' to google queries.

writing new link processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Link processors are functions that take a single argument, the `query` as a
string, and return another string::

    def wiki_processor(query):
        return google_processor('wikipedia %s' % query)
    argot.enable_link_processor(wiki_processor)

This hypothetical wiki processor merely does a google search for 'wikipedia'
and the query provided.  The tag for the processor can be provided in 3 ways:

* the name of the function before the first underscore
* a ``tag`` attribute on the function
* an optional second argument to ``enable_link_processor``

