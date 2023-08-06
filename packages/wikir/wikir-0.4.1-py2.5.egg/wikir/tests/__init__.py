
__all__ = ['attr', 'match']

def attr(**kwargs):
    """Add attributes to a test function/method/class"""
    def wrap(func):
        func.__dict__.update(kwargs)
        return func
    return wrap

sep = ('='*25)
def norm_whitespace(text):
    norm_buff = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped=='':
            # normalize:
            line = stripped
        norm_buff.append(line)
    return "\n".join(norm_buff)

def match(left, right, show=False, context=''):
    def norm(s):
        if not isinstance(s, unicode):
            s = s.decode('utf-8')
        s = norm_whitespace(s)
        return s
    left = norm(left)
    right = norm(right)
    if context:
        context = norm(context)
    def dump(s, name):
        return( "\n".join([
            '=' + name + sep,
            s + '=' + name + sep]))
    if context:
        context = dump(context, 'CONTEXT') + u"\n"
    comparison = u"\n%s%s\n%s" %  (context, dump(left, 'ACTUAL'), dump(right, 'EXPECTED'))
    if show:
        print comparison.encode('utf-8')
    msg = u"\n%s\n(strings did not match)" % comparison
    assert left==right, (msg.encode('utf-8'))