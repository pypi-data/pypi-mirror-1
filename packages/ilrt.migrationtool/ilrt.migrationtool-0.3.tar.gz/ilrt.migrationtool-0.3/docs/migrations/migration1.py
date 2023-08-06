# As a minimun a migration must have the VERSIONS tuple and the upgrade and downgrade methods
# These methods should return a list containing any messages
# related to running the methods in upgrade / downgrade

# Import the utility methods runGenericSteps and installProducts from the tool
from ilrt.migrationtool.browser.utils import *

VERSIONS = ('2.0','3.0')

def upgrade(portal):
    """ 2 upgrade to 3 
        Remember the sequence of method calls may be significant
    """
    out = []

    # Quick installer addition of products - obviously these need to be added
    # in the buildout if they are not core add-ons like plone.app.iterate
    installProducts(portal, out, products = ['ilrt.formalworkflow','plone.app.iterate'])

    # The use of runGenericSetupSteps assumes that a profile folder has been added in
    # profiles/migration1 this caters for the use of generic setup XML to configure the site

    # A profile for each migration will also need to be added to profiles.zcml ...

    # <genericsetup:registerProfile
    #    name="migration1"
    #    title="My Theme Migration 1"
    #    directory="profiles/migration1"
    #    description='Profile for use by migration 1 of my.theme'
    #    provides="Products.GenericSetup.interfaces.EXTENSION" />

    runGenericSetupSteps(portal, out, profile = 'my.theme:migration1', steps = ['rolemap',])

    # For this example we are adding a product that installs a new workflow so we also
    # want to make use of the workflow migration tool 
    portal.site_migration.runWorkflowTransfer(out=out,
                                              wf_from='simple_publication_workflow',
                                              wf_to='formal_workflow',
                                              mapping={'private':'private',
                                                      'pending':'pending',
                                                      'published':'published'})
    return out

def downgrade(portal):
    """ 3 downgrade to 2
        Remember the sequence of method calls may be significant
    """
    out = []

    # Set the site contents workflow states to be the same in the old workflow as they
    # are in the new one
    portal.site_migration.runWorkflowTransfer(out=out,
                                              wf_from='formal_workflow',
                                              wf_to='simple_publication_workflow',
                                              mapping={'private':'private',
                                                      'pending':'pending',
                                                      'published':'published'})

    # Revert back the step in the migration1 profile to the original settings
    runGenericSetupSteps(portal, out, profile = 'my.theme:default', steps = ['rolemap',])

    # Uninstall the products
    removeProducts(portal, out, products = ['ilrt.formalworkflow','plone.app.iterate'])

    return out

