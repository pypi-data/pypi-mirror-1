from paste.script import templates

class TeslaTemplate(templates.Template):
    egg_plugins = ['Elixir', 'Tesla', 'Migrate']
    required_templates = ['pylons']
    _template_dir = 'templates/default'
    summary = 'Pylons+Elixir template'

class TeslaAuthTemplate(templates.Template):
    egg_plugins = ['TeslaAuth', 'AuthKit']
    required_templates = ['tesla']
    _template_dir = 'templates/auth'
    summary = 'Pylons+Elixir+AuthKit template'
