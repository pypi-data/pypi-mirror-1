This is a buildout recipe to install eGenix mxODBC.ZopeDA and a licence.

The recipe is largely based on  collective.recipe.mxodbc, a recipe creatd by 
Jarn to installed eGenix mxODBC. That recipe will install mxODBC 3.0 and also
build an mx.base package from source.

You can add this recipe to your buildout by adding a section like this::

    [mxzopeda]
    recipe = collective.recipe.mxzopeda
    license-key = puty-ourl-icen-seco-dehe-repl-ease
    licsenses-archive = mxzopeda-licenses.zip

The licenses archive should be a zip file with one directory for every license
you want to use with the license key as file name and the license file you
got from eGenix for that code in the directory.

The recipe tries to detect the correct platform to download the prebuilt
archive for, but has so far only been verified on Apple OS X universal systems
and Ubuntu server 8.10 for i686. Please report any problems if you encounter
problems with other architectures.
