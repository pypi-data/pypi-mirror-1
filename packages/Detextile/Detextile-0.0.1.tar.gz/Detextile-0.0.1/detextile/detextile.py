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

        yield '. '

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
           }

    if getattr(el, 'contents', None):
        # Tag.
        try:
            f = tags[el.name]
            for i in f(el): yield i
        except KeyError:
            # Return unrecognized tags as is.
            yield '%s\n\n' % el
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
    <blockquote>Test</blockquote>
    <p id="firstpara" align="center" class="class1 class2">This is paragraph <b>one</b>.
    <p id="secondpara" align="blah">This is paragraph <b>two</b>.

    <blockquote>Test</blockquote>

    <pre>
    Some code
    </pre>
    </html>""" 


    textile_ = ''.join(detextile(input))
    print textile_
    import textile
    print textile.textile(textile_)
