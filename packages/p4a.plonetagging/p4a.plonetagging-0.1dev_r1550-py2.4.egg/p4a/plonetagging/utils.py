

def escape(v):
    """Take the string, list, tuple, or set and return one unicode string
    that connects all of the values by spaces with values that already
    contained spaces in double quotes.

      >>> escape([u'abc', u'def'])
      u'abc def'

      >>> escape([u'test with spaces', u'foo'])
      u'"test with spaces" foo'

      >>> escape(u'foo bar')
      u'"foo bar"'

      >>> escape('nonascii_k\xc3\xb6ln')
      u'nonascii_k\\xf6ln'

    """

    if not isinstance(v, (tuple, list, set)):
        v = [v]

    result = []
    for x in v:
        if not isinstance(x, unicode):
            x = str(x).decode('utf-8')

        if x.find(u' ') > -1:
            x = u'"%s"' % x
        result.append(x)

    return u' '.join(result)

def unescape(v):
    """Take the unicode string and return a list containing the broken
    up values from the unicode string (separated by spaces).

      >>> unescape(u'foo bar')
      [u'foo', u'bar']

      >>> unescape(u'foo "testing spaces" bar')
      [u'foo', u'testing spaces', u'bar']

      >>> unescape(u'"testing spaces" bar')
      [u'testing spaces', u'bar']

    """

    result = []
    last = u''
    inquote = False
    for x in v:
        if x == u'"':
            if not inquote:
                inquote = True
            elif inquote:
                inquote = False
        elif x == u' ' and not inquote:
            last = last.strip()
            if last:
                result.append(last)
            last = u''
        else:
            last += x

    last = last.strip()
    if last:
        result.append(last)

    return result
