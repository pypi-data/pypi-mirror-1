"""minimalist html-in-python facility used by the docaster application

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from contextlib import contextmanager

newline = u'<br/>'
newspace = u'&#160;'

def tuplify(thing):
    if isinstance(thing, (list, tuple)):
        return thing
    return (thing,)

def build_attrs(attr_dict):
    return ' '.join('%s="%s"' % (k.lower().replace('__', ':'), v)
                    for k,v in attr_dict.iteritems())

def h(level, text, **kwattrs):
    return u'<h%(level)s %(attrs)s>%(text)s</h%(level)s>\n' \
        % {'text':text, 'level': level,
           'attrs' : build_attrs(kwattrs)}


## make pylint happy, avoid exec, make them all context managers

TEXT_ELT_TMPL = """
def %(tag)s(text, **kwattrs):
    return u'<%(tag)s %%(attrs)s>%%(text)s</%(tag)s>' \
        %% {'text': text or '', 'attrs' : build_attrs(kwattrs)}
"""

for tag in ('p', 'span', 'label', 'li', 'td', 'option', 'th', 'legend', 'pre'):
    exec(TEXT_ELT_TMPL % {'tag' : tag})

def link(url, text, **kwattrs):
    return u'<a href="%(url)s" %(attrs)s>%(text)s</a>' \
        % {'url': url, 'text': text, 'attrs': build_attrs(kwattrs)}

def img(src, **kwattrs):
    return u'<img src="%(src)s" %(attrs)s></img>\n' \
        % {'src': src, 'attrs': build_attrs(kwattrs)}

@contextmanager
def table(w, headers=None, **kwattrs):
    w(u'<table %s>' % build_attrs(kwattrs))
    if headers:
        w(u'<tr>')
        for header in tuplify(headers):
             w(th(header))
        w(u'</tr>')
    yield
    w(u'</table>')

def row(columns, **kwattrs):
    out = []
    out.append(u'<tr %s>' % build_attrs(kwattrs))
    for column in tuplify(columns):
        if '<td' in column:
            out.append(column)
        else:
            out.append(td(column))
    out.append(u'</tr>')
    return '\n'.join(out)


CM_ELT_TMPL = """
@contextmanager
def %(fname)s(w, **kwattrs):
    w(u'<%(tag)s %%s>' %% build_attrs(kwattrs))
    yield
    w(u'</%(tag)s>')
"""

for tag in ('div', 'ul', 'form', 'fieldset', 'select'):
    exec(CM_ELT_TMPL % {'tag' : tag, 'fname' : tag})
for tag, fname in (('tr', 'row_ctx'), ('td', 'col_ctx'), ('li', 'li_ctx')):
    exec(CM_ELT_TMPL % {'tag' : tag, 'fname' : fname})

def input(**kwattrs):
    return u'<input %s/>\n' % build_attrs(kwattrs)

def textarea(**kwattrs):
    return u'<textarea %s></textarea>\n' % build_attrs(kwattrs)

