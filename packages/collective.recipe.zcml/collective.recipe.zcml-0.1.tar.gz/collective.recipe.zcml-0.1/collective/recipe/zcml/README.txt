Supported options
=================

The recipe supports the following options:

zcml
    A list of zcml entires.

    format::

        zcml := package ":" filename
        package := dottedname | dottedname "-" ( "configure" | "meta" | "overrides" )

zope2-location
    The location of the zope 2 installation.

The guts of creating ZCML slugs was ripped from **plone.recipe.zope2install**.

Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = collective.recipe.zcml
    ... zope2-location=${buildout:directory}/zope
    ... zcml =
    ...     my.package
    ...     somefile:my.otherpackage
    ...     my.thirdpackage-meta
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start Installing test1.
    While:
      Installing test1.
    <BLANKLINE>
    An internal error occured due to a bug in either zc.buildout or in a
    recipe being used:
    <BLANKLINE>
    OSError:
    [Errno 2] No such file or directory: '/sample-buildout/zope/etc/package-includes'
    <BLANKLINE>

We need to have a valid zope installation. Let's fake one::

    >>> mkdir("zope")
    >>> mkdir("zope", "etc")
    >>> print 'start', system(buildout) # doctest:+ELLIPSIS
    start Installing test1.

We now have a package include directory::

    >>> ls("zope", "etc")
    d  package-includes

It does contain ZCML slugs::

    >>> ls("zope", "etc", "package-includes")
    -  001-my.package-configure.zcml
    -  002-somefile-configure.zcml
    -  003-my.thirdpackage-meta.zcml

These  files contain the usual stuff::

    >>> cat("zope", "etc", "package-includes", "001-my.package-configure.zcml")
    <include package="my.package" file="configure.zcml" />
    >>> cat("zope", "etc", "package-includes", "002-somefile-configure.zcml")
    <include package="somefile" file="my.otherpackage" />
    >>> cat("zope", "etc", "package-includes", "003-my.thirdpackage-meta.zcml")
    <include package="my.thirdpackage" file="meta.zcml" />

That's all.


