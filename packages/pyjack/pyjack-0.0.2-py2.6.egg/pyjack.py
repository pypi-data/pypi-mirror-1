"""
:mod:`pyjack` consists of two major public functions: :func:`connect` and :func:`disconnect`.  
In short, :func:`connect` is used to attach to a function with a given ``callback``, ``filter``, ``block``, ``cls`` 
signature.  

``disconnect`` will remove the first callback with the exact same ``callback``, ``filter``, ``block``, ``cls`` signature.  

When the last callback/filter has been removed, the function is in the exact state it was in before the 
:func:`pyjack.connect` function was called.  

Also, a utility function :func:`report` is provided so you can see what pyjack callback/filters are connected to a given function. 
"""
import sys
import new
import exceptions

class PyjackError(exceptions.SystemError):
    pass

def _pyjack_fn(*args, **kwargs):    
    """
    Actual function that is returned by :func:`connect`.  It: 
    
    * First calls all the filters which are stored in the func_globals['_pyjack_filters']
    * If func_globals['_pyjack_do_block'] is ``False``, call the org function(_pyjack_fo in func_globals). 
    * Then, call all the callbacks (_pyjack_active_cbs in func_globals). 
    """
    for filter in _pyjack_filters:                                      # -> Filters. cb[1] is the 'filter' function
        args,kwargs = filter(_pyjack_fo, *args, **kwargs)               #    used to change args,kwargs.

    if _pyjack_do_block:                                                # -> Original Function. Here, we call the org function.
        output = None                                                   #    If it's 'blocked' set the output to none, otherwise
    else:     
        output = _pyjack_fo(*args, **kwargs)                            #    the output is the output from the org function. 
                                
    kwargs['pyjack_org_fn'] = {'fo': _pyjack_fo }

    for cb in _pyjack_active_cbs:                                       # -> Callbacks. Then, we call the callbacks in order
        kwargs['pyjack_org_fn']['output'] = output                      #    with the org function 'tagged on'.
        coutput = cb(*args, **kwargs)                               
        if _pyjack_do_block:
            output = coutput
        elif coutput:
            output = coutput[1:]

    return output                                                        # -> Return. And don't forget to return the output. 

def _update_fn(fn):
    fn.func_globals['_pyjack_filters']    = [cb[1] for cb in fn.func_globals['_pyjack_cbs'] if cb[1]]
    fn.func_globals['_pyjack_do_block']   = len([True for cb in fn.func_globals['_pyjack_cbs'] if cb[2]]) > 0
    fn.func_globals['_pyjack_active_cbs'] = [cb[0] for cb in fn.func_globals['_pyjack_cbs'] if cb[0]]
        
