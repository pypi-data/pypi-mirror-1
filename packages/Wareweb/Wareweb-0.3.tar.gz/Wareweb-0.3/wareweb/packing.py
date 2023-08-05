import sys
import inspect
import xmlrpclib
import traceback
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from paste.httpexceptions import HTTPBadRequest
json = None

__all__ = ['unpack', 'unpack_xmlrpc', 'unpack_json']

def unpack(func):
    """
    Unpacks ``self.path_parts`` and ``self.fields`` into a function
    call; this decorator can be used to turn such a method into a
    zero-argument method that unpacks those arguments.

    Arguments can have ``_path`` on the end of their name, in which
    case they are unpacked from the path.  Also variable arguments
    like ``*args`` will be unpacked from the path.

    Other arguments can have ``_int``, ``_list``, ``_float``, and
    ``_req`` appended.  These each do a convertion -- ``_int`` to
    integer, ``_float`` to floating point numbers, ``_list`` will make
    sure it is a list of items (and without this it cannot be a
    list!), ``_req`` that it is not empty.  A bad conversion will
    cause an HTTPBadRequest exception to be raised (this is not meant
    to be used for validation of user input, only for passing
    information back that came from the server).

    Note that the argument extensions shouldn't go in the HTTP
    variables, they are only present in the function signature.
    """
    argspec = FunctionArgSpec(func)
    def replacement_func(self):
        args, kw = argspec.unpack_args(self.path_parts, self.fields)
        return func(self, *args, **kw)
    replacement_func.__doc__ = func.__doc__
    replacement_func.__name__ = func.__name__
    return replacement_func

def unpack_xmlrpc(func):
    """
    Unpacks an XMLRPC request into a function call, and packs the
    response into a XMLRPC response.
    """
    def replacement_func(self):
        assert self.environ['CONTENT_TYPE'].startswith('text/xml')
        data = self.environ['wsgi.input'].read()
        xmlargs, method_name = xmlrpclib.loads(data)
        if method_name:
            kw = {'method_name': method_name}
        else:
            kw = {}
        self.set_header('content-type', 'text/xml; charset=UTF-8')
        try:
            result = func(self, *xmlargs, **kw)
        except:
            fault = make_rpc_exception(self.environ, sys.exc_info())
            body = xmlrpclib.dumps(
                xmlrpclib.Fault(1, fault), encoding='utf-8')
        else:
            if not isinstance(result, tuple):
                result = (result,)
            body = xmlrpclib.dumps(
                result, methodresponse=True, encoding='utf-8')
        self.write(body)
    replacement_func.__doc__ = func.__doc__
    replacement_func.__name__ = func.__name__
    return replacement_func

def make_rpc_exception(environ, exc_info):
    config = environ['paste.config']
    rpc_exception = config.get('rpc_exception', None)
    if rpc_exception not in (None, 'occurred', 'exception', 'traceback'):
        environ['wsgi.errors'].write(
            "Bad 'rpc_exception' setting: %r\n" % rpc_exception)
        rpc_exception = None
    if rpc_exception is None:
        if config.get('debug'):
            rpc_exception = 'traceback'
        else:
            rpc_exception = 'exception'
    if rpc_exception == 'occurred':
        fault = 'unhandled exception'
    elif rpc_exception == 'exception':
        fault = str(exc_info[0])
    elif rpc_exception == 'traceback':
        out = StringIO()
        traceback.print_exception(*exc_info, **{'file': out})
        fault = out.getvalue()
    return fault

def unpack_json(func):
    """
    Unpack a JSON request into a function call, and pack the return
    value into a JSON response.

    @@: Should this always create a JSON response?  Should there be
    a decorator to give a JSON response without a JSON request?
    """
    global json
    if json is None:
        import json
    def replacement_func(self):
        data = self.environ['wsgi.input'].read()
        jsonrpc = json.jsonToObj(data)
        method = jsonrpc['method']
        params = jsonrpc['params']
        id = jsonrpc['id']
        if method:
            kw = {'method_name': method}
        else:
            kw = {}
        self.set_header('content-type', 'text/plain; charset: UTF-8')
        try:
            result = func(self, *params, **kw)
        except:
            body = make_rpc_exception(self.environ, sys.exc_info())
            response = {
                'result': None,
                'error': body,
                'id': id}
        else:
            response = {
                'result': result,
                'error': None,
                'id': id}
        self.write(json.objToJson(response))
    replacement_func.__doc__ = func.__doc__
    replacement_func.__name__ = func.__name__
    return replacement_func


