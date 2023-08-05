from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

setup(
    name="AuthKit",
    version='0.2.4a',
    description='An autentication and authorisation system for Pylons currently in alpha.',
    long_description="""
* A complete autentication and authorisation system
* Updated for Pylons 0.9 and SQLAlchemy 0.2
* As yet no unit tests exist so expect some bugs
* APIs still subject to change

Best documentation currently at http://pylonshq.com/project/pylonshq/browser/AuthKit/trunk/docs/manual.txt
""",
    license = 'MIT',
    author='James Gardner',
    author_email='james@pythonweb.org',
    url='http://pythonshq.com/',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Pylons>=0.9",
        "FormBuild>=0.1",
        "FormEncode>=0.4",
        "SQLAlchemy>=0.2.4,<0.3.0",
        "web>=0.6",
    ],
    extras_require = {
        'docs': ["docutils>=0.4", "pudge>=0.1", "buildutils>=0.1.1", "kid>=0.7"],
    },
    entry_points="""
    [paste.global_paster_command]
    authkit=authkit.commands:SecurityCommand
    """,
)
