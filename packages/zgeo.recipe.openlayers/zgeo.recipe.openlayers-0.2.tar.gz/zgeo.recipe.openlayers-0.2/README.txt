**********************
zgeo.recipe.openlayers
**********************

.. contents::

The recipe provides the means to create `custom build profiles`_ for the
OpenLayers_ javascript library. A compressed, single OpenLayers.js file, and
accompanying ``img`` and ``theme`` directories are created in the named
directory under the buildout's ``parts`` directory.

For example, consider the following buildout.cfg file::

  [buildout]
  parts = openlayers-2.7-wms
  
  [openlayers-2.7-wms]
  recipe = zgeo.recipe.openlayers
  url = http://openlayers.org/download/OpenLayers-2.7.tar.gz
  include =
      OpenLayers/Map.js
      OpenLayers/Layer/WMS.js

Building it out::

  $ bin/buildout -c buildout.cfg
  Installing openlayers.
  openlayers-2.7-wms: Creating download directory: /Users/seang/code/ol-recipes/downloads
  openlayers-2.7-wms: Extracting package to /Users/seang/code/ol-recipes/parts/openlayers__compile__
  Merging libraries.
  Importing: OpenLayers.js
  Importing: OpenLayers/BaseTypes.js
  Importing: OpenLayers/Map.js
  Importing: OpenLayers/SingleFile.js
  Importing: OpenLayers/Util.js
  Importing: OpenLayers/BaseTypes/Class.js
  Importing: OpenLayers/Layer/WMS.js
  
  Resolution pass 1... 
  Importing: OpenLayers/BaseTypes/Bounds.js
  ...
  
  Re-ordering files...
  
  Exporting:  OpenLayers/SingleFile.js
  Exporting:  OpenLayers.js
  ...
  Exporting:  OpenLayers/Layer/WMS.js
  
  Total files merged: 22 
  Compressing using jsmin.
  Adding license file.
  Writing to OpenLayers.js.
  Done.
  
Produces these files::

  $ ls -l parts/openlayers-2.7-wms/
  total 224
  -rw-r--r--   1 seang  staff  112535 Jun  3 13:41 OpenLayers.js
  drwxr-xr-x  25 seang  staff     850 Jun  3 13:41 img
  drwxr-xr-x   3 seang  staff     102 Jun  3 13:41 theme

.. _custom build profiles: http://docs.openlayers.org/library/deploying.html#custom-build-profiles
.. _OpenLayers: http://openlayers.org
