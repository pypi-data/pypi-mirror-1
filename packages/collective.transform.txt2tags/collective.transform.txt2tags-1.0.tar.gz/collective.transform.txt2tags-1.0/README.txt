Introduction
============

This package gives Plone users the ability to use txt2tags syntax in their Plone site.

Txt2tags documentation can be found in http://txt2tags.sourceforge.net.

In this transform the first three lines of txt2tags files are ignored letting Plone setting the title, author, etc.

Install
-------

To install collective.transform.txt2tags with buildout do the following::

  [instance]
  eggs = collective.transform.txt2tags
  zcml = collective.transform.txt2tags

To write content in txt2tags format you must do the following:

- Run the 'Txt2tags Transform Install' profile
- Go to Site setup -> markup
- Make sure the text/x-txt2tags transform is enabled
- Set your default editor to 'Plain Text'

To uninstall, run the 'Txt2tags Transform Uninstall' profile and remove the package from your buildout.

