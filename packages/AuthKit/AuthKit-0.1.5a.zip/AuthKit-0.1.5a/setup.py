from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
#from pylons import finddata

setup(
    name="AuthKit",
    version='0.1.5a',
    description='A complete autentication and authorisation system.',
    long_description="""
A complete autentication and authorisation system.

This is a bugfix release for the old 0.1 branch. You should really
use the latest 0.2 branch which is completely different.
""",
    license = 'MIT',
    author='James Gardner',
    author_email='james@pythonweb.org',
    url='http://pythonshq.com/',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    #package_data=finddata.find_package_data(),
    install_requires=[
        "Paste>=0.5",
        "FormBuild>=0.1.3",
        "FormEncode>=0.4",
        "SQLObject==dev,>=0.8dev",
    ],
    extras_require = {
        'Paste':["Paste>=0.5", "PasteDeploy>=0.5","PasteScript>=0.5",],
        'database': ["database>=0.6"],
        'SQLObject': ["SQLObject==dev,>=0.8dev"],
        'docs': ["docutils>=0.3.9", "pudge>=0.1", "buildutils>=0.1.1", "kid>=0.7"],
    },
    entry_points="""
    [paste.global_paster_command]
    authkit=authkit.commands:SecurityCommand
    """,
)