from Cookie import SimpleCookie
from pyjamas.__pyjamas__ import doc
import urllib
import datetime
from string import strip

def getCookie(key):
    return getCookie2(key)
    JS("""
    var cookies = Cookies_loadCookies();
    var value = cookies[key];
    return (value == null) ? null : value;
    """)

def getCookie2(cookie_name):
    cookiestr = doc().props.cookie
    c = SimpleCookie(cookiestr)
    cs = c.get(cookie_name, None)
    print "getCookie2", cookiestr, "name", cookie_name, "val", cs
    if cs:
        return cs.value
    return None
    
    JS("""
    var results = document.cookie.match ( '(^|;) ?' + cookie_name + '=([^;]*)(;|$)' );

    if ( results )
        return ( decodeURIComponent ( results[2] ) );
    else
        return null;

    """)

# expires can be int or Date
def setCookie(name, value, expires, domain=None, path=None, secure=False):
    cookiestr = doc().props.cookie
    c = SimpleCookie(cookiestr)
    c[name] = value
    m = c[name]
    d = datetime.datetime.now() + datetime.timedelta(0, expires/1000)
    d = d.strftime("%a, %d %b %Y %H:%M:%S GMT")
    m['expires'] = '"%s"' % d
    if domain:
        m['domain'] = domain
    if path:
        m['path'] = path
    if secure:
        m['secure'] = ''

    c = c.output(header='').strip()
    print "set cookies", c

    doc().props.cookie = c

    return
    JS("""
    if (expires instanceof Date) expires = expires.getTime();
    if (pyjslib_isUndefined(domain)) domain = null;
    if (pyjslib_isUndefined(path)) path = null;
    if (pyjslib_isUndefined(secure)) secure = false;
    
    var today = new Date();
    var expiration = new Date();
    expiration.setTime(today.getTime() + expires)

    var c = encodeURIComponent(name) + '=' + encodeURIComponent(value);
    c += ';expires=' + expiration.toGMTString();

    if (domain)
        c += ';domain=' + domain;
    if (path)
        c += ';path=' + path;
    if (secure)
        c += ';secure';

    $doc.cookie = c;
    """)

def get_crumbs():
    docCookie = doc().props.cookie
    c = SimpleCookie(docCookie)
    c = c.output(header='')
    return map(strip, c.split('\n'))

def loadCookies():
    JS("""
    var cookies = {};

    var docCookie = $doc.cookie;

    if (docCookie && docCookie != '') {
        var crumbs = docCookie.split(';');
        for (var i = 0; i < crumbs.length; ++i) {
            alert(crumbs.length);
            var name, value;

            var eqIdx = crumbs[i].indexOf('=');
            if (eqIdx == -1) {
                name = crumbs[i];
                value = '';
            } else {
                name = crumbs[i].substring(0, eqIdx);
                value = crumbs[i].substring(eqIdx + 1);
            }

            alert(name);
            alert(value);

        cookies[decodeURIComponent(name)] = decodeURIComponent(value);
        }
    }

    return cookies;
    """)

