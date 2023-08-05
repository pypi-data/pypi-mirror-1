from paste.deploy import loadapp

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup authxpprojectname here.
    """    
    app = loadapp('config:' + filename)
    from authxpprojectname import model as model
    model.connect()
