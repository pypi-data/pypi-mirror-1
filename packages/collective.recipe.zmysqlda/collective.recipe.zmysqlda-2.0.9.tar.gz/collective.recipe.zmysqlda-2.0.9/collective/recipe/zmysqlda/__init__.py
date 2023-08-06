#
# This recipe is based on plone.recipe.distros and dist_plone.py script.
# 

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import zc.buildout

sourceforge_mirrors = ("umn osdn switch jaist heanet ovh "
                       "belnet kent easynews puzzle").split()

class Recipe:
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        download_dir = self.buildout['buildout'].get('download-directory', \
                       self.buildout['buildout'].get('download-cache', \
                       os.path.join(self.buildout['buildout']['directory'],'downloads')))
                       
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            self.options.created(download_dir)
        source = 'ZMySQLDA'
        target = self.options.get('target')
        if target is None:
            target = os.path.join(self.buildout['buildout']['directory'], 'products')
        result = None
        if source is not None:
            url = 'http://heanet.dl.sourceforge.net/sourceforge/mysql-python/ZMySQLDA-2.0.8.tar.gz'
            tmp = tempfile.mkdtemp('buildout-'+self.name)
            try:
                fname = os.path.join(download_dir, url.split('/')[-1])
                mirrors = None
                # Have we already downloaded the file?
                if not os.path.exists(fname):
                    while True:
                        f = open(fname, 'wb')
                        try:
                            f.write(urllib2.urlopen(url).read())
                        except IOError, msg:
                            f.close()
                            # iterate through sourceforge mirrors
                            print "Failed to retrieve '%s'" % source
                            if not url.find('sourceforge') > 0:
                                raise
                            if mirrors is None:
                                mirrors = iter(sourceforge_mirrors)
                            scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
                            parts = netloc.split('.')
                            try:
                                netloc = '.'.join([mirrors.next()] + parts[1:])
                            except StopIteration:
                                raise IOError, msg
                            url = urlparse.urlunsplit((scheme, netloc, path,
                                                          query, fragment))
                            print "Retrying with '%s'" % url
                        else:
                            f.close()
                            break
                    
                setuptools.archive_util.unpack_archive(fname, tmp)
                # walk into tmp dir until 'source' directory is found 
                for dirname, dirs, files in os.walk(tmp):
                    if (source in dirs):
                        shutil.move(os.path.join(dirname, source), os.path.join(target, source))
                        result = os.path.join(target, source)
                        break
            finally:
                shutil.rmtree(tmp)                      
        return result                   

    def update(self):
        pass
        
