from Cookie import SimpleCookie
import timeinterval
import time

class Cookie(object):

    """
    Object that represents a cookie meant to be set.  This is like the
    standard ``Cookie.SimpleCookie`` object, only slightly nicer --
    each cookie object is just one ``name=value`` setting, and dates
    can be given as a few special values (``'ONCLOSE'``, ``'NOW'``,
    ``'NEVER'``, and ``timeinterval`` strings like ``'1w'``).
    """

    def __init__(self, name, value, path, expires=None, secure=False):
        self.name = name
        self.value = value
        self.path = path
        self.secure = secure
        if expires == 'ONCLOSE' or not expires:
            expires = None
        elif expires == 'NOW' or expires == 'NEVER':
            expires = time.gmtime(time.time())
            if expires == 'NEVER':
                expires = (expires[0] + 10,) + expires[1:]
            expires = time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", expires)
        else:
            if isinstance(expires, (str, unicode)) and expires.startswith('+'):
                interval = timeinterval.time_decode(expires[1:])
                expires = time.time() + interval
            if isinstance(expires, (int, long, float)):
                expires = time.gmtime(expires)
            if isinstance(expires, (tuple, time.struct_time)):
                expires = time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", expires)
        self.expires = expires

    def __repr__(self):
        return '<%s %s=%r>' % (
            self.__class__.__name__, self.name, self.value)

    def header(self):
        c = SimpleCookie()
        c[self.name] = self.value
        c[self.name]['path'] = self.path
        if self.expires is not None:
            c[self.name]['expires'] = self.expires
        if self.secure:
            c[self.name]['secure'] = True
        return str(c).split(':')[1].strip()
    
