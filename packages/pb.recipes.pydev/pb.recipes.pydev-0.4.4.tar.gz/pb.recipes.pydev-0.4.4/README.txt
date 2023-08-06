================
pb.recipes.pydev
================

A recipe that writes a .pydevproject file in a specified location. This file will
contain paths of all the eggs of the current zope instance + any other paths 
specified in the buildout.cfg file. After running the buildout you'll have to 
close and reopen the Eclipse project, to regenerate the project's module indexes. 

Almost all options of this recipe for the buildout.cfg are optional. The only
one required is the `eggs` option. A sample zope3 instance buildout, with the
pydev recipe could be something like this::

    [buildout]
    develop = .
    parts = instance pydev

    [sample-app]
    recipe = zc.zope3recipes:app
    eggs = something [app, third_party]

    [pydev]
    recipe = pb.recipes.pydev
    eggs = ${sample-app:eggs}

For Plone integration and further configuration options, read the README.txt 
doctest inside the source code.