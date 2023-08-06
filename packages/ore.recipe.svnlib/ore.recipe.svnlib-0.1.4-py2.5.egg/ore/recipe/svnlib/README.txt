ore.recipe.svnlib
-----------------

A Recipe for downloading and compiling the python subversion
libraries, this is recipe is based on the zc.recipe.cmmi, and accepts
all the same recipe options. it downloads and compiles a subversion
release, additionally it executes the commands to compile and install
the python subversion bindings. This recipe assumes the usage of a
python with developer headers, and a swig installation, both can be
passed in via the extra_options section, if you have installed them in
custom locations or via buildout.

a note of caution regarding python subversion bindings, releases prior
to 1.5.0 have memory leaks in the bindings api.


an example buildout part, and another part which uses it to construct
a python interpreter with the svn python bindings::

  [subversion]
  recipe=ore.recipe.svnlib
  url=http://subversion.tigris.org/downloads/subversion-1.5.2.tar.bz2
  extra_options=--without-apxs

  [python]
  recipe=zc.recipe.egg
  eggs = 
  interpreter = python
  extra-paths = 
    $[subversion:location}/lib/svn-python


Changes
-------

 - 0.1.3 ( 2008.5.8 )

   both swig_pydir and swig_pydir_extra need to be passed in
   addition to destdir to give arbitrary location installation,
   the swig helper libdir is installed into the --prefix by 
   default.

 - 0.1.2 ( 2008.5.7 )


 - 0.1.1 ( 2008.5.5 )

 - 0.1.0 ( 2008.5.5 )

   First Release
