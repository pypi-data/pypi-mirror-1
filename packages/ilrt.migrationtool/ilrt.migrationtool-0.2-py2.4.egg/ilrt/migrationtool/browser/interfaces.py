from zope import interface

class IWorkflowMigrationView(interface.Interface):
    """
    Migrates content from one workflow to another via a manually
    tailored mapping implemented as an adjunct to the site migration tool
    """

    def listWorkflows(self):
        """ Return a list of id,title dictionarys for the workflows available
        """

    def setWorkflowMigration(self,wf_from,wf_to):
        """
        Set the worflows for the migration
        """

    def getWorkflowMigration(self):
        """
        Generate the state mapping data for transferring one
        workflow's states to the others
        """


class ISiteMigrationTool(interface.Interface):
    """Handles migrations between released sites. Adds methods to Plones core IMigrationTool
       Requires a theme egg or other third party product to hold the actual release migrations
    """

    def setMigration(self, migration_id):
        """ Set the migration object whose method is to be to run individually """

    def getMigrationMethods(self):
        """ List all the methods for a particular migration object """

    def runMigrationMethod(self,method):
        """ Run an individual method from a migration object """

    def registerUpgradePath(self, oldversion, newversion, function):
        """ Basic register func """

    def registerDowngradePath(self, oldversion, newversion, function):
        """ Basic register func """

    def getEgg():
        ''' Return egg or product id that contains migrations used '''

    def getExtensionContext():
        ''' Return extension profile that contains migrations used '''
        
    def setExtensionContext(context_id):
        ''' Set extension profile that contains migrations used
            At this point look up installed instance version if its in quickinstaller
        '''        

    def loadMigrations():
        ''' Search for migrations based on profile/migration naming convention '''

    def om_icons():
        ''' Exclamation icon if the site is not up to date '''

    def needDowngrading(self):
        """ Need downgrading? """

    def _migrate(version, dirn = "up"):
        """ Run the migration """
        
    def _upgrade(version):
        """ Run _migrate with dirn up """
        

class ISiteMigration(interface.Interface):
    """ The migration itself that calls utility methods e.g. to run generic setup files,
        install products etc. Or can run any bespoke methods if desired
    """

    migration = interface.Attribute("migration")
    versions = interface.Attribute("versions")

    def upgrade():
        """ Upgrade from 1 to 2 """

    def downgrade():
        """ Downgrade from 2 to 1 """
