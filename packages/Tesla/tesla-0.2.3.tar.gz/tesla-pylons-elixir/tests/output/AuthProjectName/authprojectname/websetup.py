from paste.deploy import loadapp

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup authprojectname here.
    """    
    app = loadapp('config:' + filename)
    from authprojectname import models as model
    model.connect()
