Supported options
=================

url
    URL to the package that will be downloaded and extracted. The
    supported package formats are .tar.gz, .tar.bz2, and .zip. The
    value must be a full URL,
    e.g. http://openlayers.org/download/OpenLayers-2.7.tar.gz. The
    ``path`` option can not be used at the same time with ``url``.

path
    Path to a local directory containing the source code to be built
    and installed. The directory must contain the ``configure``
    script. The ``url`` option can not be used at the same time with
    ``path``.

filename
    Name of javascript file to be written. Defaults to ``OpenLayers.js``.

md5sum
    MD5 checksum for the package file. If available the MD5
    checksum of the downloaded package will be compared to this value
    and if the values do not match the execution of the recipe will
    fail.

patch-binary
    Path to the ``patch`` program. Defaults to 'patch' which should
    work on any system that has the ``patch`` program available in the
    system ``PATH``.

patch-options
    Options passed to the ``patch`` program. Defaults to ``-p0``.

patches
    List of patch files to the applied to the extracted source. Each
    file should be given on a separate line.

keep-compile-dir
    Switch to optionally keep the temporary directory where the
    package was compiled. This is mostly useful for other recipes that
    use this recipe to compile a software but wish to do some
    additional steps not handled by this recipe. The location of the
    compile directory is stored in ``options['compile-directory']``.
    Accepted values are 'true' or 'false', defaults to 'false'.


Additionally, the recipe honors the ``download-directory`` option set
in the ``[buildout]`` section and stores the downloaded files under
it. If the value is not set a directory called ``downloads`` will be
created in the root of the buildout and the ``download-directory``
option set accordingly.

The recipe will first check if there is a local copy of the package
before downloading it from the net. Files can be shared among
different buildouts by setting the ``download-directory`` to the same
location.

Example usage
=============

We'll use a simple tarball to demonstrate the recipe

    >>> import os.path
    >>> src = join(os.path.dirname(__file__), 'testdata')
    >>> ls(src)
    -  OpenLayers-2.7.tar.gz
    -  README.txt

