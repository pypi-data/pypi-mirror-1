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
from ilrt.migrationtool.browser.atfieldtool import ATFieldIndexInfo
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
        """ Initialization just calls the reset of attributes """
        self.wfmt = WorkflowMigrationView(self,getattr(self,'REQUEST',{}))
        self.atfit = ATFieldIndexInfo()  
        self.clearMigrations()

    def clearMigrations(self):
        ''' Deletes stored migration objects and upgrade / downgrade methods '''
        self.migrations = {}
        self.methodlists = {}        
        self._upgradePaths = {}
        self._downgradePaths = {}
        self.migration_id = ''
        self.egg = ''
        return
        
    def log(self,message,summary='',severity=0):
        """ Logs errors """
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
        request = getattr(self,'REQUEST',{})
        if request.get('migration_id',''):
            self.migration_id = migration_id
            self.getMigrationMethods()
            request.RESPONSE.redirect('@@manage_run_migration_method')
        return

    def getMigrationMethods(self):
        """ List all the methods for a particular migration object """
        if not self.migration_id:
            return []
        else:
            if self.methodlists:
                return self.methodlists.get(self.migration_id,[])

    def runMigrationMethod(self,method,**kwargs):
        """ Run an individual method from a migration script
            Note that whether a migration method can be run individually or
            even whether individual methods are used is down to the author
            of the migration scripts
            This just provides them with an extra debugging tool
        """
        portal = getUtility(ISiteRoot)
        out = ["Ran individual migration method %s" % method,]
        if self.methodlists.has_key(self.migration_id):
            if method in self.methodlists.get(self.migration_id,[]):
                try:
                    exec('from ' + self.egg + ' import migrations')
                except ImportError:
                    out.append("Error: Sorry this egg, " + str(self.egg) + ", has no migrations \
                        - please add a migrations folder with migration scripts in")
                    return out
                except:
                    return self.traceout(out)
                mig = getattr(migrations,self.migration_id, None)
                if mig:
                    me = getattr(mig,method,None)
                    if me:
                        try:
                            if method in ('upgrade','downgrade'):
                                out.extend(me(self.aq_parent))
                            else:
                                me(self.aq_parent, out)
                        except:
                            out = self.traceout(out,'Error from running %s' % method)
                    else:
                        out.append('Sorry the method could not be extracted from the migration script')
                else:
                    out.append('Sorry the migration script could not be extracted from the migrations directory')
            else:
                out.append('Sorry the method %s was not found in %s' % (method, self.migration_id))                
        else:
            out.append('Sorry the methods for %s were not found' % self.migration_id)

        out = [(msg, '') for msg in out]
        return self.manage_results(self,out=out)

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
        self.clearMigrations()
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

    def traceout(self, out,
           msg='Your migration scripts caused a fatal error please correct it'):
        ''' Push error traceback out to ZMI interface '''
        out.append('Error: %s' % msg)
        out.append('TRACEBACK ...')
        errlines = traceback.format_exc().split('File')
        if len(errlines)>3:
            errlines = errlines[3:]
        for err in errlines:
            out.append(err)
        return out

    def importMigrations(self, out):
        ''' Import the migrations in the source egg to the tool '''

    def loadMigrations(self, reload=0):
        ''' Search for sitemigrations in the specified egg '''
        out = []
        if not self.egg:
            return out
        if reload or not getattr(self,'migrations',None):
            self.migrations = {}
            self.methodlists = {}
            try:
                exec('from ' + self.egg + ' import migrations')
            except ImportError:
                out.append("Error: Sorry this egg, " + str(self.egg) + ", has no migrations \
                    - please add a migrations folder with migration scripts in")
                return out
            except:
                return self.traceout(out)
            try:
                migrationlist = [m for m in dir(migrations) \
                                            if not m.startswith('__')]
            except:
                migrationlist = []
            if not migrationlist:
                out.append("Error: the migrations folder has no initialized \
                            migrations - check you have added them in the init")  
            util_methods = dir(utils)
            for m in migrationlist:
                m = str(m)
                try:
                    migration = getattr(migrations,m)
                    methodlist = [me for me in dir(migration) \
                                 if not me.startswith('__')]
                    methodlist = list(set(methodlist) - set(util_methods))
                except:
                    methodlist = []
                    msg = 'Failed to get method list from migration script %s please check your methods' % m
                    out = self.traceout(out, msg)
                if 'VERSIONS' in methodlist:
                    if 'upgrade' in methodlist:
                        try:
                            self.registerUpgradePath(migration.VERSIONS[0],
                                                     migration.VERSIONS[1],
                                                     migration.upgrade)
                            if hasattr(migration,'downgrade'):
                                self.registerDowngradePath(migration.VERSIONS[1],
                                                           migration.VERSIONS[0],
                                                           migration.downgrade)
                            self.migrations[m] = migration.VERSIONS
                            self.methodlists[m] = [me for me in methodlist if me != me.upper()]
                        except:
                            out = self.traceout(out,'Failed to register migration %s' % m)
                    else:
                        out.append("Error: Sorry migration script '" + m + \
                                   "' has no upgrade function please add \
                                   one ie. def upgrade(self, portal):")
                else:
                    out.append("Error: Sorry migration script '" + m + \
                                   "' has no VERSIONS please add one \
                                    ie. VERSIONS = ('1','2')")
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

    security.declareProtected(ManagePortal, 'runWorkflowTransfer')
    def runWorkflowTransfer(self, out, wf_from, wf_to, mapping, container=None):
        out.append(self.wfmt._runTransfer(wf_from, wf_to, mapping, container))
        return

InitializeClass(SiteMigrationTool)
