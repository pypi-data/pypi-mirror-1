from paste.deploy import loadapp

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup sandbox here.
    """    
    app = loadapp('config:' + filename)
    from projectname import model as model
    model.connect()
