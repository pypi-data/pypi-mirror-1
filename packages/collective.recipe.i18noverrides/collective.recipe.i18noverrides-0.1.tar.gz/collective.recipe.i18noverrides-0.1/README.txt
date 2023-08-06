.. contents::

collective.recipe.i18noverrides
===============================

This is a buildout recipe.  It creates an i18n directory within one or
more zope 2 instances in your buildout.  It copies some .po files to
those directories.  The translations in those .po files will override
any other translations.  


Use case
--------

An example use case is:

- In the Dutch Plone translations the msgid 'Manager' is translated as
  'Beheerder'.

- A customer wanted it to be translated as 'Site admin' instead.

- Just putting this translation within the i18n directory of the
  customer product is not guaranteed to work as it depends on the
  order in which the i18n folders get read on Zope startup: is
  CMFPlone/i18n or Customer/i18n read first.

- When you create an i18n directory within the zope 2 instance and add
  a po file with that msgid there, this is guaranteed to get used.

Note that this should work for overriding translations within i18n
directories.  Overriding translations in locales directories is not a
use case of this recipe.


Contents of .po file
--------------------

What should be in the .po file?  You need all the headers that are
normally in .po files.  So copy the headers of the current .po file
that has the translation that you want to override.  Then just add the
msgid and a new msgstr.  The name of the file does not really matter.
It should be meaningful to you and end with '.po'.  In the mentioned
use case it makes sense to call it ``plone-nl.po`` as that is the name
of the original file from the plone translations.  The contents would
be something like this (non-interesting header lines skipped for
clarity)::


  msgid ""
  msgstr ""
  ...
  "Language-Code: nl\n"
  "Language-Name: Nederlands\n"
  "Domain: plone\n"

  msgid "Manager"
  msgstr "Site admin"

