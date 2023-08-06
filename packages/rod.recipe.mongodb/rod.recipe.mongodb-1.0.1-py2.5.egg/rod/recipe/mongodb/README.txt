A brief documentation
=====================

This recipe takes a number of options:

darwin-32bit-url
    The URL to download the 32 bit binary package for the darwin platform.

darwin-64bit-url
    The URL to download the 64 bit binary package for the darwin platform.

linux2-32bit-url
    The URL to download the 32 bit binary package for the linux platform.

linux2-64bit-url
    The URL to download the 64 bit binary package for the linux platform.
 

Tests
=====

We will define a buildout template used by the recipe:

    >>> buildout_cfg = """
    ... [buildout]
    ... parts = mongodb
    ...
    ... [mongodb]
    ... recipe = rod.recipe.mongodb
    ... darwin-32bit-url = http://downloads.mongodb.org/osx/mongodb-osx-i386-0.9.7.tgz
    ... """

We'll start by creating a buildout:

    >>> import os.path
    >>> write('buildout.cfg', buildout_cfg)

Running the buildout gives us:

    >>> output = system(buildout)
    >>> if output.endswith("downloading mongoDB distribution...\n"): True
    ... else: print output
    True
