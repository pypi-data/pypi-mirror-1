.. contents::

- Code repository: https://svn.plone.org/svn/collective/buildout/collective.recipe.updateplone

Problem
===========

After executing your buildout to deploy your Plone project you have to start
the zope instance and then go on the ZMI to create/update the plone sites,
install/reinstall some products, run some GS profiles or sometimes run some 
scripts or migrate to new Plone version. This is boring!


Solution
========

collective.recipe.updateplone is a buildout recipe that you can use to create
or update plone sites. It automatizes the following tasks:

 * Backup database
 * pack database
 * create plone sites if it do not exist
 * install or reinstall products with the quickinstaller
 * uninstall products with the quickinstaller
 * run GS profiles
 * run Plone migration (portal_migration.upgrade)

 