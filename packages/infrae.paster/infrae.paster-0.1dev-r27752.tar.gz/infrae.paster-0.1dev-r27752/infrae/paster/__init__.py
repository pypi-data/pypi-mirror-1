## -*- coding: utf-8 -*-
############################################
## File : __init__.py<3>
## Author : Sylvain Viollon
## Email : sylvain@infrae.com
## Creation Date : Fri Feb 15 16:39:40 2008 CET
## Last modification : Fri Feb 22 18:11:57 2008 CET
############################################

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: __init__.py 27752 2008-02-22 17:15:52Z sylvain $"


from paste.script.create_distro import CreateDistroCommand
import os

class FalseOptions:
    """False option to paster.
    """
    simulate = False
    overwrite = True

class FalseCommand:
    """False paster-like command to make the template usable.
    """

    interactive = False
    simulate = False
    overwrite = True
    options = FalseOptions()

    def __init__(self, buildout):
        self.verbose = buildout['buildout'].get('verbosity', 0)

    def templates(self, name):
        templates = []
        command = CreateDistroCommand('infrae.paster')
        command.extend_templates(templates, name)
        return templates



class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        self.location = options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], self.name)

        self.command = FalseCommand(buildout)
        self.templates = self.command.templates(options['template'])
        
    def update(self):
        """Do nothing.
        """
        return self.location

    def install(self):
        """Install the paster template.
        """

        for _, template in self.templates:
            template.run(self.command, 
                         self.location, 
                         self.options)

        return self.location

