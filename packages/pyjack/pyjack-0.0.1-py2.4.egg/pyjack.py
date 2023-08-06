import sys
import new
import exceptions

class PyjackError(exceptions.SystemError):
    pass

def _pyjack_fn(*args, **kwargs):    
    
    for filter in _pyjack_filters:                                      # -> Filters. cb[1] is the 'filter' function
        args,kwargs = filter(_pyjack_fo, *args, **kwargs)               #    used to change args,kwargs.

    if _pyjack_do_block:                                                # -> Original Function. Here, we call the org function.
        output = None                                                   #    If it's 'blocked' set the output to none, otherwise
    else:     
                                                                        #    the output is the output from the org function. 
        output = _pyjack_fo(*args, **kwargs)                        
        
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
            fn               = new.instancemethod(fx, im_self, im_class)
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

