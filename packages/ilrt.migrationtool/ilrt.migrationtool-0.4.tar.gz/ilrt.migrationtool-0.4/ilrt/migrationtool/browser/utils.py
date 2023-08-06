from Products.CMFCore.utils import getToolByName
import os, pickle
from Acquisition import aq_base

SAVEPATH=os.path.join(INSTANCE_HOME, 'var', 'site_migration')

def runGenericSetupSteps(portal, out,
                         profile = 'mysite.theme:default',steps=[]):
    """Utility method - Remember you need to specify the right profile
       ... or else you may wipe everything back to base
       
       When using SelectedSteps you need the name of the class in
       importexport - NOT the tool name - e.g. skins, atcttool, catalog etc.
       see portal_setup/manage_importSteps checkboxes for the ids of tools
    """
    gsetup = getToolByName(portal, 'portal_setup')
    mtool = getToolByName(portal, 'site_migration')
    context_id = 'profile-%s' % profile
    ssout = []
    if not steps:
        try:
            gsetup.manage_importAllSteps(context_id=context_id)
        except ValueError:
            ssout = mtool.traceout(ssout,
                                  "Generic setup steps failed for %s" % profile)
    else:
        try:
            gsetup.manage_importSelectedSteps(context_id=context_id,
                                              ids=steps,
                                              run_dependencies=True)
        except ValueError:
            ssout = mtool.traceout(ssout,
                                  "Generic setup steps failed for %s" % profile)
    if ssout:
        out.extend(ssout)
    else:
        out.append("Finished doing generic setup steps for " + profile)
    return out

def installProducts(portal, out, products = []):
    """ Quick install products """
    if products:
        qi_tool = getToolByName(portal, 'portal_quickinstaller')
        for product in products:
            qi_tool.installProduct(product,swallowExceptions=1)
            out.append('Installed product ' + product)
    else:
        out.append('No product installed')
    return out

def removeProducts(portal,out, products = []):
    """ Quick uninstall products """

    if products:
        qi_tool = getToolByName(portal, 'portal_quickinstaller')
        for product in products:
            if qi_tool.isProductInstalled(product):
                qi_tool.uninstallProducts(products=[product,])
                out.append("Successfully uninstalled %s." % product)
            else:
                out.append("%s is *not* installed - no action taken." % product)
    else:
        out.append('No products uninstalled')
    return out


def editSiteProps(portal, out, sheet='site_properties',
                  prop='enable_link_integrity_checks',value=False):
    """ Utility function to (temporarily) switch portal properties -
        permanent changes can be done via generic setup
        Default use case is to switch off link checks whilst replacing content
    """
    portal_props = getToolByName(portal, 'portal_properties')
    propsheet = portal_props.get(sheet, None)
    if propsheet:
        if hasattr(propsheet,prop):
            try:
                propsheet._updateProperty(prop,value)
                out.append('Set %s %s to %s' % (sheet,prop,propsheet.getProperty(prop)))
            except:
                out.append('Property %s cannot be %s' % (prop,value))
        else:
            out.append('Failed to find %s property %s' % (sheet,prop))
    else:
        out.append('Failed to find property sheet %s' % sheet)
    return out

def pickleAttributes(portal,out,attributes,path,action='save'):
    """ This function is for saving persistent attributes from objects
        to file, or reloading them, where they are not handled by generic
        setup export.
        It takes the relative path to the object, a list of attributes and
        the action ie. save or load.
        Its purpose in the context of migrations is to retain ZODB data from
        objects that may be replaced by modified instances in the migration,
        e.g. the BTree of portraits attached to the memberdata tool.
    """
            
    def write_pickle(out,attr,pickled_attr):
        """ Save the attribute to a pickle """
        if not os.path.exists(SAVEPATH):        
            try:
                os.mkdir(SAVEPATH)
            except:
                return 'Failed to create or replace ' + SAVEPATH

        filepath=os.path.join(SAVEPATH,filename + '-' + attr)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
        try:
            ofd=os.open(filepath,os.O_CREAT | os.O_WRONLY | os.O_APPEND)
            try:
                os.write(ofd,pickled_attr)
            except:
                out.append("Sorry failed to write to %s due to %s" \
                                              (filepath,str(os.error)))
            os.close(ofd)
        except:
            out.append("Failed to open %s for writing" % filepath)
        return

    def read_pickle(out,attr):
        """ Load the attribute from a pickle """
        filepath = os.path.join(SAVEPATH,filename + '-' + attr)        
        pickle = None
        if not os.path.exists(filepath):
            out.append('Not found file ' + filepath)
        else:
            try:
                ofd=open(filepath,'r')
                pickle=ofd.read()
                ofd.close()
            except:
                out.append('File %s could not be read' % filepath)
        if not pickle:
            out.append('File %s was empty' % filepath)
        return pickle

    filename = path.replace('/','_')
    if filename.startswith('_'):
        filename = filename[1:]
    obj = portal
    for part in path.split('/'):
        if part and hasattr(obj,part):
            obj = getattr(obj,part)

    if action=='load':
        for attr in attributes:
            if hasattr(obj,attr):
               pickled_attribute = read_pickle(out,attr)
               if pickled_attribute:
                   attribute = pickle.loads(pickled_attribute)
                   if attribute:
                       setattr(obj,attr,attribute)
                   out.append('Loaded pickle to %s.%s' % (obj.getId(),attr))
    else:
        attrs = []
        for attr in attributes:
            attribute = getattr(obj,attr,'')
            if attribute:
                attrs.append(attr)
                attribute = aq_base(attribute)
                try:
                    pickled_attr=pickle.dumps(attribute)
                    write_pickle(out,attr,pickled_attr)
                except:
                    out.append('Unpicklable attribute - %s' % attr)
        if attrs:
            out.append('You have saved your attributes from %s to %s' \
                                             % (str(attrs)[1:-1],SAVEPATH))
        else:
            out.append('The object %s has none of the listed attributes' \
                                                             % obj.getId())


