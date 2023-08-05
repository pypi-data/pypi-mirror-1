import os
from paste.script.templates import Template

class Wareweb(Template):

    _template_dir = 'paster_templates/wareweb'
    summary = "A Wareweb web application"

    egg_plugins = ['Wareweb']

    required_templates = ['PasteDeploy#paste_deploy']
    
    def post(self, command, output_dir, vars):
        fn = os.path.join(output_dir, 'docs', 'devel_config.ini')
        if os.path.exists(fn) and not command.simulate:
            try:
                os.chmod(fn, 0111 | os.stat(fn).st_mode)
            except Exception, e:
                print "Could not make %s executable: %s" % (
                    fn, e)
            else:
                print "Run %s to start a development server" % fn

