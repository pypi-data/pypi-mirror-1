class AsynchroneousCallback(object):
    __slots__ = "callback", "data"

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.data = args, kwargs

    def call(self, *args, **kwargs):
        cargs = self.data[0] + args
        ckwargs = dict(self.data[1])  # This copies the dict.
        ckwargs.update(kwargs)  # Notice the order of the operations.
        return self.callback(*cargs, **ckwargs)

    __call__ = call  # Convenience

if __name__ == '__main__':
    def my_callback(arg1, arg2, kwarg1="kwarg1 default", kwarg2="kwarg2 default"):
        print "arg1: " + arg1
        print "arg2: " + arg2
        print "kwarg1: " + kwarg1
        print "kwarg2: " + kwarg2
        print "*" * 40

    cb = AsynchroneousCallback(my_callback, "arg1 from callback init", kwarg1="kwarg1 callback default")
    print "*" * 40
    print "AsynchroneousCallback example"
    print "*" * 40
    cb("arg1 from callback object call")
    cb("arg1 from callback object call", kwarg2="kwarg2 from callback object call")
    cb("arg1 from callback object call", kwarg1="kwarg1 from callback object call")
