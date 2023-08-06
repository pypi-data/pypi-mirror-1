import os

from paste.script import templates, pluginlib


# Monkeypatch pluginlib
def egg_info_dir(base_dir, dist_name):
    return os.path.join(base_dir, 'dap.plugins.%s.egg-info' % pluginlib.egg_name(dist_name)) 
pluginlib.egg_info_dir = egg_info_dir


class DapPluginTemplate(templates.Template):

    summary = "A DAP plugin"
    
    egg_plugins = ['dap[server]']
    _template_dir = 'paster_templates'
    use_cheetah = True

    def post(self, command, output_dir, vars):
        for prereq in ['dap[server]>=2.2.4']:
            command.insert_into_file(
                os.path.join(output_dir, 'setup.py'),
                'Extra requirements',
                '%r,\n' % prereq,
                indent=True)
        command.insert_into_file(
            os.path.join(output_dir, 'setup.py'),
            'Entry points',
            ('      [dap.plugin]\n'
             '      main = dap.plugins.%(package)s\n') % vars,
            indent=False)
