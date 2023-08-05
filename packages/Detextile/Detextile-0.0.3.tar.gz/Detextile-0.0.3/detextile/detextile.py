"""Convert HTML to Textile syntax using BeautifulSoup."""

__author__ = 'Roberto De Almeida <roberto@dealmeida.net>'

from BeautifulSoup import BeautifulSoup


def _body(el):
    """Process body tag."""
    for i in el.contents:
        for j in walk_tree(i): yield j


def _block(sig): 
    """Process block tag."""
    def block(el):
        # Get attributes as dict.
        attrs = {}
        for k,v in el.attrs: attrs[k] = v 

        # Block signature.
        yield sig

        # Store attributes.
        attrs_ = []
        if 'class' in attrs: attrs_.append('%s' % (attrs['class']))
        if 'id' in attrs: attrs_.append('#%s' % attrs['id'])
        if attrs_:
            yield '(%s)' % ''.join(attrs_)

        # We can safely always output extended blocks, because we always
        # use the p. signature for unamed blocks. 
        yield '.. '

        for i in el.contents:
            for j in walk_tree(i):
                yield j
        yield '\n\n'

    return block


def _qtag(tag):
    """Process quick tag."""
    def qtag(el):
        yield tag
        for i in el.contents:
            for j in walk_tree(i): yield j
        yield tag

    return qtag

def _image(el):
    """Process image tag."""
    # Get attributes as dict.
    attrs = {}
    for k,v in el.attrs: attrs[k] = v 

    yield '!'
    yield attrs['src'] 
    if 'alt' in attrs: yield '(%s)' % attrs['alt']
    yield '!'


def _anchor(el):
    """Process anchor tag."""
    # Get attributes as dict.
    attrs = {}
    for k,v in el.attrs: attrs[k] = v 

    # Check for image inside anchor.
    if getattr(el.contents[0], 'name', None) == 'img':
        for i in el.contents:
            for j in walk_tree(i): yield j
    else:
        yield '"'
        for i in el.contents:
            for j in walk_tree(i): yield j
        yield '"'
    if 'href' in attrs: yield ':%s ' % attrs['href']
    

def _html(el):
    """Return unrecognized tags as is."""
    yield '%s\n\n' % el

    
def walk_tree(el):
    tags = {'p'         : _block('p'),
            'blockquote': _block('bq'),
            'pre'       : _block('pre'),
            'strong'    : _qtag('*'),
            'em'        : _qtag('_'),
            'b'         : _qtag('**'),
            'i'         : _qtag('__'),
            'big'       : _qtag('++'),
            'small'     : _qtag('--'),
            'del'       : _qtag('-'),
            'ins'       : _qtag('+'),
            'sup'       : _qtag('^'),
            'sub'       : _qtag('~'),
            'span'      : _qtag('%'),
            'code'      : _qtag('@'),
            'body'      : _body,
            'img'       : _image,
            'a'         : _anchor,
           }

    if getattr(el, 'name', None):
        # Tag.
        f = tags.get(el.name, _html)
        for i in f(el): yield i
            
        # Blocks must always be followed by another block, so if we
        # add the default block signature if it's not the case.
        if f.__name__ == 'block':
            next = el.nextSibling
            # Look for the first named sibling.
            while not getattr(next, 'name', None) and next:
                next = next.nextSibling
                f = tags.get(next.name, None)
                if f and f.__name__ != 'block': yield 'p. '
    else:
        # String.
        yield el


def detextile(input):
    """Convert HTML input to Textile syntax."""
    soup = BeautifulSoup(input)

    # Check for body in soup.
    body = soup('body')
    if body:
        soup = body[0]

    return walk_tree(soup)


if __name__ == '__main__':
    input = """<html>
    <head><title>Page title</title></head>
    <body>
    <blockquote><div>Test</div></blockquote>
    <p id="firstpara" align="center" class="class1 class2">This is paragraph <b>one</b>.
    <p id="secondpara" align="blah">This is paragraph <b>two</b>.

    <blockquote>Test</blockquote>

    <pre>
    Some code

    Some more code
    </pre>

    <img src="http://example.com/image.gif" alt="alternative description" />

    <a href="http://example.com">Example.com</a>

    <a href="http://example.com"><img src="image.jpg"></a>
    </html>""" 


    textile_ = ''.join(detextile(input))
    print textile_
    import textile
    print textile.textile(textile_)
