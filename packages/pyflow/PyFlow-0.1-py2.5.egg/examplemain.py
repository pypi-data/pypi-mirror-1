from pyflow.core import *

# semi-complex hello world (http://localhost:8080/said)

@op
def said(req):
    def result(foo):
        cede(link(text("you said: " + foo),
                  "click here"))
    cede(aform(result, input("foo")))


# start server:
#
# debug=True gives tracebacks in browser
#
# namebased=True makes urls be
#   http://blog.mydomain.com/...
# instead of
#   http://mydomain.com/blog/...
#
appserve(debug=True)
