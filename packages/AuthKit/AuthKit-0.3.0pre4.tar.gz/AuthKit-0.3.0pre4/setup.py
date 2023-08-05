from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

version = '0.3.0pre4'

setup(
    name="AuthKit",
    version=version,
    description='An authentication and authorization toolkit for WSGI applications and frameworks',
    long_description="""
*   Built for WSGI applications and middleware
*   Sophisticated and extensible permissions system
*   Built in support for HTTP basic, HTTP digest, form, cookie and OpenID authentication 
    mehtods plus others.
*   Easily define users, passwords and roles
*   Designed to be totally extensible so you can use the components to integrate
    with a database, LDAP connection or your own custom system.
*   Plays nicely with the `Pylons <http://pylonshq.com>`_ web framework.
    
There is also a `development version <http://authkit.org/svn/AuthKit/trunk#egg=AuthKit-dev>`_.

Installation
============

Source distribution::

    unzip zxfv AuthKit-%s.zip
    cd AuthKit-%s
    python setup.py install

or using `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_::

    easy_install -U "AuthKit==%s"

or if you don't have easy_install installed yet::

    wget http://peak.telecommunity.com/dist/ez_setup.py
    python ez_setup.py "AuthKit==%s"
    
Development version::

    svn co http://authkit.org/svn/AuthKit/trunk AuthKit
    cd AuthKit
    python setup.py develop

Get Started
===========

* `Download and Installation <http://python.org/pypi/AuthKit/%s>`_
* `AuthKit Manual <http://authkit.org/docs/manual.html>`_
* `Module Reference <http://authkit.org/docs/module-index.html>`_
* `Pylons Integration Manual <http://authkit.org/docs/pylons.html>`_
* `Trac <http://authkit.org/trac>`_ - Tickets, Wiki, Subversion
* `Examples <http://authkit.org/trac/browser/AuthKit/trunk/examples>`_
"""%(version,version,version,version,version),
    license = 'MIT',
    author='James Gardner',
    author_email='james@pythonweb.org',
    url='http://3aims.com/',
    packages=find_packages(exclude=['ez_setup','examples','docs']),
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        "Paste>=1.1",
    ],
    extras_require = {
        'pylons': ["Pylons>=0.9"],
        'mysql': ["SQLAlchemy>=0.3.2", "DBUtils>=0.9.2"],
        'beaker': ["Beaker"],
        'full': ["Pylons>=0.9", "SQLAlchemy>=0.3.2", "DBUtils>=0.9.2", "Beaker", "pudge==dev", "buildutils==dev", "pygments==0.6"],
        'pudge': ["pudge==dev", "buildutils==dev", "pygments==0.6"],
    },
)
