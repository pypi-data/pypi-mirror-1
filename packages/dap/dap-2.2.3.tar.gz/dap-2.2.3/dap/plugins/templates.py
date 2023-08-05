import os

from paste.script import templates

class DapPluginTemplate(templates.Template):

    summary = "A DAP plugin"
    
    egg_plugins = ['dap[server]']
    required_templates = ['basic_package']
    _template_dir = 'paster_templates'
    use_cheetah = True

    def post(self, command, output_dir, vars):
        for prereq in ['dap[server]']:
            command.insert_into_file(
                os.path.join(output_dir, 'setup.py'),
                'Extra requirements',
                '%r,\n' % prereq,
                indent=True)
        command.insert_into_file(
            os.path.join(output_dir, 'setup.py'),
            'Entry points',
            ('      [dap.plugin]\n'
             '      main = %(package)s.plugin\n') % vars,
            indent=False)

