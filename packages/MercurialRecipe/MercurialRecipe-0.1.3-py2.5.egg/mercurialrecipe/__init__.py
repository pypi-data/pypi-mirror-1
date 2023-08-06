"""
This recipe offers you an easy way to integration data from some Mercurial
repository into your buildout work-environment::

    [some_hg_dependency]
    recipe = mercurialrecipe
    repository = <REPOSITORY PATH/URL>

"""
import os
import shutil
import logging
from mercurial import commands, ui, hg


def get_repository(location):
    "Builds a Mercurial repository object out of the given location."
    return hg.repository(ui.ui(), location)


class Recipe(object):
    """
    This is the recipe itself, for details on how to use it,
    please take a look at the module documentation.
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.options.setdefault('location',
            os.path.join(buildout.get('buildout') \
                .get('parts-directory'), name))
        self.source = self.options.get('repository')
        self.destination = self.options.get('location')
        self.newest = options.get('newest',
            buildout.get('buildout') \
                .get('newest', 'true')).lower() != 'false'
        self.log = logging.getLogger(name)

    def install(self):
        """
        Does the actual installation of this part.

        Be aware, that if the part was previously installed, it will
        get removed.
        """
        self.log.info("Cloning repository %s to %s" % (
            self.source, self.destination
        ))
        shutil.rmtree(self.destination, ignore_errors = True)
        commands.clone(ui.ui(), get_repository(self.source), self.destination)
        return self.destination

    def update(self):
        """
        This method is run when a buildout environment should be updated. If
        the ``newest`` option is set, this will cause a pull from the upstream
        repository.
        """
        if self.newest:
            self.log.info("Pulling repository %s and updating %s" % (
                self.source, self.destination
            ))
            commands.pull(ui.ui(), get_repository(self.destination),
                    self.source, update = True)