Let's create a buildout to build and install the package

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package
    ...
    ... [package]
    ... recipe = zgeo.recipe.openlayers
    ... url = file://%s/OpenLayers-2.7.tar.gz
    ... include =
    ...     OpenLayers/Map.js
    ...     OpenLayers/Layer/WMS.js
    ... """ % src)

This will download, extract and build our demo package with the
default build options

    >>> print system(buildout)
    Installing package.
    package: Creating download directory: /sample-buildout/downloads
    package: Extracting package to /sample-buildout/parts/package__compile__
    Merging libraries.
    Importing: OpenLayers.js
    Importing: OpenLayers/BaseTypes.js
    Importing: OpenLayers/Map.js
    Importing: OpenLayers/SingleFile.js
    Importing: OpenLayers/Util.js
    Importing: OpenLayers/BaseTypes/Class.js
    Importing: OpenLayers/Layer/WMS.js
    <BLANKLINE>
    Resolution pass 1... 
    Importing: OpenLayers/BaseTypes/Bounds.js
    Importing: OpenLayers/BaseTypes/Element.js
    Importing: OpenLayers/BaseTypes/LonLat.js
    Importing: OpenLayers/BaseTypes/Pixel.js
    Importing: OpenLayers/BaseTypes/Size.js
    Importing: OpenLayers/Events.js
    Importing: OpenLayers/Lang/en.js
    Importing: OpenLayers/Layer/Grid.js
    Importing: OpenLayers/Tile/Image.js
    Importing: OpenLayers/Tween.js
    <BLANKLINE>
    Resolution pass 2... 
    Importing: OpenLayers/Lang.js
    Importing: OpenLayers/Layer/HTTPRequest.js
    Importing: OpenLayers/Tile.js
    <BLANKLINE>
    Resolution pass 3... 
    Importing: OpenLayers/Layer.js
    <BLANKLINE>
    Resolution pass 4... 
    Importing: OpenLayers/Projection.js
    <BLANKLINE>
    Resolution pass 5... 
    <BLANKLINE>
    Re-ordering files...
    <BLANKLINE>
    Exporting:  OpenLayers/SingleFile.js
    Exporting:  OpenLayers.js
    Exporting:  OpenLayers/BaseTypes.js
    Exporting:  OpenLayers/BaseTypes/Class.js
    Exporting:  OpenLayers/Util.js
    Exporting:  OpenLayers/BaseTypes/Bounds.js
    Exporting:  OpenLayers/BaseTypes/Element.js
    Exporting:  OpenLayers/BaseTypes/LonLat.js
    Exporting:  OpenLayers/BaseTypes/Pixel.js
    Exporting:  OpenLayers/BaseTypes/Size.js
    Exporting:  OpenLayers/Lang.js
    Exporting:  OpenLayers/Tween.js
    Exporting:  OpenLayers/Events.js
    Exporting:  OpenLayers/Lang/en.js
    Exporting:  OpenLayers/Projection.js
    Exporting:  OpenLayers/Tile.js
    Exporting:  OpenLayers/Map.js
    Exporting:  OpenLayers/Tile/Image.js
    Exporting:  OpenLayers/Layer.js
    Exporting:  OpenLayers/Layer/HTTPRequest.js
    Exporting:  OpenLayers/Layer/Grid.js
    Exporting:  OpenLayers/Layer/WMS.js
    <BLANKLINE>
    Total files merged: 22 
    Compressing using jsmin.
    Adding license file.
    Writing to OpenLayers.js.
    Done.
    <BLANKLINE>
    
Installing checkouts
====================

Sometimes instead of downloading and building an existing tarball we
need to work with code that is already available on the filesystem,
for example an SVN checkout.

Instead of providing the ``url`` option we will provide a ``path``
option to the directory containing the source code.

Let's demonstrate this by first unpacking our test package to the
filesystem and building that

    >>> checkout_dir = tmpdir('checkout')
    >>> import setuptools.archive_util
    >>> setuptools.archive_util.unpack_archive('%s/OpenLayers-2.7.tar.gz' % src,
    ...                                        checkout_dir)
    >>> ls(checkout_dir)
    d OpenLayers-2.7

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = package
    ...
    ... [package]
    ... recipe = zgeo.recipe.openlayers
    ... path = %s/OpenLayers-2.7
    ... filename = ol-wms.js
    ... include =
    ...     OpenLayers/Map.js
    ...     OpenLayers/Layer/WMS.js
    ... """ % checkout_dir)

    >>> print system(buildout)
    Uninstalling package.
    Installing package.
    package: Using local source directory: /checkout/OpenLayers-2.7
    Merging libraries.
    Importing: OpenLayers.js
    Importing: OpenLayers/BaseTypes.js
    Importing: OpenLayers/Map.js
    Importing: OpenLayers/SingleFile.js
    Importing: OpenLayers/Util.js
    Importing: OpenLayers/BaseTypes/Class.js
    Importing: OpenLayers/Layer/WMS.js
    <BLANKLINE>
    Resolution pass 1... 
    Importing: OpenLayers/BaseTypes/Bounds.js
    Importing: OpenLayers/BaseTypes/Element.js
    Importing: OpenLayers/BaseTypes/LonLat.js
    Importing: OpenLayers/BaseTypes/Pixel.js
    Importing: OpenLayers/BaseTypes/Size.js
    Importing: OpenLayers/Events.js
    Importing: OpenLayers/Lang/en.js
    Importing: OpenLayers/Layer/Grid.js
    Importing: OpenLayers/Tile/Image.js
    Importing: OpenLayers/Tween.js
    <BLANKLINE>
    Resolution pass 2... 
    Importing: OpenLayers/Lang.js
    Importing: OpenLayers/Layer/HTTPRequest.js
    Importing: OpenLayers/Tile.js
    <BLANKLINE>
    Resolution pass 3... 
    Importing: OpenLayers/Layer.js
    <BLANKLINE>
    Resolution pass 4... 
    Importing: OpenLayers/Projection.js
    <BLANKLINE>
    Resolution pass 5... 
    <BLANKLINE>
    Re-ordering files...
    <BLANKLINE>
    Exporting:  OpenLayers/SingleFile.js
    Exporting:  OpenLayers.js
    Exporting:  OpenLayers/BaseTypes.js
    Exporting:  OpenLayers/BaseTypes/Class.js
    Exporting:  OpenLayers/Util.js
    Exporting:  OpenLayers/BaseTypes/Bounds.js
    Exporting:  OpenLayers/BaseTypes/Element.js
    Exporting:  OpenLayers/BaseTypes/LonLat.js
    Exporting:  OpenLayers/BaseTypes/Pixel.js
    Exporting:  OpenLayers/BaseTypes/Size.js
    Exporting:  OpenLayers/Lang.js
    Exporting:  OpenLayers/Tween.js
    Exporting:  OpenLayers/Events.js
    Exporting:  OpenLayers/Lang/en.js
    Exporting:  OpenLayers/Projection.js
    Exporting:  OpenLayers/Tile.js
    Exporting:  OpenLayers/Map.js
    Exporting:  OpenLayers/Tile/Image.js
    Exporting:  OpenLayers/Layer.js
    Exporting:  OpenLayers/Layer/HTTPRequest.js
    Exporting:  OpenLayers/Layer/Grid.js
    Exporting:  OpenLayers/Layer/WMS.js
    <BLANKLINE>
    Total files merged: 22 
    Compressing using jsmin.
    Adding license file.
    Writing to ol-wms.js.
    Done.
    <BLANKLINE>
    
    >>> ls('parts/package')
    d  img
    -  ol-wms.js
    d  theme


Since using the ``path`` implies that the source code has been
acquired outside of the control of the recipe also the responsibility
of managing it is outside of the recipe.
