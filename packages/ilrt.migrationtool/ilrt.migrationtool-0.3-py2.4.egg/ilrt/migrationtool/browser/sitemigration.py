# Migration class with general utility migration methods
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory

from ilrt.migrationtool.browser.interfaces import ISiteMigration

class SiteMigrationFactory:
    """This factory instantiates new migrations and
       registers them against the migration tool
    """
    implements(IFactory)

    title = u"Create and register a new site migration"
    description = u"This factory instantiates new migrations and \
                      registers them against the migration tool"

    def __call__(self):
        migration = SiteMigration()
        portal = getUtility(ISiteRoot)
        sm_tool = getToolByName(portal, 'site_migration')
        if getattr(sm_tool,'migrations'):
            sm_tool.migrations.append(migration)
        else:
            sm_tool.migrations = [migration,]
        migration.tool = sm_tool
        return migration

    def getInterfaces(self):
        return implementedBy(SiteMigration)

class SiteMigration:
    """ Use this class but override and add methods as required """

    implements(ISiteMigration)

    def upgrade(self,portal):
        """ 1 upgrade to 2 for example """
        out = []
        return out

    def downgrade(self, portal):
        """ 2 downgrade to 1 for example """
        out = []
        return out

    def methods(self, **kwargs):
        """ Add all the migration methods and register
            the upgrade and downgrade
        """
        for key in kwargs.keys():
            try:
                setattr(self,key,kwargs[key])
            except:
                pass
            
        if not self.versions:
            self.versions = ('0.1','0.2')
        if not self.migration:
            self.migration = 1

        if hasattr(self,'upgrade'):
            self.tool.registerUpgradePath(self.versions[0],
                                          self.versions[1],
                                          self.upgrade)
        if hasattr(self,'downgrade'):                
            self.tool.registerDowngradePath(self.versions[1],
                                            self.versions[0],
                                            self.downgrade)
        
