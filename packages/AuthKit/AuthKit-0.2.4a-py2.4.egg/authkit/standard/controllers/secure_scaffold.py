from authkit.standard.controllers.secure import SecureController 
from scaffold.standard.controllers.simple import *
import formbuild
from pylons import params, m, request, c
from authkit.standard.permissions import * 


class Secure_ScaffoldController(SecureController, SimpleScaffoldController):

    def __call__(self, **params):
        
        sqlalchemy.global_connect(request.environ['paste.config']['app_conf']['dsn'])
        sqlalchemy.objectstore.clear()
        
        # Needed from SimpleScaffoldController
        t = {}
        for k,v in request.params.items():
            t[k] = v[0]
        c.params = t
        # End needed
        
        SecureController.__call__(self, **params)
        sqlalchemy.objectstore.flush()
        
    def __before__(self, action):
        if not self.admin_permissions():
            h.log('\n'.join(self.admin_permissions.errors))
            m.abort(404)
        else:
            raise Exception('__before__ should be called in the derived class, taking care to check permissions')
    
            
        #~ c.model = self.model
        #~ c.name = 'User'
        #~ c.table = getattr(c.model,c.name).mapper.table.name
        #~ c.template = '/scaffold/templates/standard/'
        #~ c.exclude = ['active', 'uid']
        #~ c.foreign_key_values = {
            #~ 'group': [tuple([x.uid, x.name]) for x in c.model.Group.mapper.select()]
        #~ }
        #~ c.foreign_key_lookup = {
            #~ 'group': Lookup(c.model.Group, 'uid', 'name')
        #~ }
        #~ c.form = formbuild.Form()