def connect(fn, callback = None, filter = None, block = False, cls = None):
    
    """
    :summary:         Connects a callback and/or filter to a function/method.
    :param fn:        The function to connect to (e.g. a builtin like :func:`max` or some instance method).
    :param callback:  A callback function that will be called *after* the ``fn`` function is called.
                      Note, this callback function will be passed the ``pyjack_org_fn`` argument and 
                      must either accept this named argument (or simply accept **kwargs). 
    :param filter:    A filter function that is called *before* the ``fn`` function is called.  This function
                      must return an args,kwargs tuple that will be the args,kwargs passed to the original ``fn``. 
                      This way, you either pass the args,kwargs to the ``fn`` untouched or you can first 'filter' 
                      the arguments passed to ``fn``. 
                      Note, this filter function will be passed the ``pyjack_org_fn`` argument and 
                      must either accept this named argument (or simply accept **kwargs). 
    :param block:     If ``True``, this will block the return value of ``fn`` from being returned.  Instead, the 
                      return value of ``callback`` will be used. 
    :param cls:       This is used when you need to connect to a method-wrapper instance like :meth:`object.__init__`
                      or :meth:`object.__setattr__`.
    :returns:         The original "un-pyjacked" function (if you need a pointer to the org without callbacks/filters attached function). 


    Basic usage would be: 
    
    >>> import pyjack
    >>> 
    >>> def spy(*args, **kwargs):
    ...     print 'I spy args', args, 'and kwargs', kwargs, '...'
    >>>
    >>> pyjack.connect(fn = max, callback = spy)
    <function max at 0x...>
    >>> max([10, 20])
    I spy args ([10, 20],) and kwargs {'pyjack_org_fn': {'output': 20, 'fo': <built-in function max>}} ...
    20
    >>> pyjack.disconnect(fn = max, callback = spy) # Put it back the way it was ...

    Please see `Some Quick Examples`_ and `More Examples`_ for more complete usage cases. 

    """
    
    if cls:
        method_name = getattr(fn, '__name__', fn)
        fn = getattr(cls, method_name, None)
        if fn is None:
            raise PyjackError, "Object " + str(cls) + " does not have method " + str(method_name) + "."
        if not isinstance(fn, new.instancemethod):
            fn = new.instancemethod(fn, None, cls)        
    callback = (callback, filter, block,)
    im_class = getattr(fn, 'im_class', None)
    if im_class: # This is for bound and unbound methods. 
        im_self = fn.im_self            
        root    = im_self or im_class
        name    = fn.__name__
        fd      = root.__dict__.get(name, None)
        if getattr(fd, '_pyjack_type', None):
            fd.func_globals['_pyjack_cbs'].append(callback)
            _update_fn(fd)
        else:
            fx = new.function(_pyjack_fn.func_code, {'_pyjack_cbs': [callback], '_pyjack_fo': new.instancemethod(fn.im_func, None, im_class) }, name)
            fx._pyjack_type = 'instancemethod'
            fx._pyjack_org  = (root, name, fd)
            _update_fn(fx)
            fn              = new.instancemethod(fx, im_self, im_class)
            setattr(root, name, fn)
    elif isinstance(fn, new.function): # This is for standard functions. 
        if getattr(fn, '_pyjack_type', None):
            fn.func_globals['_pyjack_cbs'].append(callback)
            _update_fn(fn)
        else:
            fo              = new.function(fn.func_code, fn.func_globals, fn.func_name, fn.func_defaults, fn.func_closure)
            fn.func_code    = _pyjack_fn.func_code
            fn._pyjack_type = 'function'
            fn.func_globals.update( {'_pyjack_cbs': [callback], '_pyjack_fo': fo} )
            _update_fn(fn)
    elif fn.__name__ == 'time':
        pass
    elif fn.__name__ in __builtins__ and fn is __builtins__[fn.__name__]:
        name = fn.__name__
        gbs = _pyjack_fn.func_globals.copy()
        gbs.update({'_pyjack_cbs': [callback], '_pyjack_fo': fn})
        fn = new.function(_pyjack_fn.func_code, gbs, fn.__name__, _pyjack_fn.func_defaults, _pyjack_fn.func_closure,)
        fn._pyjack_type = 'builtin'
        _update_fn(fn)
        __builtins__[fn.__name__] = fn
    else:
        raise PyjackError, "Function " + str(fn) + " not supported.  For slot wrapper functions, set the 'cls' variable."
    return fn

