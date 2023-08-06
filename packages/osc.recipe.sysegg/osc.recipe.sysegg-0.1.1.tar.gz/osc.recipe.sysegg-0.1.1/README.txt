SysEggs
=======

This buildout recipe allows you to reuse system wide eggs in your buildout.
If SysEggs finds the requested eggs in you pythons site-packages directory
(or PYTHONPATH) it will create a ``.egg-link`` to it. Other packages that
require these eggs will not fetch them. 

Example
-------
If you have an application that depends on the python image library (PIL) and
you want to use the library that is already installed (e.g. with apt-get on Debian),
you can use a buildout.cfg like this::

    [buildout]

    parts =
        sysegg
        otherpart

    [sysegg]
    recipe = osc.recipe.sysegg
    eggs = PIL
    
    [otherpart]
    recipe = zs.recipe.egg
    egg = egg_that_depends_on_PIL

You should list sysegg before all other parts.
