tranchitella.recipe.i18n
========================

This buildout recipe creates i18n tools to extract and manage po files.  More
specifically, i18n messages can occur in Python code, in Chameleon (ZPT) page
templates and in ZCML declarations.

Scripts
-------

This recipe provides the following scripts:

 i18nextract:
 
   extract the i18n messages from the Python code, the Chameleon (ZPT) page
   templates and the ZCML configuration files;

 i18nmerge:

   requires the GNU gettext package to be installed; the command 'msgmerge'
   will be executed for each language;

 i18nstatus:

   prints a simple statistics with the status of the translations.

Usage
-----

Add to your buildout configuration file the following snippet::

    [i18n]
    recipe = tranchitella.recipe.i18n
    package = PACKAGE
    zcml = PACKAGE:configure.zcml
    output = locales
    domain = DOMAIN
    verify_domain = true
    exclude =
        tests.py
        ftests.py

Replace ``PACKAGE`` with your Python package name and ``DOMAIN`` with your i18n
domain; the ``zcml`` setting is optional.
