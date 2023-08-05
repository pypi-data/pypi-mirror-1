import sys

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__doc__')
WRAPPER_UPDATES = ('__dict__',)

# Like Python 2.5's functools.wraps()
def wrap(wrapped, wrapper, replace=WRAPPER_ASSIGNMENTS):
    for attr in WRAPPER_ASSIGNMENTS:
        setattr(wrapper, attr, getattr(wrapped, attr))
    for attr in WRAPPER_UPDATES:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    return wrapper


def test_with(**kwargs):
    """Turn a context manager into unittest's setUp and tearDown functions.
    
    It should be used like
    
    class Test(TestCase):
        setUp, tearDown = context_tools.test_with(foo_bar=my_context_manager,
                                                  bin_baz=my_other_manager)
        
        def test(self):
            frobinate(self.foo_bar)
            franzibald(self.bin_baz)
            self.assertEqual(frobnication_count, 1)
            self.assertEqual(franzibald_num, 123)
            
    setUp() will call the context manager's __enter__() method, and tearDown()
    will call the manager's __exit__() method.
    
    Args:
        A single keyword argument. The name can be anything you like.
    
    Returns:
        (set_up, tear_down), where set_up is should be assigned to the
        test case's setUp method and tear_down to the tearDown method.
    """
    kwargs = dict(kwargs)
    def set_up(test):
        for var, mgr in list(kwargs.items()):
            setattr(test, var, mgr.__enter__())
    def tear_down(test):
        for mgr in list(kwargs.values()):
            mgr.__exit__(None, None, None)
    return (set_up, tear_down)


def decorate_with(mgr):
    """Turn a context manager into a decorator.
    
    @context_tools.decorate_with(manager)
    def foo(x, y):
        ...
        
    is the same as
    
    def foo(y):
        with manager as x:
            ...
    
    Args:
        mgr: A context manager.
    
    Returns:
        A decorator.
    """
    def decorator(func):
        def replacement(*args, **kwargs):
            # Implement this manually to support Python 2.4
            value = mgr.__enter__()
            exc = True
            try:
                try:
                    return func(value, *args, **kwargs)
                except:
                    exc = False
                    if not mgr.__exit__(*sys.exc_info()):
                        raise
            finally:
              if exc:
                  mgr.__exit__(None, None, None)
        return wrap(func, replacement)
    return decorator


def yield_with(mgr):
    """Turn a context manager into a decorator suitable for use on generators.
    
    The context manager's __exit__() method will only be called when an
    exception is raised, either StopIteration or some other exception.
    
    Args:
        mgr: A context manager.
    
    Returns:
        A decorator.
    """
    def decorator(func):
        class DecoratedGenerator(object):
            def __init__(self, *args, **kwargs):
                self.mgr = mgr
                self.gen = func(mgr.__enter__(), *args, **kwargs)
                self.stopped = False

            def __next__(self):
                if self.stopped:
                    raise StopIteration
                try:
                    return next(self.gen)
                except StopIteration:
                    self.stopped = True
                    self.mgr.__exit__(None, None, None)
                    raise
                except:
                    if not self.mgr.__exit__(*sys.exc_info()):
                        raise

            def __iter__(self):
                return self

            def __getattr__(self, attr):
                return getattr(self.gen, attr)
        for k, v in list(func.__dict__.items()):
            if not hasattr(DecoratedGenerator, k):
                setattr(DecoratedGenerator, k, v)
        return DecoratedGenerator
    return decorator
