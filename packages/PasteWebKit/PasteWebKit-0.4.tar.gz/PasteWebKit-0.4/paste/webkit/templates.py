import os
from paste.script.templates import Template

class WebKit(Template):

    _template_dir = 'paster_templates/webkit'
    summary = "A Paste WebKit web application"

    egg_plugins = ['PasteWebKit']

    required_templates = ['PasteDeploy#paste_deploy']
    
    def post(self, command, output_dir, vars):
        fn = os.path.join(output_dir, 'setup.py')
        command.insert_into_file(
            fn, 'Entry points',
            'main = %s.wsgiapp:make_app\n' % vars['package'],
            True)
        command.insert_into_file(
            fn, 'Entry points',
            '[paste.app_factory]\n',
            True)
        
