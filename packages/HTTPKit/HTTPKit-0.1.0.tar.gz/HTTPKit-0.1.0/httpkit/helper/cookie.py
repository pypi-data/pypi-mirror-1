
#
# Helpers
#

import Cookie
from datetime import timedelta, datetime, date
import time

def _serialize_cookie_date(dt):
    if dt is None:
        return None
    if isinstance(dt, unicode):
        dt = dt.encode('ascii')
    if isinstance(dt, timedelta):
        dt = datetime.now() + dt
    if isinstance(dt, (datetime, date)):
        dt = dt.timetuple()
    return time.strftime('%a, %d-%b-%Y %H:%M:%S GMT', dt)

def set_cookie(key, value='', max_age=None,
               path='/', domain=None, secure=None, httponly=False,
               version=None, comment=None, expires=None, charset='utf8'):
    """
    Set (add) a cookie for the response
    """
    if isinstance(value, unicode) and charset is not None:
        value = '"%s"' % value.encode(charset)
    cookies = Cookie.BaseCookie()
    cookies[key] = value
    if isinstance(max_age, timedelta):
        max_age = max_age.seconds + max_age.days*24*60*60
    if max_age is not None and expires is None:
        expires = datetime.utcnow() + timedelta(seconds=max_age)
    if isinstance(expires, timedelta):
        expires = datetime.utcnow() + expires
    if isinstance(expires, datetime):
        expires = '"'+_serialize_cookie_date(expires)+'"'
    for var_name, var_value in [
        ('max_age', max_age),
        ('path', path),
        ('domain', domain),
        ('secure', secure),
        ('HttpOnly', httponly),
        ('version', version),
        ('comment', comment),
        ('expires', expires),
        ]:
        if var_value is not None and var_value is not False:
            cookies[key][var_name.replace('_', '-')] = str(var_value)
    header_value = cookies[key].output(header='').lstrip()
    if header_value.endswith(';'):
        # Python 2.4 adds a trailing ; to the end, strip it to be
        # consistent with 2.5
        header_value = header_value[:-1]
    return header_value

def get_cookie(cookie_string, name=None):
    if cookie_string:
        cookie = Cookie.SimpleCookie()
        cookie.load(cookie_string)
        if name:
            if cookie.has_key(name):
                return cookie[name].value
        else:
            return cookie
    else:
        return None

