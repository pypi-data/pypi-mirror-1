Introduction
============

This package gives Plone users the ability to use creole wiki syntax in their Plone site.  Creole aims to be a common wiki format across all wiki engines.  Now you can use it in Plone!

To see some examples of Creole wiki text take a look at the cheat sheet: http://www.wikicreole.org/wiki/CheatSheet

Install
-------

To install collective.transform.creole with buildout do the following::

  [instance]
  eggs = collective.transform.creole
  zcml = collective.transform.creole

Once the package is installed you can do the following:

- Run the 'Creole Transform Install' profile
- Go to Site setup -> markup
- Make sure the text/wiki+creole transform is enabled
- Set your default editor to 'Plain Text'
- Write some wiki text!

To uninstall, run the 'Creole Transform Uninstall' profile and remove the package from your buildout.

