from pyflow.core import *
import inspect

_Users = getstoredict("__users")
_Logins = getstoredict("__logins")

def _finish(req, user, after):
    _Logins[req.sessid] = user
    commit()
    if isinstance(after, basestring): cede(redir(after))
    else: cede(after())

def loginPage(req, after, msg=""):
    def onlogin(user, password):
        if user not in _Users or hashlib.sha1(password).digest() != _Users[user]["pw"]:
            return cede(loginPage(req, after, "Bad user name or password."))
        return _finish(req, user, after)

    def onregister(user, password, password2):
        if user in _Users: return cede(loginPage(req, after, "User name is already taken, please choose another."))
        if password != password2: return cede(loginPage(req, after, "Passwords didn't match."))
        _Users[user] = pdict()
        _Users[user]['name'] = user
        _Users[user]['pw'] = hashlib.sha1(password).digest()
        return _finish(req, user, after)

    cede(defpage(tag("b", msg),
        br(2),
        aform(onlogin, tag("b", "Login"),
            inputl("user"),
            passwordl("password")),
        br(3),
        aform(onregister, 
            tag("b", "Register"),
            inputl("user"),
            passwordl("password"),
            passwordl("password2", label="confirm"))))

def reqlogin(func):
    """ decorator, require login to access this handler function. """
    def wrap(req):
        mapped = mapQueryToFuncArgs(req.query, inspect.getargspec(func)[0], False)
        if getUser(req):
            func(*mapped)
        else:
            cede(loginPage(req, lambda: func(*mapped), "You need to be logged in to do that."))
    wrap.no_query_map = True
    return wrap

def oplogin(func):
    """ decorator: export function as /func, but require login to access. """
    def wrap(req):
        if getUser(req):
            func(req)
        else:
            cede(loginPage(req, lambda: func(req), "You need to be logged in to do that."))
    return op(wrap, func.__name__)

def getUser(req):
    return _Logins.get(req.sessid)


def whoami(req):
    user = getUser(req)
    if user: return defpage("Logged in as " + user + ".")
    else: return defpage("You are not logged in. " + link(lambda: loginPage(req, "whoami"), "Log in") + ".")
globalHelperOps['whoami'] = whoami
