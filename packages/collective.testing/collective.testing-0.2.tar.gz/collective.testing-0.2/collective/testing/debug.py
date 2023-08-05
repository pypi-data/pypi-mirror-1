import pdb

class Bag(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
    update = __init__
    def __repr__(self):
        return "%s" %self.__dict__

_test = False
def dfunc(*args, **kwargs):
    """
    convenience decorator for applying pdb and postmortem

    Test reference integrity(assume use of only)

    >>> func = dfunc(test_func)
    >>> func()
    (<function <lambda> at ...>, True, False)

    >>> func = dfunc(trace=True, pm=True)(test_func)
    >>> func()
    (<function <lambda> at ...>, True, True)
    """
    f = None
    if args and callable(args[0]):
        f = args[0]
    opts = Bag(trace=True, pm=False, func=f, test=_test)
    opts.update(**kwargs)

    def wrap(*args, **kwargs):
        try:
            if opts.trace:
                pdb.set_trace()
            return opts.func(*args, **kwargs)
        except Exception, e:
            if not opts.pm:
                raise e
            else:
                import sys
                pdb.post_mortem(sys.exc_info()[2])
            
    def mkfunc(func):
        opts.func = func
        return wrap

    if opts.test:
        def wraptest(*args, **kwargs):
            return opts.func, opts.trace, opts.pm,
        wrap = wraptest
    
    if opts.func:
        return wrap
    else:
        return mkfunc


def autopsy(func):
    def razor(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except :
            import sys
            pdb.post_mortem(sys.exc_info()[2])
    return razor

        
