#!/usr/bin/python

from migrate.versioning.shell import main 
from turbogears import config
from turbogears.command.base import CommandWithDB

class MigrateCommand(CommandWithDB):
    """Make project to a Stand Alone Application
    """

    desc = "Make the sqlalchemy migration"
    need_project = True
    
    def __init__(self,*args, **kwargs):
        self.find_config()
        self.name = "migration"
        if config.get("sqlalchemy.dburi"):
            self.dburi = config.get("sqlalchemy.dburi")
        else:
            print "you shold set sqlalchemy dburi in config first"
            
    def run(self):
        print "The repository is %s\nThe dburi is in %s"%(self.name, self.dburi)
        main(url=self.dburi,repository=self.name, name=self.name)
          
        
