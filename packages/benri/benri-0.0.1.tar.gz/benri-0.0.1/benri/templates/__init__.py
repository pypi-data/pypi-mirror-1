from paste.script import templates

class BenriTemplate(templates.Template):
    summary = 'Default benri service on the web.'
    _template_dir = 'benri'
    egg_plugins = ['benri']
