class AsynchroneousCallback(object):
    """Asynchroneous callbacks are objects which when called in turn call a
    function (or any callable) with a given set of arguments.

    >>> def print_addition(a, b):
    ...     print a + b
    ... 
    >>> print_addition(1, 2)
    3
    >>> cb = AsynchroneousCallback(print_addition, 5)
    >>> cb(5)
    10
    >>> cb(1)
    6
    >>> def rot13_kwargs(**d):
    ...     return dict((k.encode("rot13"), d[k]) for k in d)
    ... 
    >>> rot13_kwargs(foo="bar")
    {'sbb': 'bar'}
    >>> cb = AsynchroneousCallback(rot13_kwargs, sbb="bar")
    >>> cb()
    {'foo': 'bar'}
    >>> cb(quux="lax")
    {'foo': 'bar', 'dhhk': 'lax'}
    """

    __slots__ = "callback", "data"

    def __init__(self, callback, *args, **kwargs):
        """Set callback to "callback", and set the default arguments to any
        other arguments provided.
        """

        self.callback = callback
        self.data = args, kwargs

    def call(self, *args, **kwargs):
        """Call the callback callable with the arguments given at
        construction, with any extra arguments added. For the keyword
        arguments, any keyword arguments passed will override the ones passed
        to the constructor.
        """

        default_args, default_kwargs = self.data
        call_args = default_args + args
        call_kwargs = default_kwargs.copy()
        call_kwargs.update(kwargs)
        return self.callback(*call_args, **call_kwargs)

    __call__ = call  # Convenience

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
