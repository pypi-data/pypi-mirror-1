from cStringIO import StringIO

def HTMLmarkup(tag, text=None, **attributes):
    """
    markups the text with the tag and
    attributes
    """

    s = StringIO()
    s.write('<%s' % tag)
    for attribute, value in attributes.items():
        s.write(' %s="%s"' % (attribute, value))

    if text:        
        s.write('>%s</%s>' % (text, tag))
    else:
        s.write('/>')
    return s.getvalue()

tags = [ 'a',
         'b', 'body', 'br',
         'center',
         'div', 'dl',
         'form',
         'head', 'html',
         'i', 'img', 'input',
         'li',
         'ol', 'option',
         'p',
         'select', 'span',
         'table', 'td', 'th', 'title', 'tr',
         'ul',
         ]

for _i in tags:
    globals()[_i] = lambda x=None, _i=_i, **y: HTMLmarkup(_i, x, **y)

### front ends to tags to make our lives easier
### these don't stomp on tags -- they're just front ends

def image(src, **attributes):
    attributes['src'] = src
    return img(**attributes)

def link(location, description=None, **attributes):
    if description is None:
        description = location
    attributes['href'] = location
    return a(description, **attributes)

def listify(items, ordered=False, item_attributes=None, **attributes):
    """return a HTML list of iterable items"""

    # type of list
    if ordered:
        func = ol
    else:
        func = ul

    if item_attributes is None:
        item_attributes = {}
    
    listitems = [ li(item, **item_attributes) for item in items ]
    return func('\n%s\n' % '\n'.join(listitems))

def tablify(rows, header=False, item_attributes=None, 
            **attributes):
    """return an HTML table from a iterable of iterable rows"""
    
    if item_attributes is None:
        item_attributes = {}

    retval = []
    if header:
        markup = th
    else:
        markup = td

    for row in rows:
        retval.append(' '.join([markup(str(item)) for item in row]))
        markup = td

    return table('\n%s\n' % '\n'.join([tr(row) for row in retval]))

def wrap(string, pagetitle=None, stylesheets=None, icon=None):
    """wrap a string in a webpage"""
    _head = ''
    if pagetitle:
        _head += title(pagetitle)
    rel = 'stylesheet'
    for i in stylsheets:
        attributes = dict(rel=rel,
                          type='text/css')        
        if hasattr(i, '__iter__'):
            # assume a 2-tuple
            attributes['href'] = i[0]
            attributes['title'] = i[1]
        else:
            attributes['href'] = i
        _head += HTMLmarkup('link', None, **attributes)
        rel = 'alternate stylesheet' # first stylesheet is default
    if icon:
        _head += HTMLmarkup('link', None, href=icon)
    if _head:
        _head = head(_head)        

    return html('\n%s\n%s\n' % ( _head, body(string) ) )
