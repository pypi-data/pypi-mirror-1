Supported options
=================

The recipe supports the following options:

source
    Source directory that contains the .po files that the recipe will
    copy.  All ``*.po`` files will be copied.  This option is mandatory.

destinations
    Target directory or directories.  This should point to the
    directory of the zope 2 instance.  The recipe will create an i18n
    directory in each of the destinations and copy all ``*.po`` files
    from the source directory to these i18n directories.  This option
    is mandatory.


Example usage
=============

We'll start by creating a buildout that uses the recipe.  Here is a
template where we only have to fill in the source and destinations::

    >>> buildout_config_template = """
    ... [buildout]
    ... index = http://pypi.python.org/simple
    ... parts = i18noverrides
    ...
    ... [i18noverrides]
    ... recipe = collective.recipe.i18noverrides
    ... source = %(source)s
    ... destinations = %(dest)s
    ... """

We will start with specifying some non existing source and destination
directories::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': '${buildout:directory}/translations',
    ... 'dest': '${buildout:directory}/instance'})

Running the buildout gives us::

    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: path '/sample-buildout/translations' does not exist.
    <BLANKLINE>

The source must be a directory::

    >>> write('translations', 'This is a file.')
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: path '/sample-buildout/translations' must be a directory.
    <BLANKLINE>

Now we remove this file and try with a proper directory::

    >>> remove('translations')
    >>> mkdir('translations')
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: path '/sample-buildout/instance' does not exist.
    <BLANKLINE>

So we set a destination too and first try with a file as well before
creating a directory::

    >>> write('instance', 'This is a file.')
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: path '/sample-buildout/instance' must be a directory.
    <BLANKLINE>
    >>> remove('instance')
    >>> mkdir('instance')
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: source '/sample-buildout/translations' contains no .po files.
    <BLANKLINE>

Now the source and destination have been setup correctly, but we get a
warning as the source directory has no translation files.  We first
add a file that does not end with ``.po``.  Since the previous
buildout run only had a warning and finished successfully, the recipe
now runs in update mode, which does the same as the install mode::

    >>> write('translations', 'not-a-po-file', 'I am not a po file')
    >>> print system(buildout) 
    Updating i18noverrides.
    collective.recipe.i18noverrides: source '/sample-buildout/translations' contains no .po files.
    <BLANKLINE>
    >>> write('translations', 'plone-nl.po', 'I am a Dutch plone po file')
    >>> write('translations', 'plone-de.po', 'I am a German plone po file')
    >>> print system(buildout) 
    Updating i18noverrides.
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>

No warnings, no errors, so let's see what the end result is::

    >>> ls('translations')
    -  not-a-po-file
    -  plone-de.po
    -  plone-nl.po
    >>> ls('instance')
    d  i18n

A i18n directory has been created in the instance.  Inside that
directory we find our two po files::

    >>> ls('instance', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> cat('instance', 'i18n', 'plone-de.po')
    I am a German plone po file
    >>> cat('instance', 'i18n', 'plone-nl.po')
    I am a Dutch plone po file

If the destination directory for some strange reason already contains
a i18n file instead of a directory, we fail::

    >>> remove('instance', 'i18n')
    >>> write('instance', 'i18n', 'I am a file')
    >>> print system(buildout) 
    Updating i18noverrides.
    collective.recipe.i18noverrides: '/sample-buildout/instance/i18n' is not a directory.
    <BLANKLINE>
    >>> remove('instance', 'i18n')

It should also be possible to have multiple destinations::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': '${buildout:directory}/translations',
    ... 'dest': """
    ...     ${buildout:directory}/instance
    ...     ${buildout:directory}/instance2"""})
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: path '/sample-buildout/instance2' does not exist.
    <BLANKLINE>

Right, right, we will create that directory too::

    >>> mkdir('instance2')
    >>> print system(buildout) 
    Installing i18noverrides.
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance/i18n
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance2/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>

Let's check the result::

    >>> ls('instance')
    d  i18n
    >>> ls('instance', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> ls('instance2')
    d  i18n
    >>> ls('instance2', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> cat('instance2', 'i18n', 'plone-de.po')
    I am a German plone po file
    >>> cat('instance2', 'i18n', 'plone-nl.po')
    I am a Dutch plone po file
