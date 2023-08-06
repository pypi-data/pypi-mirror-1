#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Argot markup language, a set of extensions on John Gruber's markdown."""

import re
import sys
import random

from htmlentitydefs import name2codepoint as n2cp

# simplejson could potentially be all over the place
try: import json as simplejson # python 2.6
except ImportError:
    try: import simplejson
    except ImportError:
        try: from django.utils import simplejson
        except: simplejson = None

# pygments syntax highlighter
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from markdown import markdown, inlinepatterns

import lxml.html
import lxml.etree

# from argot
import utils
import uuid

enabled_extensions = set(['codeblock', 'link_processors'])

class ArgotString(str):
    pass

def safe_markdown(string, encoding='utf-8'):
    """Markdown's a string in a way that preserves the string's codeblocks."""
    cb = False
    if isinstance(string, ArgotString):
        cb = string.codeblocks
    # the only safe way to do this is to be told the encoding
    string = string.decode(encoding, 'replace')
    string = utils.decode_html_entities(string)
    #string = string.replace('&', '&amp;')
    html   = markdown(string)
    if cb:
        html = ArgotString(html)
        html.codeblocks = cb
    return html

def render(string, no_surrounding_tag=False):
    """Applies our creole to a string."""
    string = preprocess(string)
    string = safe_markdown(string)
    string = postprocess(string)
    if no_surrounding_tag:
        return utils.strip_surrounding_tag(string)
    return string

def preprocess(string):
    enabled = [e for e in pre_apply_order if e.tag in enabled_extensions]
    for ext in pre_apply_order:
        string = ext.preprocess(string)
    return string

def postprocess(string):
    enabled = [e for e in post_apply_order if e.tag in enabled_extensions]
    for ext in enabled:
        string = ext.postprocess(string)
    return string

def replace_section(string, replace, start, end):
    return string[:start] + replace + string[end:]

class LinkProcessor(object):
    """A link processor is a callable who has an attribute 'tag' or whose
    __name__ is in the format `tag`_processor.  The `tag` portion will
    then be used to find and execute the links."""
    markdown_link_re = re.compile(inlinepatterns.LINK_RE)
    link_processor_re = re.compile('(?P<name>[\w]+?):(?P<query>[^/]+)')
    tag = 'link_processor'

    def preprocess(self, string):
        string = unicode(string)
        found = True
        # iterate over all markdown links; if we find one we have to replace,
        # replace it and start over.  this is stupid but 'fast enough'
        while found:
            found = False
            for match in LinkProcessor.markdown_link_re.finditer(string):
                link_text = match.groups()[7]
                lmatch = LinkProcessor.link_processor_re.search(link_text)
                if lmatch:
                    found = True
                    name, query = map(unicode.strip, lmatch.groups())
                    url = self.run_link_processor(name, query)
                    new = '[%s](%s)' % (match.groups()[0], url)
                    string = replace_section(string, new, match.start(), match.end())
                    break
        return string

    def postprocess(self, string):
        return string

    def run_link_processor(self, name, query):
        for proc in enabled_link_processors:
            tag = LinkProcessor.get_tag(proc)
            if name == tag:
                return proc(query)

    @staticmethod
    def get_tag(function):
        tag = getattr(function, 'tag', None)
        if tag is not None:
            return tag
        else:
            return function.__name__.lower().split('_')[0]
link_processor = LinkProcessor()

class Codeblock(object):
    code_re = re.compile(r'(?P<open><code.+?>)(?P<content>.+?)(?P<close></code>)', re.MULTILINE | re.DOTALL)
    tag = 'codeblock'

    def preprocess(self, string):
        """The pygmentized codeblocks can be done in two ways, mostly for backwards
        compatibility with pre-released versions of argot.  The suggested way is via
        moin codeblocks, but as moin codeblocks themselves are compiled to markdown
        syntax, you can use the raw markdown syntax for highlighted codeblocks."""
        string = moin_codeblocks(string)
        string = Codeblock.remove_code(string)
        return string

    def postprocess(self, string):
        return Codeblock.restore_code(string)

    @staticmethod
    def remove_code(htmlstr):
        """Takes a html-ish fragment that might have <code> blocks in it and
        removes the code blocks.  It sets a new object on the string, 'codeblocks',
        that is used by 'restore_code'."""
        matches = [m.groupdict() for m in Codeblock.code_re.finditer(htmlstr)]
        if not matches:
            return htmlstr
        for match in matches:
            # generate a pretty naive randint-based replacement key; this will be
            # swapped with the content at each stage for each match
            bookend = chr(random.randint(65, 122))*3
            key = hex(random.randint(0, 0xffffffff)).upper()
            match['key'] = str(uuid.uuid4())
        # the matches are in order, left to right..
        for match in matches:
            htmlstr = htmlstr.replace(match['content'], match['key'], 1)
        htmlstr = ArgotString(htmlstr)
        htmlstr.codeblocks = matches
        return htmlstr

    @staticmethod
    def restore_code(htmlstr):
        """Takes a string processed by `remove_code` and restores the code block.
        Along with restoring the code-block, it applies pygments syntax
        highlighting to the block."""
        if not isinstance(htmlstr, ArgotString):
            return htmlstr
        html = str(htmlstr)
        for block in htmlstr.codeblocks:
            lang_tag = block['open'] + block['close']
            lang = lxml.html.fromstring(lang_tag).attrib.get('class', None)
            tag  = block['open'] + block['key'] + block['close']
            html = html.replace(tag, utils.pygmentize(block['content'], lang), 1)
        return html
