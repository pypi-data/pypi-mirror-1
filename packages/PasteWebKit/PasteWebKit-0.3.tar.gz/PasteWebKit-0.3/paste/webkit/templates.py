from paste.script.templates import Template

class WebKit(Template):

    _template_dir = 'paster_templates/webkit'
    summary = "A Paste WebKit web application"

    egg_plugins = ['PasteWebKit']

    required_templates = ['PasteDeploy#paste_deploy']
    
