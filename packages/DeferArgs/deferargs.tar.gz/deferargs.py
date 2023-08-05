"""
deferargs module
Provides the deferargs decorator, which lets you write functions that think
they take and return normal values, when they can actually be passed and will
return Deferreds!

This code is free to use, copy, modify, and redistribute. You can use it in
any code to do anything you want, but there is no warranty.

Usage is like: (Not a doctest)

>>> @deferargs
... def printResults(*args, **kwargs):
...     print args
...     print kwargs
...     return (args, kwargs)
... 
>>> args, kwargs = printResults(getPage("www.google.com")
>>> page = args[0] # This is actually a Deferred
>>>

Plans are to later be able to do this:

>>> @catch(AssertionError)
>>> def handle(error):
...     print error
...     sys.exit(-1)
...
>>> @deferargs
>>> def doSomething():
...     somethingThatRaisesLater()

"""

from twisted.internet import defer

def deferargs(f):
    def new_f(*args, **kwargs):
        args = list(args)
        defers = []
        for i, arg in enumerate(args):
            if isinstance(arg, defer.Deferred):
                defers.append(arg)
                @arg.addCallback
                def setResultingArg(r):
                    args[i] = r
        for k, v in kwargs.items():
            if isinstance(v, defer.Deferred):
                defers.append(v)
                @v.addCallback
                def setResultingArg(r):
                    kwargs[k] = r
        if defers:
            dl = defer.DeferredList(defers, fireOnOneErrback=True, consumeErrors=True)
            @dl.addCallback
            def callWithResults(_results):
                return f(*args, **kwargs)
            return dl
        else:
            return defer.succeed(f(*args, **kwargs))
    return new_f


if __name__ == '__main__':
    @deferargs
    def test(*args, **kwargs):
        return (args, kwargs)
    @deferargs
    def testequal(a, b):
        assert a == b
    testequal(test(1, 2, foo=3), ((1,2),{'foo':3}))
    testequal(test(1, defer.succeed(2), foo=defer.succeed(3)), ((1,2),{'foo':3}))
    
    from twisted.internet import reactor
    reactor.runUntilCurrent()

