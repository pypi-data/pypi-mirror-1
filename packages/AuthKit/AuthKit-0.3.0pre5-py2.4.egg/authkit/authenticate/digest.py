"""\
HTTP digest authentication middleware

This implementation is identical to the `paste.auth.digest
<http://pythonpaste.org/module-paste.auth.digest.html>`_ implemenation.
"""
from paste.auth.digest import middleware
from paste.auth.digest import digest_password

