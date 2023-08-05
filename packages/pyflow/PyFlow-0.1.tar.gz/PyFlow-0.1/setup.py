import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "PyFlow",
    version = "0.1",
    package_dir = { '': 'src' },
    packages = [ 'pyflow' ],
    scripts = ['distscripts/make-pyflow-app.py'],

    install_requires = ['durus', 'greenlet', 'pyinotify', 'markdown' ],

    package_data = {
        'pyflow': ['../conf/*',
            '../html/*.html',
            '../html/static/*.css',
            '../html/static/*.png',
            '../sbin/run',
            '../sbin/servermgr.py',
            '../examplemain.py']
    },

    # metadata for upload to PyPI
    author = "Scott Graham",
    author_email = "scott.pypi@h4ck3r.net",
    description = "PyFlow is a continuation-based web development library.",
    keywords = "web http continuations greenlet coroutines",
    url = "http://blog.pipinghot.info/",
)

