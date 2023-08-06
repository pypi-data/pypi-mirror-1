"""
 DrAdm1 utilities pack - www.dradm.org
 2009 (c) Axel <dev@axel.pp.ru>
 Under GPL v3
"""

import os, shutil
from subprocess import *
from utils import *


class ProjectError(Exception):
    """ Display errors.
    """
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg or "Operation error in the 'project' module." 

    def __str__(self):
        return self.msg


class Project:
    """ Work with projects.
    """
    def __init__(self, config, name=''):
        self.section = 'PROJECT'
        self.name = name
        self.base = config.get(self.section, 'base')

    @addactions
    def add(self):
        """ Add a new project.
        """
        try:
            os.mkdir(os.path.join(self.base, self.name))
            os.mkdir(os.path.join(self.base, self.name, 'tmp'))
            os.mkdir(os.path.join(self.base, self.name, 'bin'))
            os.mkdir(os.path.join(self.base, self.name, 'var'))
        except:
            raise ProjectError("Can't create the %s project." % self.name)

    def getname(self):
        """ Return name of the project.
        """
        return self.name
    
    def exists(self):
        """ Is the project exists?
        """
        return os.path.exists(os.path.join(self.base, self.name))

    def getpath(self):
        """ Get full project path.
        """
        return os.path.join(self.base, self.name)
        
    @addactions
    def drop(self):
        """ Remove the project with all data.
        """
        try:
            shutil.rmtree(os.path.join(self.base, self.name))
            err = False
        except:
            raise ProjectError("Can't delete the %s project." % self.name)
    
    def list_get(self):
        """ Return list of all projects.
        """
        return os.listdir(self.base)

    def list_print(self):
        """ Print list of all projects.
        """
        for fname in self.list_get():
            print fname

 
if __name__ == "__main__":
    """ Quick unit test
    """
    if not rootcheck():
        errexit("You need run this utility as root!")
    cfg = Config()
    test = Project(cfg, 'test1314')
    if test.add():
        print "Test project created."
    test.list_print()
    if test.drop():
        print "Test project deleted."

