from paste.deploy import loadapp

def run(filename):
    "Write your commands here."    
    app = loadapp('config:' + filename)
    from projectname import model as model
    model.connect()
