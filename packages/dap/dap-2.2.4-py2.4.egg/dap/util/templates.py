import os

from paste.script import templates

class DapServerTemplate(templates.Template):

    summary = "A DAP server deployed through paste.deploy"
    
    egg_plugins = ['dap[server]']
    _template_dir = 'paster_templates'
    use_cheetah = True

    def post(self, command, output_dir, vars):
        if command.verbose:
            print '*'*72
            print '* Run "paster serve %s/server.ini" to run' % output_dir
            print '* the DAP server on http://localhost:8080'
            print '*'*72
