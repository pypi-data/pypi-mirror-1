"""Pylons environment configuration"""
import os

from pylons import config

from authprojectname.config.routing import make_map
import authprojectname.lib.app_globals as app_globals
import authprojectname.lib.helpers

def load_environment(global_conf, app_conf):
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = {'root': root,
             'controllers': os.path.join(root, 'controllers'),
             'templates': [os.path.join(root, 'templates')],
             'static_files': os.path.join(root, 'public')
             }

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='authprojectname',
                    template_engine='mako', paths=paths)

    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = authprojectname.lib.helpers
    config['routes.map'] = make_map()

    # The template options
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override any
    # Pylons config options)
