from paste.script.templates import Template, var

class KSSPluginTemplate(Template):
    _template_dir = 'plugin'
    summary = 'KSS plugin template'
    egg_plugins = []
    vars = [
        var('namespace', 
            'The namespace for your plugin (something like `my-namespace`)'),
        ]

class KSSZopePluginTemplate(Template):
    _template_dir = 'zope_plugin'
    summary = 'KSS Zope plugin template'
    required_templates = ['kss_plugin']
