ilrt.migrationtool Package Readme
=================================

Ed Crewe, `ILRT
<http://www.ilrt.bris.ac.uk/>`_ at University of Bristol, May 2009

Overview
--------

This package installs a Site Migration Tool in the root of a plone site.
It provides a controlled upgrade (and downgrade) system for production
plone sites. It is designed for a scenario where you have developed a theme egg for
the site and you now wish to roll out new development phases to the production
site in an automated manner, e.g. without significant use of the ZMI.

The tool is based on the CMFPlone.MigrationTool but with downgrade functionality added.
This is because most site upgrades involve more minor changes than a plone upgrade, ie. adding 
some products, configuring them, changing zope security, etc. If we are going to automate these 
changes then we also want to automate undoing them. That way we can quickly revert a roll out 
if it goes wrong.

Once it is installed you will have a new tool at /site_migration via the ZMI in your plone site. 

As a generic site migration tool it provides the framework and a number of migration related 
utility functions, plus one 'sub-tool' (so far) for migrating content's workflow states, the 
workflow migration tool, which can be used in isolation. 

The main utility function allows migrations to use `generic setup
<http://pypi.python.org/pypi/Products.GenericSetup>`_ so that each migration is 
likely to have a related profile in the theme egg, where the changes from the last migration
(or the initial default profile) are stored.

Just as with the portal_migration tool the site_migration tool looks up the version via the 
version.txt on the file system as compared to the version in the ZODB. Based on that it flags 
up whether a migration is needed. 

Concept
-------

The concept is derived from an unreleased plone 2 product by Dominic Hiles, which has been
used to control production site releases since 2005.

It is envisaged that users would run through performing an upgrade on a development server with 
a copy of the production ZODB, from that they would generate the appropriate migration profile
and compose the upgrade, downgrade methods. These can then be added and re-tested ready for pushing
the migrate button on the production server.

The underlying principle being that the exact configuration state of your production site is
recorded and replicable, similar to the aims of generic setup, but here you are 
more specifically recording the plone customisations related to the particular 
production site / theme egg, rather than all the setup configurations in plone. 

Of course if you lose track of the changes made between one migration and the next you could just 
dump the whole generic setup export into your migration profile, that at least ties a site 
config to a version of the site, but buries the changes required for that version of the site 
amongst all the others.
     

Using the Site Migration Tool
-----------------------------

The tool allows for the setting of the source theme egg for migrations. 

That egg must have the actual migrations added to it within a migrations folder.
An example migrations folder is provided within the migrationtool to copy to a theme egg, ie.
copy ilrt.migrationtool/docs/migrations to my.theme/my/theme/migrations

Each migration script within the folder must be imported in the __init__.py for the folder in
order to find it. The migrations upgrade can have a related folder created in profiles with
generic setup files added.

- Once the theme egg has migrations, and the server has been restarted to initialize these new 
  files, the migrationtool can use python introspection to find them and activate them.

- Choose the appropriate profile from the drop down on the 'Set migration source' tab for the tool.

- You should then see a list of your migrations and what versions of the site they relate to.

- Now you can click on the 'Do migration' tab 

- For a site to be ready for migration the ZODB version of the theme egg should be earlier 
  than the one on the file system, ie. your file system code is upgraded ... so now the ZODB 
  needs to be migrated to be in synch.

- If this is the case for your site the Migrate button will be available, if not then either 
  your theme egg version.txt file needs upping a notch (plus a restart), or you need to force 
  the ZODB version down a notch with the 'update instance version' button.

- Once you have the migrate button you can check 'Dry run' to test it will work first. 

- A failiure to upgrade or any other errors mean you will need to fix your upgrade methods. 

- Once the 'Dry run' runs OK, you can upgrade for real, and add the migration to your egg and repeat
  the process on your production server.

Utilities
---------

1. runGenericSetupSteps
   Wrapper for generic setup

2. installProducts / uninstallProducts
   Wrapper for the quickinstaller

3. pickleAttributes
   This caters for writing ZODB stored data associated with objects out to the file system.
   The use case being that a migration may require the removal and reinstantiation of objects 
   due to their class having been modified. When these objects are replaced associated data 
   may be lost, if it is not handled by generic setup export/import. 
   An example for this is the portraits associated with the memberdata_tool, if a migration 
   modified this class then this tool allows for its reinstantiation to keep the BTree 
   that is its .portraits attribute.

4. editSiteProps
   Utility function to temporarily switch portal properties while the migration runs.
   Default use case is to switch off link checks whilst replacing content.

Workflow Migration Tool
-----------------------

The workflow migration tool moves the state of content that has been in one workflow to the 
specified state in another. Likely uses for the tool are to maintain equivalent state for 
content when the workflow that a site uses is changed, or in conjunction with CMFPlacefulWorkflow.

So for example a site may allow users to toggle whether a folder is an intranet folder or public.
However when a public folder is made into an intranet the user doesn't want everything to be 
reset to the private state, in this case the tool can be called via an event tied to the change
of workflow policy for a folder. 

To use the tool via the web:

- Change the workflows for your plone site in the portal_workflow tool 
  (or add a placeful workflow policy to a folder)

- Go to the Migrate workflow tab and enter the previous workflow followed by the new one you 
  have replaced it with.

- Next specify the mapping that you require of states from one workflow to another, 
  eg. public draft = published etc.

- Finally if its placeful specify the folder.

Hit submit and the migration will recursively find all the objects in the new workflow and update 
their state based on the mapping, from what it was in the old one. The tool will return the
number of workflow transitions performed.

Keyword Index Migration Tool
----------------------------

This is lifted from Products.PloneKeywordManager, the extra feature is that keywords can 
be moved between different fields and their corresponding indexes in the zcatalog. 
The use case being the migration of a set of standard keywords into their own field 
and controlled vocabulary.

