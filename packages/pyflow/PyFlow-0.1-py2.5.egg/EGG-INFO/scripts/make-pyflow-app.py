#!/usr/bin/python
import sys, urllib, os
import shutil
from pkg_resources import Requirement, resource_filename
from optparse import OptionParser

def ensureprog(prog):
    if os.system("which \"%s\"") != 256:
        print "Error: '%s' not found." % prog
        raise SystemExit
def ensuredir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
def run(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print "Error: in '%s'. Stopping." % cmd
        raise SystemExit

parser = OptionParser("usage: %prog [options] app-name")
parser.add_option("-d", "--dir", dest="directory", help="directory to create project in", default=".")
# todo;
#parser.add_option("-p", "--port", dest="port", help="port to serve on", type="int", default=8080)
#parser.add_option("-c", "--children", dest="children", help="number of backends to spawn", type="int", default=4)
(options, args) = parser.parse_args()
if len(args) != 1: parser.error("must specify application name")
ensureprog("tar")
ensureprog("gunzip")
name = args[0]
children = 4
path = os.path.abspath(os.path.join(options.directory, name))
if os.path.exists(path):
    print "Path: '%s' already exists. Please move/remove before making a project there." % path
    raise SystemExit
tmppath = os.path.abspath("/tmp")
ensuredir(path)
ensuredir(tmppath)

print "Making '%s' in '%s' (%d backends)..." % (name, path, children)
nginx_tgz = "nginx-0.5.35.tar.gz"
lighttpd_tgz = "lighttpd-1.4.18.tar.gz"

tmp_nginx_tgz = os.path.join(tmppath, nginx_tgz)
if not os.path.exists(tmp_nginx_tgz):
    print "Grabbing", nginx_tgz
    urllib.urlretrieve("http://sysoev.ru/nginx/" + nginx_tgz, tmp_nginx_tgz)

tmp_lighttpd_tgz = os.path.join(tmppath, lighttpd_tgz)
if not os.path.exists(tmp_lighttpd_tgz):
    print "Grabbing", lighttpd_tgz, "(only for spawn-fcgi)"
    urllib.urlretrieve("http://www.lighttpd.net/download/" + lighttpd_tgz, tmp_lighttpd_tgz)

ensuredir(os.path.join(path, "tmp"))
ensuredir(os.path.join(path, "logs"))
ensuredir(os.path.join(path, "src"))
ensuredir(os.path.join(path, "sbin"))

os.chdir(path)
run("rm -rf '%s'" % os.path.join(path, "nginx-0.5.35"))
run("tar xfz '%s'" % tmp_nginx_tgz)
os.chdir(os.path.join(path, "nginx-0.5.35"))
run("./configure --prefix=\"%s\"" % path)
run("make")
shutil.copyfile("objs/nginx", os.path.join(path, "sbin", "nginx"))
run("chmod +x \"%s\"" % (os.path.join(path, "sbin", "nginx")))

os.chdir(path)
run("rm -rf '%s'" % os.path.join(path, "lighttpd-1.4.18"))
run("tar xfz '%s'" % tmp_lighttpd_tgz)
os.chdir(os.path.join(path, "lighttpd-1.4.18"))
run("./configure")
os.chdir(os.path.join(path, "lighttpd-1.4.18", "src"))
run("make spawn-fcgi")
shutil.copyfile("spawn-fcgi", os.path.join(path, "sbin", "spawn-fcgi"))
run("chmod +x \"%s\"" % (os.path.join(path, "sbin", "spawn-fcgi")))

confdir = resource_filename(Requirement.parse("PyFlow"),"conf")
shutil.copytree(confdir, os.path.join(path, "conf"))
htmldir = resource_filename(Requirement.parse("PyFlow"),"html")
shutil.copytree(confdir, os.path.join(path, "html"))
runscript = resource_filename(Requirement.parse("PyFlow"),"sbin/run")
shutil.copyfile(runscript, os.path.join(path, "sbin", "run"))
run("chmod +x \"%s\"" % (os.path.join(path, "sbin", "run")))
servermgr = resource_filename(Requirement.parse("PyFlow"),"sbin/servermgr.py")
shutil.copyfile(servermgr, os.path.join(path, "sbin/servermgr.py"))
servermgr = resource_filename(Requirement.parse("PyFlow"),"sbin/servermgr.py")
shutil.copyfile(servermgr, os.path.join(path, "sbin/servermgr.py"))
servermgr = resource_filename(Requirement.parse("PyFlow"), "examplemain.py")
shutil.copyfile(servermgr, os.path.join(path, "src/main.py"))


os.chdir(path)
run("rm -rf '%s'" % os.path.join(path, "lighttpd-1.4.18"))
run("rm -rf '%s'" % os.path.join(path, "nginx-0.5.35"))

print "\nProject created in %s" % path
print "To get started:\n  $ cd \"%s\"\n  $ sbin/run" % path
