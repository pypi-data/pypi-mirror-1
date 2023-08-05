from paste.deploy import loadapp

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup sandbox here.
    """    
    app = loadapp('config:' + filename)
    from projectname import models as model
    model.connect()
    newsitem = model.NewsItem(title = 'Sample', content='OK')
    newsitem.flush()
