__test__ = {
    'test this': """
Ellisis in particular are tested here.  First, an
error:

    >>> o = object()
    >>> o # Expect a doctest error here!
    ...   # really, it's okay
    <object object at ...>

See, you got an error!  Next:

    >>> from dtopt import ELLIPSIS
    >>> o
    <object object at ...>
""",
    }

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    print 'Expect *one* error.  Zero is bad, two is bad.'
    print 'One error is good'
    
