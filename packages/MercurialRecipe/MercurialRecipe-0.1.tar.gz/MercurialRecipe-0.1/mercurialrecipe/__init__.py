import os
import logging
from mercurial import commands, ui, hg, repo

def get_repository(location):
	if '://' not in location and not os.path.exists(location):
		return VirtualRepo(location)
	return hg.repository(ui.ui(), location)

class VirtualRepo(repo.repository):
	
	def __init__(self, path):
		self.path = "file:/%s" % path
	
	def url(self):
		return self.path

class Recipe(object):
	
	def __init__(self, buildout, name, options):
		self.options = options
		self.options.setdefault('location', os.path.join(buildout.get('buildout').get('parts-directory'), name))
		self.source = get_repository(self.options.get('repository'))
		self.destination = get_repository(self.options.get('location'))
		self.newest = options.get('newest', buildout.get('buildout').get('newest', 'true')).lower() != 'false'
		self.log = logging.getLogger(name)
	
	def install(self):
		self.log.info("Cloning repository %s to %s" % (self.source.url(), self.destination.url()))
		commands.clone(ui.ui(), self.source, self.destination.url())
		self.destination = get_repository(self.destination.url())
		return self.options.get('location')
	
	def update(self):
		if self.newest:
			self.log.info("Pulling repository %s and updating %s" % (self.source.url(), self.destination.url()))
			commands.pull(ui.ui(), self.destination, self.source.url(), update = True)
