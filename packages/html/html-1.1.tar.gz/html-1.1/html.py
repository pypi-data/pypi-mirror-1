# $id$
#
'''
Simple, elegant HTML generation
-------------------------------

To construct HTML start with an instance of ``html.HTML()``. Add
tags by accessing the tag's attribute on that object. For example::

   >>> from html import HTML
   >>> h = HTML()
   >>> h.br
   >>> print h
   <br>

If the tag should have text content you may pass it at tag creation time or
later using the tag's ``.text()`` method (note it is assumed that a fresh
``HTML`` instance is created for each of the following examples)::

   >>> p = h.p('hello world!\\n')
   >>> p.text('more &rarr; text', escape=False)
   >>> h.p
   >>> print h
   <p>hello, world!
   more &rarr; text</p>
   <p>

Any HTML-specific characters (``<>&"``) in the text will be escaped for HTML
safety as appropriate unless ``escape=False`` is passed. Note also that the
top-level ``HTML`` object adds newlines between tags by default.

If the tag should have sub-tags you have two options. You may either add
the sub-tags directly on the tag::

   >>> l = h.ol
   >>> l.li('item 1')
   >>> l.li.b('item 2 > 1')
   >>> print h
   <ol>
   <li>item 1</li>
   <li><b>item 2 &gt; 1</b></li>
   </ol>

Note that the default behavior with lists (and tables) is to add newlines
between sub-tags to generate a nicer output.

The alternative to the above method is to use the containter tag as a
context for adding the sub-tags. The top-level ``HTML`` object keeps track
of which tag is the current context::

   >>> with h.table(border='1'):
   ...   for i in range(2):
   ...     with h.tr:
   ...       h.td('column 1')
   ...       h.td('column 2')
   ...  print h
   <table border="1">
   <tr><td>column 1</td><td>column 2</td></tr>
   <tr><td>column 1</td><td>column 2</td></tr>
   </table>

Note the addition of an attribute to the ``<table>`` tag.

A variation on the above is to explicitly reference the context variable,
but then there's really no benefit to using a ``with`` statement. The
following is functionally identical to the first list construction::

   >>> with h.ol as l:
   ...   l.li('item 1')
   ...   l.li.b('item 2 > 1')

You may turn off/on adding newlines by passing ``newlines=False`` or
``True`` to the tag (or ``HTML`` instance) at creation time::

   >>> l = h.ol(newlines=False)
   >>> l.li('item 1')
   >>> l.li('item 2')
   >>> print h
   <ol><li>item 1</li><li>item 2</li></ol>

----

This code is copyright 2009 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
'''
__version__ = '1.1'

import unittest
import cgi

class HTML(object):
    '''Easily generate HTML.

    '''
    newline_default_on = set('table ol ul dl'.split())
        
    def __init__(self, name=None, stack=None, newlines=True):
        self.name = name
        self.content = []
        self.attrs = {}
        # insert newlines between content?
        if stack is None:
            stack = [self]
            self.top = True
            self.newlines = newlines
        else:
            self.top = False
            self.newlines = name in self.newline_default_on
        self.stack = stack
    def __getattr__(self, name):
        # adding a new tag or newline
        if name == 'newline':
            e = '\n'
        else:
            e = HTML(name, self.stack)
        if self.top:
            self.stack[-1].content.append(e)
        else:
            self.content.append(e)
        return e
    def text(self, text, escape=True):
        if escape:
            text = cgi.escape(text)
        # adding text
        if self.top:
            self.stack[-1].content.append(text)
        else:
            self.content.append(text)
    def __call__(self, *content, **kw):
        # customising a tag with content or attributes
        if content:
            self.content = map(cgi.escape, content)
        if 'newlines' in kw:
            # special-case to allow control over newlines
            self.newlines = kw.pop('newlines')
        for k in kw:
            self.attrs[k] = cgi.escape(kw[k], True)
        return self
    def __enter__(self):
        # we're now adding tags to me!
        self.stack.append(self)
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        # we're done adding tags to me!
        self.stack.pop()
    def __repr__(self):
        return '<HTML %s 0x%x>'%(self.name, id(self))
    def __str__(self):
        # turn me and my content into text
        join = '\n' if self.newlines else ''
        if self.name is None:
            return join.join(map(str, self.content))
        a = ['%s="%s"'%i for i in self.attrs.items()]
        l = [self.name] + a
        s = '<%s>%s'%(' '.join(l), join)
        if self.content:
            s += join.join(map(str, self.content))   
            s += join + '</%s>'%self.name
        return s

class TestCase(unittest.TestCase):
    def test_empty_tag(self):
        h = HTML()
        h.br
        self.assertEquals(str(h), '<br>')

    def test_para_tag(self):
        h = HTML()
        h.p('hello')
        self.assertEquals(str(h), '<p>hello</p>')

    def test_escape(self):
        h = HTML()
        h.text('<')
        self.assertEquals(str(h), '&lt;')

    def test_no_escape(self):
        h = HTML()
        h.text('<', False)
        self.assertEquals(str(h), '<')

    def test_escape_attr(self):
        h = HTML()
        h.br(a='"')
        self.assertEquals(str(h), '<br a="&quot;">')

    def test_subtag_context(self):
        h = HTML()
        with h.ol:
            h.li('foo')
            h.li('bar')
        self.assertEquals(str(h), '<ol>\n<li>foo</li>\n<li>bar</li>\n</ol>')

    def test_subtag_direct(self):
        h = HTML()
        l = h.ol
        l.li('foo')
        l.li.b('bar')
        self.assertEquals(str(h), '<ol>\n<li>foo</li>\n<li><b>bar</b></li>\n</ol>')

    def test_subtag_direct_context(self):
        h = HTML()
        with h.ol as l:
            l.li('foo')
            l.li.b('bar')
        self.assertEquals(str(h), '<ol>\n<li>foo</li>\n<li><b>bar</b></li>\n</ol>')

    def test_subtag_no_newlines(self):
        h = HTML()
        l = h.ol(newlines=False)
        l.li('foo')
        l.li('bar')
        self.assertEquals(str(h), '<ol><li>foo</li><li>bar</li></ol>')

    def test_add_text(self):
        h = HTML()
        p = h.p('hello, world!\n')
        p.text('more text')
        self.assertEquals(str(h), '<p>hello, world!\nmore text</p>')

    def test_add_text_newlines(self):
        h = HTML()
        p = h.p('hello, world!', newlines=True)
        p.text('more text')
        self.assertEquals(str(h), '<p>\nhello, world!\nmore text\n</p>')

    def test_doc_newlines(self):
        h = HTML()
        h.br
        h.br
        self.assertEquals(str(h), '<br>\n<br>')

    def test_doc_no_newlines(self):
        h = HTML(newlines=False)
        h.br
        h.br
        self.assertEquals(str(h), '<br><br>')

    def test_table(self):
        h = HTML()
        with h.table(border='1'):
            for i in range(2):
                with h.tr:
                    h.td('column 1')
                    h.td('column 2')
        self.assertEquals(str(h), '''<table border="1">
<tr><td>column 1</td><td>column 2</td></tr>
<tr><td>column 1</td><td>column 2</td></tr>
</table>''')


if __name__ == '__main__':
    unittest.main()


# Copyright (c) 2009 eKit.com Inc (http://www.ekit.com/)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# vim: set filetype=python ts=4 sw=4 et si
