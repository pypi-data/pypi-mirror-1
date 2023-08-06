import os
import logging
from mercurial import commands, ui, hg

def get_repository(location):
	return hg.repository(ui.ui(), location)

class Recipe(object):
	
	def __init__(self, buildout, name, options):
		self.options = options
		self.options.setdefault('location', os.path.join(buildout.get('buildout').get('parts-directory'), name))
		self.source = self.options.get('repository')
		self.destination = self.options.get('location')
		self.newest = options.get('newest', buildout.get('buildout').get('newest', 'true')).lower() != 'false'
		self.log = logging.getLogger(name)
	
	def install(self):
		self.log.info("Cloning repository %s to %s" % (self.source, self.destination))
		commands.clone(ui.ui(), get_repository(self.source), self.destination)
		return self.destination
	
	def update(self):
		if self.newest:
			self.log.info("Pulling repository %s and updating %s" % (self.source, self.destination))
			commands.pull(ui.ui(), get_repository(self.destination), self.source, update = True)
