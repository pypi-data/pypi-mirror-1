- Code repository: https://svn.plone.org/svn/collective/plonetheme.overlappedtabs
- Questions and comments to jmansilla "at" machinalis [dot] com
- Report bugs by mail for now

-- INSTALL

Add plonetheme.overlappedtabs to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
       ...
       plonetheme.overlappedtabs

And also tell the plone.recipe.zope2instance recipe to install a ZCML slug:

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        plonetheme.overlappedtabs

With portal_quickinstaller install it and enjoy

