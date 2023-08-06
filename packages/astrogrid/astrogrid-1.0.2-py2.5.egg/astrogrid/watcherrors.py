__id__ = '$Id: watcherrors.py 111 2007-06-03 10:30:23Z eddie $'

from astrogrid import acr
import os, sys, inspect
import xmlrpclib
errorframe = None

# We have two ways of decorating here.
# The first one is based on this thread and conserves the method signature.
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/60f22ed33af5dbcb/5f870d271456ccf3

def _signature_gen(varnames, n_default_args, n_args, rm_defaults=False):
    n_non_default_args = n_args - n_default_args
    non_default_names = varnames[:n_non_default_args]
    default_names = varnames[n_non_default_args:n_args]
    other_names = varnames[n_args:]
    n_other_names = len(other_names)
    for name in non_default_names:
        yield "%s" % name
    for i, name in enumerate(default_names):
        if rm_defaults:
            yield name
        else:
            yield "%s = arg[%s]" % (name, i)
    if n_other_names == 1:
        yield "*%s" % other_names[0]
    elif n_other_names == 2:
        yield "*%s" % other_names[0]
        yield "**%s" % other_names[1]

def decorate(func, caller):
    args, varargs, varkw, defaults = inspect.getargspec(func)
    argdefs = defaults or ()
    argcount = func.func_code.co_argcount
    varnames = args + (varargs or []) + (varkw or [])
    signature = ", ".join(_signature_gen(varnames, len(argdefs), argcount))
    variables = ", ".join(_signature_gen(varnames, len(argdefs), argcount, rm_defaults=True))
    lambda_src = "lambda %s: call(func, %s)" % (signature, variables)
    #print func.__name__, "->", lambda_src
    dec_func = eval(lambda_src, dict(func=func, call=caller, arg=argdefs))
    dec_func.__name__ = func.__name__
    dec_func.__doc__ = func.__doc__
    dec_func.__dict__ = func.__dict__.copy()
    return dec_func 
    
def watcherrors_tracer(function, *args, **kwargs):
    self = args[0]
    if hasattr(self, '__status'):
        if not self.__status: 
            return
    try:
        res = function(*args, **kwargs)
        if function.__name__ == '__init__': self.__status = True
        return res
    except AttributeError:
        if function.__name__ == '__init__': self.__status = False
        print '-'*60
        error_type, error, traceback = sys.exc_info()
        print function.__name__
        print error_type
        print error
        print '-'*60
    except xmlrpclib.Fault, e:
    	message = e.faultString
    	if message.find('CommunitySecurityException'):
    		i = message.find('CommunitySecurityException')
    		acr._ELOG(message[i+26:])
    	elif message.find('CommunityResolverException'):
    		acr._ELOG('Community not found')
    	else:
    		acr._ELOG(' '+message)

        #raise  # Optional-- you may want to squech some errors here
            
def watcherrors2(fn):
	return decorate(fn, watcherrors_tracer)

def needslogin_tracer(function, *args, **kwargs):
    self = args[0]
    if acr.autologin():
        return function(*args, **kwargs)
    else:
        acr._ELOG('Need to login to access this function.')
            
def needslogin2(fn):
	return decorate(fn, needslogin_tracer)
	

# It looks like the avobe works so we are keeping it for now.
# Just in case, below the classical decorators which do keep information about
# the methods names but substutite the method signature.
	
def watcherrors1(function):
    '''function decorator to display Exception information.'''
    def substitute(*args, **kwargs):
        self = args[0]
        if hasattr(self, '__status'):
            if not self.__status: 
                return
        try:
            res = function(*args, **kwargs)
            if function.__name__ == '__init__': self.__status = True
            #if hasattr(res, 'im_func'):
           #    res.im_func.func_name = function.func_name
            #   res.im_func.func_code = function.func_code
            return res
        except AttributeError:
            if function.__name__ == '__init__': self.__status = False
            print '-'*60
            error_type, error, traceback = sys.exc_info()
            print function.__name__
            print error_type
            print error
            print '-'*60
            #raise  # Optional-- you may want to squech some errors here

    substitute.__name__ = function.__name__
    substitute.__doc__ = function.__doc__
    substitute.__module__ = function.__module__
    substitute.__dict__.update(function.__dict__)
    substitute.func_name = function.func_name
    # substitute.func_defaults = function.func_defaults

    try:
        substitute.__doc__ = function.__doc__
    except AttributeError:
        pass

    return substitute


def needslogin1(function):
    def substitute(*args, **kwargs):
        self = args[0]
        if acr.autologin():
            return function(*args, **kwargs)
        else:
            acr._ELOG('Need to login to access this function.')
        
    return substitute
        
    

# You can use it as follows to wrap functions and methods:
'''
class ....

     @watcherrors
     def something(somearg)
         if somearg is not None:
                 raise ValueError(somearg)
     ...
'''

# Alternative: (watcherrors is defined almost as above)

def augmentedwatch(holder, framefieldname):
    def watcherrors(function):
        '...' # -- same as above
        def substitute(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception:
                error_type, error, traceback = sys.exc_info()
                ### new code:
                errorframe = getattr(holder, framefieldname, None) 
                '...' # -- same as above
        return substitute
    return watcherrors

# You use this as follows to wrap functions and methods, where 
# holder is an expression at "first import" time that will, at
# the time of one of the uncaught exceptions, have an attribute 
# named 'frame':
''' 
class ....

     @augmentedwatch(holder, 'frame')
     def something(somearg)
         if somearg is not None:
                 raise ValueError(somearg)
     ...
'''

watcherrors = watcherrors2
needslogin = needslogin2

