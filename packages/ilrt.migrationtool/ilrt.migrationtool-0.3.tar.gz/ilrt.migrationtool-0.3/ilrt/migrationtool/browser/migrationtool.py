from Globals import InitializeClass, package_home
import os, sys, traceback
from zope.interface import implements
from Products.CMFPlone.interfaces import IMigrationTool
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFPlone.MigrationTool import MigrationTool as BaseMTool
from distutils.version import LooseVersion
from Products.CMFCore.utils import getToolByName
import zLOG

from sets import Set
from zope.component import createObject
from zope.component import getUtility
from Products.Five.browser import BrowserView
from zope.app.publisher.interfaces.browser import IBrowserMenu

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.interfaces import ISiteRoot
from ilrt.migrationtool.browser.interfaces import ISiteMigrationTool
from ilrt.migrationtool.browser.workflowtool import WorkflowMigrationView
from ilrt.migrationtool.browser import utils

PRE_MIGRATION_RELEASE = "0.1"
MIGRATION_TOOL_TYPE = "Site Migration Tool"
MIGRATION_TOOL_ID = "site_migration"

class SiteMigrationView(BrowserView):
    ''' This allows for zcml config of the management screens for the tool '''

class SiteMigrationTool(BaseMTool):
    """Synchronises filesystem code across the Site theme egg
       with any necessary updates to the ZODB
    """

    implements(ISiteMigrationTool, IMigrationTool)

    id = MIGRATION_TOOL_ID
    meta_type = MIGRATION_TOOL_TYPE
    security = ClassSecurityInfo()

    manage_overview = PageTemplateFile('templates/migrationTool.pt',globals())

    def manage_options(self):
        """ Builds a zope2 style menu from the zope3 configure.zcml one
            NB: Beware an empty tuple causes inaccurate security error """
        if getattr(self,'options',()) == ():
            zope2menu = []
            menu = getUtility(IBrowserMenu, name='migrationtool_options')
            try:
                for item in menu.getMenuItems(self,getattr(self,'REQUEST',{})):
                    zope2menu.append({'label':item['title'],
                                 'action':str(item['action'])})
            except:
                pass
            self.options = tuple(zope2menu)
        return self.options
    
    def __init__(self):
        self.migrations = []
        self._upgradePaths = {}
        self._downgradePaths = {}
        self.migration_id = ''
        self.egg = ''
  
    def log(self,message,summary='',severity=0):
        zLOG.LOG('Site (MigrationTool): ', severity, summary, message)

    def _logErrorOut(self, out, handle='raise'):
        """ Make migration messages loggable or raisable """
        errmsgs = ''
        for msg in out:
            if msg.startswith('Error:'):
                if handle=='log':
                    errmsgs += msg
                else:
                    self.log(msg,'ilrt.migrationtool error',1)
        if errmsgs and handle == 'raise':
               raise errmsgs

    def setMigration(self, migration_id):
        """ Set the migration object whose method
            is to be to run individually """
        self.migration_id = migration_id

    def getMigrationMethods(self):
        """ List all the methods for a particular migration object """
        methods = []
        if not self.migration_id:
            return methods
        else:
            for m in self.migrations:
                if m.migration == self.migration_id:
                    attribs = [me for me in dir(m) if not me.startswith('__')]
                    for attrib in attribs:
                        # if type(attrib) != StringType:
                        methods.append(attrib)
            return methods

    def runMigrationMethod(self,method):
        """ Run an individual method from a migration object """
        portal = getUtility(ISiteRoot)
        for m in self.migrations:
            if m.migration == self.migration_id:
                me = getattr(m,method,None)
                if me:
                    try:
                        out = str(me(portal))
                    except:
                        out = str(me) + str(Error)
                    return out

    def registerUpgradePath(self, oldversion, newversion, function):
        """ Basic register func """
        self._upgradePaths[oldversion.lower()] = [newversion.lower(),
                                                  function]

    def registerDowngradePath(self, oldversion, newversion, function):
        """ Basic register func """
        self._downgradePaths[oldversion.lower()] = [newversion.lower(),
                                                    function]

    def getEgg(self):
        ''' Return egg or product id that contains migrations used '''
        return getattr(self,'egg','')

    def getExtensionContext(self):
        ''' Return extension profile that contains migrations used '''
        if hasattr(self,'extension'):
            return self.extension
        else:
            return ''
        
    def setExtensionContext(self,context_id):
        ''' Set extension profile that contains migrations used
            At this point look up installed instance version
            if its in quickinstaller
        '''
        if context_id:
            self.egg = str(context_id)
        if self.egg:
            qitool = getToolByName(self, 'portal_quickinstaller')            
            for prod in qitool.listInstalledProducts():
                if prod['id'] == self.egg:
                    self.setInstanceVersion(prod['installedVersion'])
            self.extension = 'profile-' + self.egg + ':default'
            out = ["Instance initialised to new product %s" % self.egg,]
            out.extend(self.loadMigrations(reload=1))
        return self.manage_overview(self, out=out)

    def loadMigrations(self, reload=0):
        ''' Search for sitemigrations in the specified egg '''
        out = [] 
        if not self.egg:
            return out
        if reload or not getattr(self,'migrations',None):
            self.migrations = []
            try:
                exec('from ' + self.egg + ' import migrations')
            except ImportError:
                out.append("Error: Sorry this egg, " + str(self.egg) + ", has no migrations \
                    - please add a migrations folder with migration scripts in")
                return out
            except:
                errlines = traceback.format_exc().split('File')
                out.append('Error: Your migration scripts caused a fatal error please correct it')
                out.append('TRACEBACK ...')
                if len(errlines)>3:
                    errlines = errlines[3:]
                for err in errlines:
                    out.append(err)
                return out
            migrationlist = [m for m in dir(migrations) \
                                if not m.startswith('__')]
            if not migrationlist:
                out.append("Error: the migrations folder has no initialized \
                            migrations - check you have added them in the init")  
            util_methods = dir(utils)
            for m in migrationlist:
                migration = getattr(migrations,m)
                methodlist = [me for me in dir(migration) \
                                 if not me.startswith('__')]
                methodlist = list(set(methodlist) - set(util_methods))
                if 'VERSIONS' in methodlist:
                    if 'upgrade' in methodlist:
                        mig = createObject(u"SiteMigration")
                        mig.migration = m
                        mig.versions = migration.VERSIONS
                        methods = {}
                        # Unpicklable objects could be returned which we skip
                        for me in methodlist:
                            try:
                                methods[me] = getattr(migration,me,None)
                            except:
                                pass
                        try:
                            mig.methods(**methods)
                        except:
                            pass
                        out.append('Added migration ' + m)
                    else:
                        out.append("Error: Sorry migration script '" + m + \
                                   "' has no upgrade function please add \
                                   one ie. def upgrade(self, portal):")
                else:
                    out.append("Error: Sorry migration script '" + m + \
                                   "' has no VERSIONS please add one \
                                    ie. VERSIONS = ('1','2')")
        if self.migrations:
            for migration in self.migrations:
                self.registerUpgradePath(migration.versions[0],
                                         migration.versions[1],
                                         migration.upgrade)
                self.registerDowngradePath(migration.versions[1],
                                           migration.versions[0],
                                           migration.downgrade)
        else:
            out.append('Error: Sorry no migrations found')
        return out

    def getFileSystemVersion(self):
        """ The version this instance of the theme egg is on """
        fs_v = PRE_MIGRATION_RELEASE
        egg = getattr(self,'egg',None)
        if egg:
            cp = self.Control_Panel.Products
            eggobj = getattr(cp,egg,None)
            if eggobj:
                fs_v = eggobj.version.lower()

        return fs_v

    security.declareProtected(ManagePortal, 'needMigrating')
    def needMigrating(self):
        """ Need migrating? """

        return self.needUpgrading() or self.needDowngrading() or False


    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? Will enforce strict version numbering """

        fs_v = LooseVersion(self.getFileSystemVersion())
        z_v = LooseVersion(self.getInstanceVersion())

        return fs_v > z_v

    security.declareProtected(ManagePortal, 'needDowngrading')
    def needDowngrading(self):
        """ Need downgrading? Will enforce strict version numbering """
        
        fs_v = LooseVersion(self.getFileSystemVersion())
        z_v = LooseVersion(self.getInstanceVersion())

        return fs_v < z_v

    security.declareProtected(ManagePortal, 'coreVersions')
    def coreVersions(self):
        """ Useful core information """
        vars = {}
        vars['Site Instance'] = self.getInstanceVersion()
        vars['Site File System'] = self.getFileSystemVersion()
        return vars

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version ids, except current one """
        current_version = self.getInstanceVersion()
        if not self._upgradePaths.keys():
            self._logErrorOut(out=self.loadMigrations(reload=1))
        versions = [LooseVersion(x) for x in \
                  Set(self._upgradePaths.keys() + self._downgradePaths.keys()) \
                  if x != current_version]
        versions.sort()
        return versions

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of plone is on """
        self._version = version
        return self.manage_results(self,
               out=(("Instance initialised to version %s" % version,
                     zLOG.INFO),))

    def _migrate(self, version, dirn = "up"):
        """ Run the migration """
        
        assert dirn in ("up", "down")

        path_dict = self._upgradePaths
        if dirn == "down":
              path_dict = self._downgradePaths

        version = version.lower()
        if not path_dict.has_key(version):
            return None, ("Migration completed at version %s" % version,)
               
        newversion, function = path_dict[version]
        res = function(self.aq_parent)
        return newversion, res

    def _upgrade(self, version):
        """ Run the migration as an upgrade """
        
        version = version.lower()

        if self.needDowngrading():
            return self._migrate(version, "down")
        
        if not self.needUpgrading():
           return None, ("Migration completed at version %s" % version,)           
        
        return self._migrate(version, "up")


    security.declareProtected(ManagePortal, 'runWorkflowMigration')
    def runWorkflowTransfer(self, out, wf_from, wf_to, mapping, container=None):
        wfmt = WorkflowMigrationView(self,getattr(self,'REQUEST',{}))
        out.append(wfmt._runTransfer(wf_from, wf_to, mapping, container))
        return

InitializeClass(SiteMigrationTool)
