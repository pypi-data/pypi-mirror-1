=======================
Google Appengine Recipe
=======================

This recipe takes a number of options:

appengine-lib
    Path to an already installed appengine library

eggs
    List of required eggs

packages
    A list of packages to be included into the zip archive, which will be
    uploaded to the appspot.

src
    The directory which contains the project source files.

url
    The url for fetching the google appengine distribution

zip-name
    The name of the zip archive containing all external packages ready
    to deploy.


Tests
=====

We will define a buildout template used by the recipe:

    >>> buildout_template = """
    ... [buildout]
    ... develop = %(egg_src)s
    ... parts = sample
    ...
    ... [sample]
    ... recipe = rod.recipe.appengine
    ... eggs = foo.bar
    ... url = http://googleappengine.googlecode.com/files/google_appengine_1.2.0.zip
    ... """

We'll start by creating a buildout:

    >>> import os.path
    >>> import rod.recipe.appengine.tests as tests
    >>> egg_src = os.path.join(os.path.split(tests.__file__)[0], 'foo.bar')
    >>> write('buildout.cfg', buildout_template % {'egg_src': egg_src})

Running the buildout gives us:

    >>> output = system(buildout)
    >>> if output.endswith("Installing sample.\n"): True
    ... else: print output
    True

And now we try to run the appserver script:

    >>> print system(os.path.join('bin', 'sample'))
    <BLANKLINE>
    ...
    Invalid arguments
    <BLANKLINE>
