"""
Kind of like htmlgen, only much simpler.  The only important symbol
that is exported is ``html``.

This builds ElementTree nodes, but with some extra useful methods.
(Open issue: should it use ``ElementTree`` more, and the raw
``Element`` stuff less?)

You create tags with attribute access.  I.e., the ``A`` anchor tag is
``html.a``.  The attributes of the HTML tag are done with keyword
arguments.  The contents of the tag are the non-keyword arguments
(concatenated).  You can also use the special ``c`` keyword, passing a
list, tuple, or single tag, and it will make up the contents (this is
useful because keywords have to come after all non-keyword arguments,
which is non-intuitive).  Or you can chain them, adding the keywords
with one call, then the body with a second call, like::

    >>> print html.a(href='http://yahoo.com')('<Yahoo>')
    <a href=\"http://yahoo.com\">&lt;Yahoo&gt;</a>

Note that strings will be quoted; only tags given explicitly will
remain unquoted.

If the value of an attribute is None, then no attribute
will be inserted.  So::

    >>> print html.a(href='http://www.yahoo.com', name=None,
    ...              c='Click Here')
    <a href=\"http://www.yahoo.com\">Click Here</a>

If the value is None, then the empty string is used.  Otherwise str()
is called on the value.

``html`` can also be called, and it will produce a special list from
its arguments, which adds a ``__str__`` method that does ``html.str``
(which handles quoting, flattening these lists recursively, and using
'' for ``None``).

``html.comment`` will generate an HTML comment, like
``html.comment('comment text')`` -- note that it cannot take keyword
arguments (because they wouldn't mean anything).

Examples::

    >>> print html.html(
    ...    html.head(html.title(\"Page Title\")),
    ...    html.body(
    ...    bgcolor='#000066',
    ...    text='#ffffff',
    ...    c=[html.h1('Page Title'),
    ...       html.p('Hello world!')],
    ...    ))
    <html><head><title>Page Title</title></head><body bgcolor=\"#000066\" text=\"#ffffff\"><h1>Page Title</h1><p>Hello world!</p></body></html>
    >>> print html.a(href='#top')('return to top')
    <a href=\"#top\">return to top</a>

"""

from cgi import escape
import elementtree.ElementTree as et

default_encoding = 'utf-8'

class _HTML:

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError
        attr = attr.lower()
        if attr.endswith('_'):
            attr = attr[:-1]
        if attr.find('__') != -1:
            attr = attr.replace('__', ':')
        if attr == 'comment':
            return Element(et.Comment, {})
        else:
            return Element(attr, {})
        
    def __call__(self, *args):
        return ElementList(args)

    def quote(self, arg):
        if arg is None:
            return ''
        return escape(unicode(arg).encode(default_encoding), 1)

    def str(self, arg, encoding=None):
        if isinstance(arg, str):
            return arg
        elif arg is None:
            return ''
        elif isinstance(arg, unicode):
            return arg.encode(default_encoding)
        elif isinstance(arg, (list, tuple)):
            return ''.join(map(self.str, arg))
        elif isinstance(arg, Element):
            return str(arg)
        else:
            return unicode(arg).encode(default_encoding)

html = _HTML()

class Element(et._ElementInterface):

    def __call__(self, *args, **kw):
        el = self.__class__(self.tag, self.attrib)
        if kw.has_key('c'):
            if args:
                raise ValueError(
                    "You may either provide positional arguments or a "
                    "'c' keyword argument, but not both")
            args = kw['c']
            del kw['c']
            if not isinstance(args, (list, tuple)):
                args = (args,)
        for name, value in kw.items():
            if value is None:
                del kw[name]
                continue
            kw[name] = unicode(value)
            if name.endswith('_'):
                kw[name[:-1]] = value
                del kw[name]
            if name.find('__') != -1:
                new_name = name.replace('__', ':')
                kw[new_name] = value
                del kw[name]
        el.attrib.update(kw)
        el.text = self.text
        last = None
        for item in self.getchildren():
            last = item
            el.append(item)
        for arg in flatten(args):
            if arg is None:
                continue
            if not et.iselement(arg):
                if last is None:
                    if el.text is None:
                        el.text = unicode(arg)
                    else:
                        el.text += unicode(arg)
                else:
                    if last.tail is None:
                        last.tail = unicode(arg)
                    else:
                        last.tail += unicode(arg)
            else:
                last = arg
                el.append(last)
        return el

    def __str__(self):
        return et.tostring(self, default_encoding)

    def __unicode__(self):
        # This is lame!
        return str(self).decode(default_encoding)

    def __repr__(self):
        content = str(self)
        if len(content) > 25:
            content = repr(content[:25]) + '...'
        else:
            content = repr(content)
        return '<Element %r>' % content

class ElementList(list):
    
    def __str__(self):
        return html.str(self)

    def __repr__(self):
        return 'ElementList(%s)' % list.__repr__(self)

def flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            for sub in flatten(item):
                yield sub
        else:
            yield item

__all__ = ['html']