def disconnect(fn, callback = None, filter = None, block = False, cls = None):
    
    """
    :summary:         Disconnects a callback and/or filter to a function/method.
    :parameters:      Parameters are the exact same as in the :func:`connect` call.  Parameters
                      must be **identical** for the callback/filter to be removed.
    :returns:         ``None``. 

    .. note:: 
       When using :func:`disconnect` the parameter signature must be **exactly** the same as the :func:`connect` signature
       or the callback/filter will not be removed
       
    An example:
    
    >>> import pyjack
    >>>
    >>> def spy(*args, **kwargs):
    ...     print 'spy', args, kwargs
    ...
    >>> def filter(pyjack_fo, *args, **kwargs):
    ...     print 'filter', pyjack_fo, args, kwargs
    ...     return args,kwargs               # NOTE, FILTERS MUST RETURN ARGS,KWARGS TUPLE
    ...

    >>> 
    >>> pyjack.connect(fn = sorted, callback = spy, filter = filter, block = False)
    <function sorted at 0x...>

    >>> sorted([20, 30, 10])
    filter <built-in function sorted> ([20, 30, 10],) {}
    spy ([20, 30, 10],) {'pyjack_org_fn': {'output': [10, 20, 30], 'fo': <built-in function sorted>}}
    [10, 20, 30]

    >>> pyjack.report(fn = sorted)
    [(<function spy at 0x...>, <function filter at 0x...>, False)]
    >>>
    >>> # Now, we try and disconnect -- but it causes an error because we didn't use exact signature ...
    >>> pyjack.disconnect(fn = sorted, callback = spy, filter = None, block = False)
    Traceback (most recent call last):
        ...
        ...
    PyjackError: callback <function spy at 0x...> is not a registered callback for function <function sorted at 0x...>.
    >>>
    >>> # Now, use exact signature ...
    >>> pyjack.disconnect(fn = sorted, callback = spy, filter = filter, block = False)
    >>> sorted([20, 30, 10])
    [10, 20, 30]
    >>> pyjack.report(fn = sorted)
    []
    """
    
    if getattr(fn, '_pyjack_type', None) is None:
        raise PyjackError, "fn " + str(fn) + " is not a pyjackped function."
    else:
        cb  = (callback,filter,block,) 
        cbs = fn.func_globals['_pyjack_cbs']
        try:
            cbs.remove(cb)
            if len(cbs) == 0:
                if fn._pyjack_type == 'function':
                    fn.func_code = fn.func_globals['_pyjack_fo'].func_code
                    del fn._pyjack_type
                    for key in fn.func_globals.keys():
                        if key.startswith('_pyjack_'):
                            del fn.func_globals[key]          
                elif fn._pyjack_type is 'instancemethod':
                    org = fn._pyjack_org
                    if org[2] is None:
                        delattr(org[0], org[1])
                    else:
                        setattr(org[0], org[1], org[2])
                elif fn._pyjack_type == 'builtin':
                    __builtins__[fn.__name__] = fn.func_globals['_pyjack_fo']
                else:
                    raise PyjackError, "Type " + str(fn._pyjack_type) + " is not supported ..."
        except ValueError:
            raise PyjackError, "callback " + str(callback) + " is not a registered callback for function " + str(fn) + "."

def report(fn):
    """    
    :summary:   Allows you to see callbacks/filters attached to function/method ``fn``. 
    :param fn:  The function/method you want a pyjack report upon. 
    :returns:   A list of callback/filter tuples that are connected to ``fn``.
                These tuples are in the form (callback function, filter function, block,).
                Note, returns an empty list if nothing is connected. 

    >>> import pyjack
    >>>
    >>> def spy0(*args, **kwargs):
    ...     print 'spy0', args, kwargs
    ...
    >>> def spy1(*args, **kwargs):
    ...     print 'spy1', args, kwargs
    ...
    >>> def filter1(*args, **kwargs):
    ...     print 'filter1', args, kwargs
    ...     return args,kwargs               # NOTE, FILTERS MUST RETURN ARGS,KWARGS TUPLE
    ...
    >>>
    >>> # Let's try one callback ...
    >>> pyjack.connect(fn = max, callback = spy0, filter = None, block = False)
    <function max at 0x...>
    >>> max([10, 20, 30])
    spy0 ([10, 20, 30],) {'pyjack_org_fn': {'output': 30, 'fo': <built-in function max>}}
    30
    >>> pyjack.report(fn = max)
    [(<function spy0 at 0x...>, None, False)]
    
    >>> # Now, add a another callback with filter ..    
    >>> pyjack.connect(fn = max, callback = spy1, filter = filter1, block = False)
    <function max at 0x...>
    >>> max([10, 20, 30])
    filter1 (<built-in function max>, [10, 20, 30]) {}
    spy0 (<built-in function max>, [10, 20, 30]) {'pyjack_org_fn': {'output': [10, 20, 30], 'fo': <built-in function max>}}
    spy1 (<built-in function max>, [10, 20, 30]) {'pyjack_org_fn': {'output': [10, 20, 30], 'fo': <built-in function max>}}
    [10, 20, 30]
    >>> pyjack.report(fn = max)
    [(<function spy0 at 0x...>, None, False), (<function spy1 at 0x...>, <function filter1 at 0x...>, False)]

    >>> # Now remove one ...
    >>> pyjack.disconnect(fn = max, callback = spy0, filter = None, block = False)
    >>> pyjack.report(fn = max)
    [(<function spy1 at 0x...>, <function filter1 at 0x...>, False)]

    >>> # Now remove another ...
    >>> pyjack.disconnect(fn = max, callback = spy1, filter = filter1, block = False)
    >>> pyjack.report(fn = max)
    []
    """
    func_globals = getattr(fn, 'func_globals', None)
    if func_globals is not None:
        return fn.func_globals['_pyjack_cbs']
    else:
        return []
