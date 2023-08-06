ore.recipe.svnlib
-----------------

A Recipe for downloading and compiling the python subversion libraries, this is recipe is based on
the zc.recipe.cmmi, it downloads and compiles a subversion release, additionally it executes the
commands to compile and install the python subversion bindings. This recipe assumes the usage of a python
with developer headers, and a swig installation, both can be passed in via the extra_options section,
if you have installed them in custom locations or via buildout.

a note of caution regarding python subversion bindings, releases prior to 1.5.0 have memory leaks in the
bindings api.


an example buildout part::

  [subversion]
  recipe=ore.recipe.svnlib
  url=http://subversion.tigris.org/downloads/subversion-1.5.0-rc4.tar.bz2
  extra_options=--without-apxs