codeblock = Codeblock()

# a ~3k block of text w/ 2 code blocks ran in:
#   10000 loops, best of 3: 69.5 µs per loop
codeblock_re = re.compile(r'{{{\s*(?P<decl>#!\w+)?(?P<content>.*?)}}}', re.MULTILINE|re.DOTALL)
def moin_codeblocks(string):
    """An implementation of moin-style codeblocks on top of markdown.  This
    implementation compiles them down to a special markdown/html hybrid markup
    which is then parsed and highlighted separately.

     * wiki-style codeblocks w/ pygments highlighting:
        {{{#!parser
            ... (code block) ...
        }}}

    The 'parser' is the parser to use with pygments.  This gets compiled
    down to an html codeblock with a class="parser", which is the turned
    into a highlighted code block later by the argot parser.
    """
    match = codeblock_re.search(string)
    while match:
        parser, block = match.groups()
        lang = parser if parser else None
        if lang:
            # strip off #!
            lang = lang[2:]
            newblock = '<code class="%s">%s</code>' % (lang, block)
        else:
            newblock = '<code>%s</code>' % (block)
        string = replace_section(string, newblock, match.start(), match.end())
        match = codeblock_re.search(string)
    return string

def google_processor(query):
    """Default google link processor.  Attempts to do a googleapi ajax
    search with the query and return the first result.  For this to succeed,
    you need to set the `google_referer` to your website referer, either
    at the module level of `argot.markup` or via `set_google_referer`.
    If it fails, it returns the url of an 'Feeling Lucky' search.

    google api:
        http://code.google.com/apis/ajaxsearch/documentation/
    """
    from urllib2 import Request, urlopen
    from urllib import urlencode
    q = urlencode({'q': query})
    fallback_url = 'http://www.google.com/search?%s&btnI' % q
    if simplejson is None:
        sys.stderr.write('simplejson is required for the google link processor.')
    if not google_referer:
        return fallback_url
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % q
    req = Request(url)
    req.add_header('Referer', google_referer)
    response = urlopen(req).read()
    j = simplejson.loads(response)
    results = j['responseData']['results']
    if not len(results):
        return fallback_url
    return results[0]['url']

# example firefox headers to hide our traffic in the bright glare of the sun
firefox_headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.10) Gecko/2009042523 Firefox/3.0.10',
    'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
}

# amazon's search results were too fickle to run a test suite on, If you
# want to include links to books or media, I suggest you just append 'amazon'
# to a google search of the amazon query.
def amazon_processor(query):
    """Default amazon link processor, finds links of type 'amazon' and does
    a query on Amazon to find the book link.  Slightly less nice than the
    google link processor, for now this scrapes amazon's site.  If it fails,
    it falls back on providing the url of the search."""
    from urllib2 import Request, urlopen
    from urllib import urlencode
    q = urlencode({'field-keywords': query})
    url = "http://www.amazon.com/s/ref=nb_ss_gw?url=search-alias%%3Daps&%s" % q
    req = Request(url, headers=firefox_headers)
    response = urlopen(req).read()
    html = lxml.html.fromstring(response)
    link = html.cssselect('div.productData div.productTitle a')
    if not len(link):
        return url
    return link[0].items()[0][1]

pre_apply_order = [link_processor, codeblock]
post_apply_order = [codeblock]
enabled_link_processors = set([google_processor])

google_referer = None
def set_google_referer(ref):
    """Set the referer for the google search API.  If the referer is set to
    False, the google link processor will return "I'm feeling lucky" pages."""
    global google_referer
    google_referer = ref

def enable_link_processor(func, tag=None):
    """Enable a function as a link processor.  If no tag is supplied, it is
    added without one, and the tag for that processor will be the part of its
    __name__ before the first underscore."""
    if tag: func.tag = tag
    enabled_link_processors.add(func)

def disable_link_processor(func):
    """Disable link processors.  If a function is passed, that function is
    removed from the set of enabled link processors.  If a string is passed,
    any processors whose name or tags start with that string are disabled."""
    if isinstance(func, basestring):
        rem = []
        for proc in enabled_link_processors:
            if proc.__name__.startswith(func):
                rem.append(proc)
            elif hasattr(proc, 'tag') and proc.tag.startswith(func):
                rem.append(proc)
        for r in rem:
            try: enabled_link_processors.remove(func)
            except KeyError: pass
    else:
        try: enabled_link_processors.remove(func)
        except KeyError: pass

