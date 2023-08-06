==============================
collective.recipe.z2testrunner
==============================

Overview
========

A zc.buildout recipe for generating test runners that run under a Zope 2
environment and is "Products"-aware.


Options
=======

collective.recipe.z2testrunner has the following options:

zope2part 
    name of the script in bin directory to run zope (e. g. zopectl)

defaults 
    list of default options to call zopectl test with

environment
    name of a section which defines variables to be set in environment

modules
    list of modules to test (arguments for parameter -m)

packages 
    list of packages to test (arguments for parameter -s)

extra-paths
    list of paths (arguments for parameter --path)

exit-with-status
    boolean whether to set parameter --exit-with-status or not (default: false)
