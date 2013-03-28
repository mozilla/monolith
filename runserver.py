from paste.deploy import loadapp

application = loadapp('config:monolith.ini', relative_to='.')
