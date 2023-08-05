from paste.script.command import Command
import os
import glob
from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp
from paste.script import pluginlib, copydir

class SecurityCommand(Command):
    summary = "Add Security Facilities"
    usage = 'SECURE_CONTROLLER_NAME'
    
    parser = Command.standard_parser(simulate=True)
    
    min_args = 0
    max_args = 0
    group_name = 'pylons'

    def command(self):
        try:
            self.verbose = 3
            fo = FileOp(source_dir=os.path.dirname(__file__) + '/templates/pylons'.replace('/',os.sep))
            #try:
            #    name, dir = fo.parse_path_name_args(self.args[0])
            #except:
            #    raise BadCommand('No egg_info directory was found')
            fo.copy_file(
                template='security.py_tmpl',
                dest='controllers', 
                filename='security.py',
                add_py = False,
            )
            fo.ensure_dir('templates/security')
            for file in [
                'alreadyin.myt',
                'alreadyout.myt',
                'signedin.myt',
                'signedout.myt',
                'signin.myt',
            ]:
                fo.copy_file(
                    template=file,
                    dest='templates/security', 
                    filename=file,
                    add_py = False,
                )
        except:
            import sys
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error ocurred, %s'%msg)
