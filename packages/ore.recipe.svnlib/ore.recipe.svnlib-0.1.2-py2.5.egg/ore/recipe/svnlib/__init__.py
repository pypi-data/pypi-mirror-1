##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# Parts Copyright (c) 2008 Kapil Thangavelu <kapil.foss@gmail.com>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zc.recipe.cmmi import Recipe as BaseRecipe, getFromCache

"""
make swig-py

make install-swig-py

make install-swig-py swig_pydir
"""

import logging, os, shutil, tempfile, urlparse
import setuptools.archive_util


def system(c):
    if os.system(c):
        raise SystemError("Failed", c)
    
class Recipe( BaseRecipe ):

    def install( self ):
        logger = logging.getLogger(self.name)
        dest = self.options['location']
        url = self.options['url']
        extra_options = self.options.get('extra_options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        extra_options = ' '.join(extra_options.split())
        patch = self.options.get('patch', '')
        patch_options = self.options.get('patch_options', '-p0')

        fname = getFromCache(
            url, self.name, self.download_cache, self.install_from_cache)
 
        # now unpack and work as normal
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        logger.info('Unpacking and configuring')
        setuptools.archive_util.unpack_archive(fname, tmp)
          
        here = os.getcwd()
        if not os.path.exists(dest):
            os.mkdir(dest)

        try:
            os.chdir(tmp)
            try:
                if not os.path.exists('configure'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find configure")
                if patch is not '':
                    # patch may be a filesystem path or url
                    # url patches can go through the cache
                    if urlparse.urlparse( patch, None)[0] is not None:
                        patch = getFromCache( patch
                                            , self.name
                                            , self.download_cache
                                            , self.install_from_cache
                                            )
                    system("patch %s < %s" % (patch_options, patch))
                system("./configure --prefix=%s %s" %
                       (dest, extra_options))
                system("make")
                system("make install")
                system("make swig-py")
                system("make install-swig-py DESTDIR=%s"%dest)
            finally:
                os.chdir(here)
        except:
            shutil.rmtree(dest)
            raise

        return dest




        


        


        
