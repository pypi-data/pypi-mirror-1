from Products.CMFCore.utils import getToolByName

def runGenericSetupSteps(portal, out,
                         profile = 'mysite.theme:default',steps=[]):
    """Utility method - Remember you need to specify the right profile
       ... or else you may wipe everything back to base """
    gsetup = getToolByName(portal, 'portal_setup')
    context_id = 'profile-%s' % profile 
    if not steps:
        try:
            gsetup.manage_importAllSteps(context_id=context_id)
        except ValueError:
            out.append("Sorry you submitted an invalid value " \
                       + str(ValueError))
    else:
        try:
            gsetup.manage_importSelectedSteps(context_id=context_id,
                                              ids=steps,
                                              run_dependencies=True)
        except ValueError:
            out.append("Sorry you submitted an invalid value " \
                       + str(ValueError))

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
