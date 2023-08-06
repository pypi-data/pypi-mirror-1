- Code repository: https://svn.plone.org/svn/collective/plonetheme.pyar
- Questions and comments to jmansilla "at" machinalis [dot] com
- Report bugs by mail for now

-- INSTALL

Add plonetheme.pyar to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
       ...
       plonetheme.pyar

And also tell the plone.recipe.zope2instance recipe to install a ZCML slug:

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        plonetheme.pyar

With portal_quickinstaller install it and enjoy


