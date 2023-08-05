from unittest import TestCase
import unittest
import pkg_resources
import os
pkg_resources.require('AuthKit')

class TestUsers(TestCase):
    
    def setUp(self):
        pass
    
    def test_01_applications_add_remove_exists(self):
        self.assertEqual(('default',), auth.applications())
        self.assertEqual(True, auth.application_exists('default'))
        self.assertEqual(False, auth.application_exists('trendy'))
        # None not allowed
        self.assertRaises(AuthError, auth.application_exists, None) 
        self.assertRaises(AuthError, auth.add_application, None)
        self.assertRaises(AuthError, auth.remove_application, None)
        # Can't delete default app
        self.assertRaises(AuthError, auth.remove_application, name='default') 
        # Adding applications
        self.assertEqual(None, auth.add_application(name='email'))
        self.assertEqual(('default','email'), auth.applications())
        # Application already exists
        self.assertRaises(AuthError, auth.add_application, name='default')
        self.assertRaises(AuthError, auth.add_application, name='email')
        # Remove Applications
        self.assertEqual(None, auth.remove_application(name='email'))
        self.assertEqual(('default',), auth.applications())

    def test_01_roles_add_remove_exists(self):
        self.assertEqual((), auth.roles())
        self.assertEqual(False, auth.role_exists('default'))
        # None not allowed
        self.assertRaises(AuthError, auth.role_exists, None)
        self.assertRaises(AuthError, auth.add_role, None)
        self.assertRaises(AuthError, auth.remove_role, None)
        # Adding roles
        self.assertEqual(None, auth.add_role(role='editor'))
        self.assertEqual(('editor',), auth.roles())
        self.assertEqual(None, auth.add_role(role='creator'))
        self.assertEqual(('editor', 'creator'), auth.roles())
        # Application already exists
        self.assertRaises(AuthError, auth.add_role, role='editor')
        # Remove Roles
        self.assertEqual(None, auth.remove_role(role='creator'))
        self.assertEqual(('editor',), auth.roles())
        
    def test_01_groups_add_remove_exists(self):
        self.assertEqual((), auth.groups())
        self.assertEqual(False, auth.group_exists('default'))
        # None not allowed
        self.assertRaises(AuthError, auth.group_exists, None)
        self.assertRaises(AuthError, auth.add_group, None)
        self.assertRaises(AuthError, auth.remove_group, None)
        # Adding roles
        self.assertEqual(None, auth.add_group(group='butcher'))
        self.assertEqual(('butcher',), auth.groups())
        self.assertEqual(None, auth.add_group(group='baker'))
        self.assertEqual(('butcher', 'baker'), auth.groups())
        # Application already exists
        self.assertRaises(AuthError, auth.add_group, group='butcher')
        # Remove Roles
        self.assertEqual(None, auth.remove_group(group='baker'))
        self.assertEqual(('butcher',), auth.groups())

    def test_03_add_user(self):
        self.assertRaises(AuthError, auth.add_user, username='james', firstname=None)
        self.assertRaises(TypeError, auth.add_user,  firstname='James')
        self.assertEqual(
            None, # XXX Could return the user object
            auth.add_user(username='james')
        )
        self.assertEqual('james', auth.user(username='james', property='username'))
        self.assertEqual('', auth.user(username='james', property='password'))
        self.assertEqual('', auth.user(username='james', property='firstname'))
        self.assertEqual('', auth.user(username='james', property='surname'))
        self.assertEqual(None, auth.user(username='james', property='group'))
        self.assertEqual(1, auth.user(username='james', property='active'))
        self.assertEqual(('james',), auth.users())
        self.assertEqual(('james',), auth.users(group=[]))
        self.assertEqual(('james',), auth.users(group=None))
        # @@: Should raise an AuthGroup error
        self.assertRaises(AuthError, auth.users, group='fire')
        self.assertEqual((), auth.users(active=0))
        self.assertEqual(('james',), auth.users(active=1))
        self.assertEqual(('james',), auth.users(active=None))
        self.assertEqual(('james',), auth.users(application=None))

    def test_04_add_user(self):
        self.assertEqual(None, auth.add_user(username='ian', password='bananas', firstname='Ian', surname='Smith', active=0))
        self.assertEqual('ian', auth.user(username='ian', property='username'))
        self.assertEqual('bananas', auth.user(username='ian', property='password'))
        self.assertEqual('Ian', auth.user(username='ian', property='firstname'))
        self.assertEqual('Smith', auth.user(username='ian', property='surname'))
        self.assertEqual(None, auth.user(username='ian', property='group'))
        self.assertEqual(0, auth.user(username='ian', property='active'))
        self.assertEqual(('ian','james'), auth.users())
        self.assertEqual(('ian','james'), auth.users(group=[]))
        self.assertEqual(('ian','james'), auth.users(group=None))
        # @@: Should raise an AuthGroup error
        self.assertRaises(AuthError, auth.users, group='fire')
        self.assertEqual(('ian',), auth.users(active=0))
        self.assertEqual(('james',), auth.users(active=1))
        self.assertEqual(('ian','james'), auth.users(active=None))
        self.assertEqual(('ian','james'), auth.users(application=None))

    def test_04_set_user(self):
        self.assertEqual(None, auth.add_user(username='andy'))
        auth.user('andy').firstname = 'Andy'
        self.assertEqual('Andy', auth.user('andy').firstname)
        auth.user('andy').surname = 'Blogs'
        self.assertEqual('Blogs', auth.user('andy').surname)
        auth.user('andy').password = 'Password'
        self.assertEqual('Password', auth.user('andy').password)
        auth._encryption = 'md5'
        auth.user('andy').password = 'Password'
        self.assertEqual('dc647eb65e6711e155375218212b3964', auth.user('andy').password)
        auth._encryption = None
        auth.add_group('andy_group')
        auth.user('andy').group = 'andy_group'
        self.assertEqual('andy_group', auth.user('andy').group)
        auth.user('andy').active = 0
        self.assertEqual(0, auth.user('andy').active)
        auth.remove_user('andy')
        
    def test_04_sr_groups(self):
        self.assertEqual(('butcher', 'andy_group'), auth.groups())
        auth.add_user('andy')
        auth.user('andy').group = 'andy_group'
        # XXX
        auth.user('james').group = 'butcher'
        # XXX
        auth.user('ian').group = 'butcher'
        self.assertEqual('andy_group', auth.user('andy').group)
        self.assertEqual(('andy','ian', 'james'), auth.users())
        self.assertEqual(('andy',), auth.users(group='andy_group'))
        auth.remove_group('andy_group', remove_users=True)
        
    def test_05_users_simple(self):
        self.assertEqual(('ian','james'), auth.users())
        self.assertRaises(AuthError, auth.users, role={})
        self.assertRaises(AuthError, auth.users, application={})
        self.assertRaises(AuthError, auth.users, group={})
        self.assertRaises(AuthError, auth.users, active={})
        # @@: Why not have username, password etc here too?
        # Test Roles
        self.assertRaises(AuthError, auth.users, role='fire')
        self.assertEqual(('ian', 'james'), auth.users(role=None))
        self.assertEqual((), auth.users(role='editor'))
        self.assertEqual(None, auth.add_role(role='deleter'))
        self.assertEqual((), auth.users(role='deleter'))
        # Test Applications
        self.assertRaises(AuthError, auth.users, application='fire')
        self.assertEqual(('ian', 'james'), auth.users(application=None))
        self.assertEqual((), auth.users(application='default'))
        self.assertEqual(None, auth.add_application(name='email'))
        self.assertEqual((), auth.users(application='email'))

    def test_06_users_active_1(self):
        # Test Roles
        self.assertEqual(('james',), auth.users(role=None, active=1))
        self.assertEqual((), auth.users(role='editor', active=1))
        self.assertEqual((), auth.users(role='deleter', active=1))
        # Test Applications
        self.assertEqual(('james',), auth.users(application=None, active=1))
        self.assertEqual((), auth.users(application='default', active=1))
        self.assertEqual((), auth.users(application='email', active=1))
        
    def test_06_users_active_0(self):
        # Test Roles
        self.assertEqual(('ian',), auth.users(role=None, active=0))
        self.assertEqual((), auth.users(role='editor', active=0))
        self.assertEqual((), auth.users(role='deleter', active=0))
        # Test Applications
        self.assertEqual(('ian',), auth.users(application=None, active=0))
        self.assertEqual((), auth.users(application='default', active=0))
        self.assertEqual((), auth.users(application='email', active=0))
        
    def test_06_users_active_None(self):
        # Test Roles
        self.assertEqual(('ian','james'), auth.users(role=None, active=None))
        self.assertEqual((), auth.users(role='editor', active=None))
        self.assertEqual((), auth.users(role='deleter', active=None))
        # Test Applications
        self.assertEqual(('ian', 'james'), auth.users(application=None, active=None))
        self.assertEqual((), auth.users(application='default', active=None))
        self.assertEqual((), auth.users(application='email', active=None))

    def test_07_set_roles_role(self, active=None):

        self.assertEqual(('ian', 'james'), auth.users())
        self.assertEqual(('editor', 'deleter'), auth.roles())
        self.assertEqual(('default', 'email'), auth.applications())
        
        self.assertEqual({}, auth.user('james').roles)
        self.assertEqual(None, auth.set_role('james', role='editor'))
        self.assertEqual({'default':('editor',)}, auth.user('james').roles)
        self.assertEqual(('ian','james'), auth.users(role=None, active=active))
        self.assertEqual(('james',), auth.users(role='editor', active=active))
        self.assertRaises(AuthError, auth.unset_role,'james', role='fire')
        self.assertEqual(None, auth.unset_role('james', role='editor'))
        self.assertEqual({}, auth.user('james').roles)
        
        self.assertEqual(None, auth.set_role('james', role='editor'))
        self.assertEqual(None, auth.set_role('james', role='deleter'))
        self.assertEqual(None, auth.set_role('ian', role='editor'))
        self.assertEqual({'default':('editor','deleter')}, auth.user('james').roles)
        self.assertEqual({'default':('editor',)}, auth.user('ian').roles)
        self.assertEqual(('ian','james'), auth.users(role=None, active=active))
        self.assertEqual(('ian','james'), auth.users(role='editor', active=active))
        self.assertEqual(('james',), auth.users(role='deleter', active=active))
        self.assertEqual(None, auth.unset_role('james', role='editor'))
        self.assertEqual({'default':('deleter',)}, auth.user('james').roles)
            
    def test_08_set_roles_application(self, active=None):
        
        group = []
        self.assertEqual(('ian', 'james'), auth.users(active=active, group=group))
        self.assertEqual(('editor', 'deleter'), auth.roles())
        self.assertEqual(('default', 'email'), auth.applications())

        self.assertEqual(None, auth.unset_all_roles('james'))
        self.assertEqual({}, auth.user('james').roles)
        self.assertEqual(None, auth.unset_all_roles('ian'))
        self.assertEqual({}, auth.user('ian').roles)
        # No Role specified
        self.assertRaises(TypeError, auth.set_role,'james', application='email')
        
        self.assertEqual(None, auth.set_role('james', application='email', role='editor'))
        self.assertEqual({'email':('editor',)}, auth.user('james').roles)
        self.assertEqual(None, auth.unset_role('james', application='email', role='editor'))
        self.assertEqual({}, auth.user('james').roles)
        
        self.assertEqual(None, auth.set_role('ian', application='email', role='editor'))
        self.assertEqual(None, auth.set_role('ian', application='email', role='deleter'))
        self.assertEqual(None, auth.set_role('james', application='email', role='editor'))

        self.assertEqual({'email':('editor','deleter')}, auth.user('ian').roles)
        self.assertEqual({'email':('editor',)}, auth.user('james').roles)
            
        self.assertEqual(('ian','james'), auth.users(application='email', role='editor', active=active, group=group))
        self.assertEqual(('ian',), auth.users(application='email', role='deleter', active=active, group=group))
        
        group = None
        self.assertEqual('butcher', auth.user('james').group)
        self.assertEqual('butcher', auth.user('ian').group)
        self.assertEqual({'email': ('editor',)}, auth.user('james').roles)
        self.assertEqual({'email':('editor','deleter')}, auth.user('ian').roles)
        self.assertEqual((), auth.users(active=active, group=group))
        self.assertEqual((), auth.users(application='email', role='editor', active=active, group=group))
        
        group = 'butcher'
        self.assertEqual(('ian','james'), auth.users(application='email', role='editor', active=active, group=group))
        self.assertEqual(('ian',), auth.users(application='email', role='deleter', active=active, group=group))

        #
        # XXX Need better users()* tests.
        #

        
        #~ print auth.sign_out(username='ian')
        #~ # 0
        #~ print auth.user(username='ian')['active']
        #~ # False
        #~ print auth.user(username='ian')['history']
        #~ # []
        #~ print auth.user(username='ian')['roles']
        #~ #{'email': ('editor', 'deleter')}
        #~ print auth.authorise(username='ian', signed_in=1)
        #~ print auth.authorise(username='ian', signed_in=0)
        # Fasle
        
        # NB, an application returns true when you authorise even with no role associated with it.

        results = [
            #  0 username=ian, active=None, group=[], application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  1 username=ian, active=None, group=[], application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  2 username=ian, active=None, group=[], application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  3 username=ian, active=None, group=[], application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  4 username=ian, active=None, group=[], application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  5 username=ian, active=None, group=[], application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  6 username=ian, active=None, group=[], application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  7 username=ian, active=None, group=[], application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  8 username=ian, active=None, group=[], application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  9 username=ian, active=None, group=[], application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            True,
            #  10 username=ian, active=None, group=[], application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            True,
            #  11 username=ian, active=None, group=[], application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            
            #  12 username=ian, active=None, group=butcher, application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  13 username=ian, active=None, group=butcher, application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  14 username=ian, active=None, group=butcher, application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  15 username=ian, active=None, group=butcher, application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  16 username=ian, active=None, group=butcher, application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  17 username=ian, active=None, group=butcher, application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  18 username=ian, active=None, group=butcher, application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            
            # Haven't checked these ones onwards XXX
            
            #  19 username=ian, active=None, group=butcher, application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  20 username=ian, active=None, group=butcher, application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  21 username=ian, active=None, group=butcher, application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            True,
            #  22 username=ian, active=None, group=butcher, application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            True,
            #  23 username=ian, active=None, group=butcher, application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  24 username=ian, active=0, group=[], application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  25 username=ian, active=0, group=[], application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  26 username=ian, active=0, group=[], application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  27 username=ian, active=0, group=[], application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  28 username=ian, active=0, group=[], application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  29 username=ian, active=0, group=[], application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  30 username=ian, active=0, group=[], application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  31 username=ian, active=0, group=[], application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  32 username=ian, active=0, group=[], application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  33 username=ian, active=0, group=[], application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            True,
            #  34 username=ian, active=0, group=[], application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            True,
            #  35 username=ian, active=0, group=[], application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  36 username=ian, active=0, group=butcher, application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  37 username=ian, active=0, group=butcher, application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  38 username=ian, active=0, group=butcher, application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  39 username=ian, active=0, group=butcher, application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  40 username=ian, active=0, group=butcher, application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  41 username=ian, active=0, group=butcher, application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  42 username=ian, active=0, group=butcher, application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            True,
            #  43 username=ian, active=0, group=butcher, application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            True,
            #  44 username=ian, active=0, group=butcher, application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  45 username=ian, active=0, group=butcher, application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            True,
            #  46 username=ian, active=0, group=butcher, application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            True,
            #  47 username=ian, active=0, group=butcher, application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  48 username=ian, active=1, group=[], application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            False,
            #  49 username=ian, active=1, group=[], application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            False,
            #  50 username=ian, active=1, group=[], application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  51 username=ian, active=1, group=[], application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  52 username=ian, active=1, group=[], application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  53 username=ian, active=1, group=[], application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  54 username=ian, active=1, group=[], application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            False,
            #  55 username=ian, active=1, group=[], application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            False,
            #  56 username=ian, active=1, group=[], application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  57 username=ian, active=1, group=[], application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  58 username=ian, active=1, group=[], application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  59 username=ian, active=1, group=[], application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  60 username=ian, active=1, group=butcher, application=default, role=None, signed_in=None, idle_max=None, session_max=None,
            False,
            #  61 username=ian, active=1, group=butcher, application=default, role=None, signed_in=0, idle_max=None, session_max=None,
            False,
            #  62 username=ian, active=1, group=butcher, application=default, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  63 username=ian, active=1, group=butcher, application=default, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  64 username=ian, active=1, group=butcher, application=default, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  65 username=ian, active=1, group=butcher, application=default, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
            #  66 username=ian, active=1, group=butcher, application=email, role=None, signed_in=None, idle_max=None, session_max=None,
            False,
            #  67 username=ian, active=1, group=butcher, application=email, role=None, signed_in=0, idle_max=None, session_max=None,
            False,
            #  68 username=ian, active=1, group=butcher, application=email, role=None, signed_in=1, idle_max=None, session_max=None,
            False,
            #  69 username=ian, active=1, group=butcher, application=email, role=editor, signed_in=None, idle_max=None, session_max=None,
            False,
            #  70 username=ian, active=1, group=butcher, application=email, role=editor, signed_in=0, idle_max=None, session_max=None,
            False,
            #  71 username=ian, active=1, group=butcher, application=email, role=editor, signed_in=1, idle_max=None, session_max=None,
            False,
        ]

        counter = 0
        for username in ['ian']:
            for active in [None, 0, 1]:
                for group in [[], 'butcher']:
                    for application in ['default', 'email']:
                        for role in [None, 'editor']:
                            for signed_in in [None, 0, 1]:
                                #for idle_max in [None, 10]:
                                 #   for session_max in [None, 10]:
                                session_max = None
                                idle_max = None
                                
                                self.assertEqual(results[counter],auth.authorise(username, active=active, group=group, application=application, role=role, signed_in=signed_in, idle_max=idle_max, session_max=session_max)) 
                                #print '# ', counter, 'username=%s,'%username, 'active=%s,'%active, 'group=%s,'%group, 'application=%s,'%application, 'role=%s,'%role, 'signed_in=%s,'%signed_in, 'idle_max=%s,'%idle_max, 'session_max=%s,'%session_max
                                #print '%s,'%auth.authorise(username, active=active, group=group, application=application, role=role, signed_in=signed_in, idle_max=idle_max, session_max=session_max)
                                counter += 1

        # Test session_max
        # Test idle_max
        # XXX Tested in example rather than in this test file.

        # Test history stuff
        # XXX Tested in example rather than in this test file.
        
        # Test sign in sign out
        # XXX Tested in example rather than in this test file.
        
        # Test delete roles/users etc
        
        
if __name__ == '__main__':

    path = os.getcwd()+'/'+'test.db'
    try:
        os.remove(path)
    except OSError:
        pass
    from authkit import SQLObjectAuthStore, connectionForURI, AuthError
    auth = SQLObjectAuthStore(connection=connectionForURI('sqlite:///'+path.replace(':','|').replace('\\','/')))
    auth.create_store()

    suite = [unittest.makeSuite(TestUsers)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
