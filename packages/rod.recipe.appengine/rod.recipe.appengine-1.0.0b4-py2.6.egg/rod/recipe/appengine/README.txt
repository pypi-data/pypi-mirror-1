appengine-Build Recipe
======================

The build recipe takes a number of options:

src
    The directory which contains the project source files.

packages
    A list of packages to be included into the zip archive, which will be
    uploaded to the appspot.

zip-name
    The name of the zip archive containing all external packages ready
    to deploy.

script
    Name of the appserver script.

appengine-lib
    A path where the appengine library is installed.
