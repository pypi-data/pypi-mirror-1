import fcgi
import greenlet
import traceback
import cgi
import Cookie
import inspect
import base64
import sys
import hashlib
import random
import time
import cPickle
import random
import markdown as markdownmod
import durus.client_storage
import durus.connection
from durus.persistent import PersistentObject as persist
from durus.persistent_dict import PersistentDict as pdict
from durus.persistent_list import PersistentList as plist
from urllib import quote as urlq

_conts = {}
_greenletToId = {}
_sessdb = {}
_handlers = {None: {}}
globalHelperOps = {}
_fnUrl = 'x'
_yieldTo = None
_SESSION_COOKIE = 'pyflow_session'
datastore = durus.connection.Connection(durus.client_storage.ClientStorage())
_curdom = None
_usingDom = False
_domRoot = ""

def setdom(dom):
    global _curdom
    global _usingDom
    if dom: _usingDom = True
    _curdom = dom
    if _curdom not in _handlers: _handlers[_curdom] = {}
    if _curdom not in datastore.get_root(): datastore.get_root()[_curdom] = pdict()
    _addHelperOps(_handlers[_curdom])

def genid():
    """ generate a base64 url-insertable random key """
    # todo; include ip addr &| 'secret' salt?
    return base64.urlsafe_b64encode(hashlib.sha1('%s %s' % (random.random(), time.time())).digest())[:-1]

def _makeHandler(runnable):
    id = genid()
    ret = greenlet.greenlet(runnable)
    _conts[id] = (ret, inspect.getargspec(runnable)[0], getattr(runnable, 'no_query_map', False))
    _greenletToId[ret] = id
    return (id, ret)

def _addHelperOps(to):
    for k,v in globalHelperOps.iteritems(): to[k] = v

def op(func, name=None):
    if name == None: name = func.__name__
    _handlers[_curdom]['/' + name] = (func, "" if _curdom == None else "/" + _curdom)
    return func
def oproot(func): return op(func, '')

def flat(*args):
    """
    flatten stuff

    >>> def rec(*args):
    ...     return flat('a', args, 'b')
    >>> flat('alpha')
    'alpha'
    >>> flat('alpha', 'bravo')
    'alpha bravo'
    >>> rec('alpha', 'bravo')
    'a alpha bravo b'

    """
    res = []
    for a in args:
        if hasattr(a, '__iter__'):
            res.append(flat(*a))
        else:
            res.append(str(a))
    return ' '.join(res)

def text(s):
    """ cede'ing handler for generic text output """
    def ret(*args): cede(s)
    return ret

def markdown(s):
    """ output html for markdown `s`. code highlighting enabled """
    return str(markdownmod.Markdown(s, extensions=['codehilite'], encoding='utf8', safe_mode=False))

def randomof(l): return l[random.randint(0, len(l) - 1)]

def html(*args):
    return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>%s</html>