class FunctionArg(object):
    """
    Object that represents an argument to a function which may have
    magic extensions which fetch it from the path parts or coerce it
    to a specific type.

    Example:

    user_id_int_path: fetch user_id from path and coerce it into an 
    int
    """

    def __init__(self, name):
        self.from_path = False
        self.argname = name
        self.name_parts = []
        self.coercer = normal
        while 1:
            if name.endswith('_int'):
                self.add_coercer(make_int)
                self.name_parts.append(name[-4:])
                name = name[:-4]
            elif name.endswith('_list'):
                coercer = self.add_coercer(make_list)
                self.name_parts.append(name[-5:])
                name = name[:-5]
            elif name.endswith('_float'):
                self.add_coercer(make_float)
                self.name_parts.append(name[-6:])
                name = name[:-6]
            elif name.endswith('_req'):
                self.add_coercer(make_required)
                self.name_parts.append(name[-4:])
                name = name[:-4]
            elif name.endswith('_path'):
                if self.name_parts:
                    raise TypeError("The _path extension must come "
                        "last (use foo_int_path, not foo_path_int)")
                self.name_parts.append(name[-5:])
                name = name[:-5]
                self.from_path = True
            else:
                break
        self.name = name

    def add_coercer(self, new_coercer):
        coercer = self.coercer
        if not coercer or coercer is normal:
            self.coercer = new_coercer
        else:
            def coerce(val):
                return new_coercer(coercer(val))
            self.coercer = coerce

    def coerce(self, value):
        try:
            value = self.coercer(value)
        except (ValueError, TypeError), e:
            raise HTTPBadRequest(
                "Bad variable %r: %s" % (self.name, e))
        return value


class FunctionArgSpec(object):

    """
    Object that represents the parsed function signature for a given
    function.
    """

    def __init__(self, func):
        self.argnames, self.varargs, self.varkw, defaults = (
            inspect.getargspec(func))
        self.required_args = []
        self.required_path_args = []
        self.optional_path_args = []

        if self.argnames and self.argnames[0] == 'self':
            self.argnames = self.argnames[1:]
        funcargs = [FunctionArg(name) for name in self.argnames]
        argnames = [arg.name for arg in funcargs]
        for name in argnames:
            if argnames.count(name) > 1:
                raise TypeError("Argument names must be unique. "
                    "More than one found for %r" % name)
        self.funcargs = dict(zip(argnames, funcargs))

        while funcargs and funcargs[0].from_path:
            if len(defaults or ()) == len(funcargs):
                # This is an optional path segment
                self.optional_path_args.append(funcargs.pop(0))
                defaults = defaults[1:]
            else:
                self.required_path_args.append(funcargs.pop(0))
        if not defaults:
            self.required_args = funcargs
        else:
            self.required_args = funcargs[:-len(defaults)]

    def unpack_args(self, path_parts, fields):
        args = []
        found_args = []
        kw = {}
        if len(self.required_path_args) > len(path_parts):
            raise HTTPBadRequest(
                "Not enough parameters on the URL (expected %i more "
                "path segments)" % (len(self.required_path_args)-len(path_parts)))
        if (not self.varargs
            and (len(self.required_path_args)+len(self.optional_path_args))
                 < len(path_parts)):
            raise HTTPBadRequest(
                "Too many parameters on the URL (expected %i less path "
                "segments)" % (len(path_parts)-len(self.required_path_args)
                               -len(self.optional_path_args)))

        all_path_args = self.required_path_args + self.optional_path_args
        for i, value in enumerate(path_parts):
            if len(all_path_args) > i:
                value = all_path_args[i].coerce(value)
            args.append(value)
        for name, value in fields.iteritems():
            if not self.varkw and name not in self.funcargs:
                raise HTTPBadRequest("Variable %r not expected" % name)
            if name in self.funcargs:
                value = self.funcargs[name].coerce(value)
                name = self.funcargs[name].argname
            kw[name] = value
        for arg in self.required_args:
            if arg.argname not in kw:
                raise HTTPBadRequest("Variable %r required" % arg.name)
        return args, kw

def make_int(v):
    if isinstance(v, list):
        return map(int, v)
    else:
        return int(v)

def make_float(v):
    if isinstance(v, list):
        return map(float, v)
    else:
        return float(v)

def make_list(v):
    if isinstance(v, list):
        return v
    else:
        return [v]

def make_required(s):
    if s is None:
        raise TypeError
    return s

def normal(v):
    if isinstance(v, list):
        raise ValueError("List not expected")
    return v
