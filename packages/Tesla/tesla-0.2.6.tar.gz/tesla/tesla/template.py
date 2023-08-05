from paste.script import templates

class TeslaTemplate(templates.Template):
    egg_plugins = ['Tesla', 'Elixir']
    required_templates = ['pylons']
    _template_dir = 'templates/default'
    summary = 'Pylons+Elixir template'

class TeslaAuthTemplate(templates.Template):
    required_templates = ['tesla']
    _template_dir = 'templates/auth'
    summary = 'Tesla + authentication'

class TeslaAuthXpTemplate(templates.Template):
    required_templates = ['tesla_auth']
    _template_dir = 'templates/auth_xp'
    summary = 'Tesla + row-level authentication (experimental)'