""" % flat(args)

def _attrsToString(attrs):
    ret = []
    #print >>sys.stderr, attrs
    for k, v in attrs.items():
        fixedk = k
        if fixedk == "klass": fixedk = "class"
        if fixedk == "fer": fixedk = "for"
        fixedk = fixedk.replace("_", "-")
        ret.append(fixedk + '="' + v + '"')
    if len(ret) == 0: return ''
    return ' ' + ' '.join(ret)
def tag(tagname, *args, **attrs): return """<%s%s>%s</%s>""" % (tagname, _attrsToString(attrs), flat(args), tagname)
def tagx(tagname, **attrs): return """<%s%s />""" % (tagname, _attrsToString(attrs))
def head(*args, **attrs): return tag("head", *args, **attrs)
def title(*args, **attrs): return tag("title", *args, **attrs)
def meta(**attrs): return tagx("meta", **attrs)
ctutf8 = meta(http_equiv='Content-Type', content='text/html; charset=utf-8')
def extcss(fn): return tagx("link", rel='stylesheet', type='text/css', href=fn)
def extjs(fn): return tag("script", type='text/javascript', src=fn)
def body(*args, **attrs): return tag("body", *args, **attrs)
def div(klass, *args): return tag("div", *args, **{'class':klass})
def ediv(klass): return tag("div", "&nbsp;", **{'class':klass})
def span(klass, *args): return tag("span", *args, **{'class':klass})
def form(*args, **attrs): return tag("form", *args, **attrs)
def fixed600(*args): return div("f600", *args)
def fixed750(*args): return div("f750", *args)
def fixed950(*args): return div("f950", *args)
def fixed974(*args): return div("f974", *args)
def br(count=1): return tagx("br")*count
def withsep(sep, *args): return (" " + sep + " ").join([flat(a) for a in args])
def withsepbull(*args): return withsep("&bull;", *args)
def withsepbr(*args): return withsep("<br />", *args)
def ul(*args, **attrs): return tag("ul", *args, **attrs)
def li(*args, **attrs): return tag("li", *args, **attrs)
def h1(*args, **attrs): return tag("h1", *args, **attrs)
def h2(*args, **attrs): return tag("h2", *args, **attrs)
def h3(*args, **attrs): return tag("h3", *args, **attrs)
def para(*args, **attrs): return tag("p", *args, **attrs)
def bold(*args, **attrs): return tag("b", *args, **attrs)
def img(*args, **attrs): return tagx("img", *args, **attrs)
def defpage(*body_, **extra):
    return html(
            head(title(extra.get("title", "PyFlow")),
                 ctutf8,
                 extcss('/static/default.css')
                 + flat(extra.get("extrahead", ()))),
            body(flat(body_))
            )

def makelabel(lab, forwhat): return tag("label", lab + ": " if lab else '', fer=forwhat)
def submit(value="Submit"): return tagx("input", type="submit", id="submit", value=value, klass="submit")
def hidden(name, value): return tagx("input", type="hidden", name=name, id=name, value=value)
def input(name, value="", size=20): return tagx("input", name=name, id=name, type="text", value=value, size=str(size))
def inputl(name, value="", size=20, label=None):
    if label == None: label = name
    return makelabel(label, name) + input(name, value, size)
def password(name, size=20): return tagx("input", name=name, id=name, type="password", value="", size=str(size))
def passwordl(name, size=20, label=None):
    if label == None: label = name
    return makelabel(label, name) + password(name, size)
def textarea(name, value="", rows=4, cols=40):
    return tag("textarea", value, name=name, id=name, rows=str(rows), cols=str(cols))
def textareal(name, value="", rows=4, cols=40, label=None):
    if label == None: label = name
    return makelabel(label, name) + textarea(name, value, rows, cols)
def fileupload(name, size=40):
    return tagx("input", name=name, id=name, type="file", size=str(size))
def fileuploadl(name, size=40, label=None):
    if label == None: label = name
    return makelabel(label, name) + fileupload(name, size)

def aform(handler, *args):
    # todo; 'submit' in kwargs or isinstance(args, submit) for other custom submit
    return form(tag("fieldset", withsepbr(*args), br(),
                hidden(name='_a', value=_makeHandler(handler)[0]),
                makelabel(None, "submit"), submit()),
            **{'method':'POST', 'action':'/'+_fnUrl})

def extlink(url, text): return "<a href='%s'>%s</a>" % (url, text)

def link(handler, text=None):
    if isinstance(handler, basestring):
        if text == None: text = handler
        return "<a href='%s/%s'>%s</a>" % (_domRoot, handler, text)
    else:
        return "<a href='/%s?_a=%s'>%s</a>" % (_fnUrl, _makeHandler(handler)[0], text)

class redir:
    def __init__(self, loc):
        self.loc = _domRoot + "/" + loc

def cede(res): _yieldTo.switch(res)

def pdump(data, fn):
    f = open(fn, "w")
    cPickle.dump(data, f)
    f.close()

def pload(fn):
    f = open(fn, "r")
    ret = cPickle.load(f)
    f.close()
    return ret

def _GetSession(cookies):
    isnew = False
    if _SESSION_COOKIE not in cookies or cookies[_SESSION_COOKIE].value not in _sessdb:
        s = genid()
        _sessdb[s] = {}
        cookies[_SESSION_COOKIE] = s
        isnew = True
    else:
        s = cookies[_SESSION_COOKIE].value
    return (isnew, s, _sessdb[s])

def _SaveSession(cookies, s, sess):
    _sessdb[s] = sess
    cookies[_SESSION_COOKIE] = s 

class _Response:
    def __init__(self, env, debug):
        self.headers = ['Content-Type: text/html\r\n']
        self.body = ''
        self.cookies = Cookie.SimpleCookie()
        self.Status('200 OK')
        self.cookies.load(env.get('HTTP_COOKIE', ''))
        self.debug = debug

    def Status(self, status):
        self.status = 'Status: ' + status + '\r\n'

    def AddHeader(self, header):
        self.headers.append(header + '\r\n')

    def Write(self, req):
        # todo; doesn't quite work; sticks extra space in places where it shouldn't,
        # specifically inside of textarea tags, and after link text but before </a>.
        #if self.debug:
            #from BeautifulSoup import BeautifulSoup
            #self.body = BeautifulSoup(self.body).prettify()
        self.AddHeader('Content-Length: ' + str(len(self.body)))
        headers = self.status + ''.join(self.headers) + self.cookies.output() + '\r\n\r\n'
        req.out.write(headers + self.body)

    def AddBody(self, body):
        self.body += body

def mapQueryToFuncArgs(query, funcargs, debug):
    if debug:
        querySet = set(query.keys())
        funcSet = set(funcargs)

        inFunctionButNotQuery = funcSet.difference(querySet)
        if len(inFunctionButNotQuery): raise Exception, "function was expecting " + str(list(inFunctionButNotQuery)) + " but weren't in query"

        inQueryButNotFunction = querySet.difference(funcSet)
        if len(inQueryButNotFunction): raise Exception, "function wasn't expecting " + str(list(inQueryButNotFunction)) + " but appeared in query"

    return [query[fa][0] for fa in funcargs]

def _getstoretype(root, typ, typname):
    cur = datastore.get_root()[_curdom].get(root)
    if cur:
        if not isinstance(cur, typ): raise Exception, "already something named '%s' that isn't a %s" % (root, typname)
        return cur
    ret = typ()
    datastore.get_root()[_curdom][root] = ret
    return ret
def getstoredict(root):
    """ get a persistent dict named by `root'. call commit() or abort() to store/cancel writes. """
    return _getstoretype(root, pdict, "dict")
def getstorelist(root):
    """ get a persistent list named by `root'. call commit() or abort() to store/cancel writes. """
    return _getstoretype(root, plist, "list")
