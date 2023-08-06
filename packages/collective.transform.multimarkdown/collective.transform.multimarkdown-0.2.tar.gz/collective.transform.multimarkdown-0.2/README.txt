Introduction
============

This package allows Plone users to include MultiMarkdown syntax in their Plone sites. MultiMarkdown is a derivative of John Gruber's original Markdown project.

To see the improved MultiMarkdown syntax, check out the `Syntax Guide <http://fletcherpenney.net/multimarkdown/users_guide/multimarkdown_syntax_guide/>`_.

Install
-------

To install collective.transform.multimarkdown with buildout do the following::

  [instance]
  eggs = collective.transform.multimarkdown
  zcml = collective.transform.multimarkdown

Once the package is installed you can do the following:

- Run the `MultiMarkdown Transform` profile
- Go to `Site Setup` -> `Markup`
- Make sure the `text/x-multimarkdown` transform is enabled
- Set your default editor to `Plain Text`
- Write some MultiMarkdown!

To uninstall, run the `MultiMarkdown Transform Uninstall` profile and remove the package from your buildout.

Limitations
-----------

This packages makes use of the MultiMardown perl scripts to do the actual transform. If you have a copy of MultiMarkdown.pl and want to use it instead of the script included in this package, make sure it is in your PATH, and the package will find and use it.

Since this packages uses perl scripts, you must have perl installed and in your PATH for the transform to work correctly. This package has only been tested on \*nix and should work on most flavors of Linux and BSD. Use of this package on a Windows machine could cause errors.
