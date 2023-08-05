MxBase recipe
=============

As there isn't available eggs for Egenix mx base
(http://www.egenix.com/products/python/mxBase/ ). This recipe will download
the tarball, build it and link it for you inside your buildout.

Usage:

    Define the recipe and add it to the buildout parts. Ex:


        [buildout]
        parts =
            mx-base
            ...

        [mx-base]
        recipe = collective.recipe.mxbase


    If you use buildout for zope 2 don't forget to add the created egg to your
    zope2instance:


        [instance]
        recipe = plone.recipe.zope2instance
        ...
        eggs =
            ...
            egenix-mx-base