def commit():
    #print >>sys.stderr, "calling commit"
    datastore.commit()
def abort():
    #print >>sys.stderr, "calling commit"
    datastore.abort()
if None not in datastore.get_root(): datastore.get_root()[None] = pdict()

class _RequestData(object):
    def __init__(self, query, sessid):
        self.query = query
        self.sessid = sessid

    def getint(self, key):
        """ returns the query string value or post data value (as an int) specified by key """
        return int(self.get(key))

    def get(self, key):
        """ returns the query string value or post data value (as a string) specified by key """
        return self.query.get(key, [None])[0]

    @property
    def ip(self):
        return self.get('REMOTE_ADDR')

def appserve(debug=False, namebased=False):

    global _handlers
    global _yieldTo
    global _domRoot
    if not _usingDom: _addHelperOps(_handlers[None])

    if _usingDom:
        if len(_handlers[None]):
            raise Exception, "setdom was called, but these ops were inserted before the first call: " + flat(_handlers[None].keys())

    if not namebased:
        if '' in _handlers:
            raise Exception, "setdom('') used without namebased=True"

    """ namespacing handling:
        1) completely ignored setdom (for simple stuff), so there's a bunch that are [None]['/func']
        2) setdom'd so there's ['dom']['/func']

        if setdom'd and we're not namebased:
            modify all ['dom']['/func'] to [None]['/dom/func']
            on each request, update root for link() to curop's dom
        else:
            root = "/"
            """
    if _usingDom and not namebased:
        for dom in _handlers.keys():
            for fname in _handlers[dom].keys():
                _handlers[None]['/' + dom + fname] = _handlers[dom][fname]

    try:
        while fcgi.isFCGI():
            req = fcgi.Accept()
            try:
                resp = _Response(req.env, debug)
                resp.cookies.load(req.env.get('HTTP_COOKIE', ''))
                (isnew, id, sess) = _GetSession(resp.cookies)
                #print >>sys.stderr, isnew, id, sess
                scriptName = req.env.get('SCRIPT_NAME', '/')
                if req.env['REQUEST_METHOD'] == "GET":
                    query = cgi.parse_qs(req.env.get('QUERY_STRING', ''))
                elif req.env['REQUEST_METHOD'] == "POST":
                    contlen = int(req.env['CONTENT_LENGTH'])
                    if contlen < 2000000: # todo; conf
                        data = sys.stdin.read(contlen)
                        query = cgi.parse_qs(data)
                    else:
                        raise Exception, "post data too large"
                action = query.get('_a', [None])[0]
                if scriptName == "/x" and action:
                    _yieldTo = greenlet.getcurrent()
                    #print >>sys.stderr, _conts
                    cont = _conts[action][0]
                    del query['_a']
                    argspec = _conts[action][1]
                    noQueryMap = _conts[action][2]
                    if noQueryMap:
                        result = cont.switch(_RequestData(query, id))
                    else:
                        result = cont.switch(*mapQueryToFuncArgs(query, argspec, debug))
                    resp.Status('302 Moved Temporarily')
                    if isinstance(result, redir):
                        resp.AddHeader('Location: ' + result.loc)
                    else:
                        sess['__result'] = result
                        resp.AddHeader('Location: ' + sess['__curop'])
                    _yieldTo = None
                elif '__result' in sess:
                    resp.AddBody(sess['__result'])
                    del sess['__result']
                else:
                    if _usingDom and namebased:
                        splitdom = req.env['HTTP_HOST'].lower().split(".")
                        if len(splitdom) == 2: hostprefix = ''
                        else: hostprefix = splitdom[0]
                        #print >>sys.stderr, req.env['HTTP_HOST']
                        if hostprefix in _handlers:
                            handler = _handlers[hostprefix].get(scriptName)
                        else:
                            handler = None
                    else:
                        handler = _handlers[None].get(scriptName)
                    if handler:
                        commit() # this isn't really a commit, it's a sync. durus' caching is a bit weird
                        sess['__curop'] = scriptName
                        if _usingDom and not namebased:
                            _domRoot = handler[1]
                        _yieldTo = greenlet.getcurrent()
                        (hid, run) = _makeHandler(handler[0])
                        resp.AddBody(run.switch(_RequestData(query, id)))
                        _yieldTo = None
                    else:
                        if not scriptName[-1:] == "/":
                            resp.Status('302 Moved Temporarily')
                            resp.AddHeader('Location: ' + scriptName + "/")
                        else:
                            resp.Status("404 Not Found")
                            resp.AddBody(defpage(scriptName + " not found"))
                #print >>sys.stderr, "going to save session:", isnew, id, sess
                _SaveSession(resp.cookies, id, sess)
                resp.Write(req)
                resp = None
            except:
                if debug:
                    req.out.write('Content-Type: text/plain\r\n\r\nException thrown:\r\n\r\n' + traceback.format_exc())
                else:
                    req.out.write('Status: 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nInternal Server Error.')
            finally:
                req.Finish()
    except KeyboardInterrupt:
        pass
