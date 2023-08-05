****************************************************************
Recipe that parses compile options from libraries config scripts
****************************************************************

.. contents::

The LibInc recipe can parse CFLAGS, LDFLAGS and other information
tipically returned by libraries config scripts like gdal-config, libpng-config
and others. The parsed information can be used by other recipes as
hexagonit.recipe.cmmi or zc.recipe.egg to make the build process more
robust.

The initial version of this recipe has been written within the PrimaGIS
topic of the 2007 Plone Naples Sprint and it is used for the PCL/PrimaGIS
buildout.
