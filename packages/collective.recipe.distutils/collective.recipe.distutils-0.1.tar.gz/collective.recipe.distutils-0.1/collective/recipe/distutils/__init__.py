import logging, os, sys, shutil, tempfile
import urllib2
import urlparse
import sha
import datetime
import setuptools.archive_util
import zc.buildout

def system(c):
    if os.system(c):
        raise SystemError('Failed', c)

class Recipe(object):
    """
    Downloads and installs a distutils Python distribution.
    """
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout, self.name, self.options = buildout, name, options
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], 'site-packages')
        
        # If 'download-cache' has not been specified,
        # fallback to buildout/downloads
        buildout['buildout'].setdefault(
            'download-cache', 
            buildout['buildout'].get(
                'download-cache', 
                os.path.join(
                    buildout['buildout']['directory'], 'downloads'
                )
            )
        )
        self.download_cache = os.path.join(
            buildout['buildout']['directory'],
            buildout['buildout'].get('download-cache'),
            'distutils'
        )
        self.install_from_cache = buildout['buildout'].get('install-from-cache')

    def install(self):
        dest = self.options['location']
        url = self.options['url']
        build_ext = self.options.get('build_ext')
        fname = getFromCache(
            url, self.name, self.download_cache, self.install_from_cache)
        
        tmp = tempfile.mkdtemp('buildout-' + self.name)
        self.logger.info('Unpacking and configuring')
        setuptools.archive_util.unpack_archive(fname, tmp)
        here = os.getcwd()
        if not os.path.exists(dest):
            os.makedirs(dest)
        
        try:
            os.chdir(tmp)
            try:
                if not os.path.exists('setup.py'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find setup.py")
                cmd = '''"%s" setup.py -q install \
--install-purelib="%s" --install-platlib="%s"''' % (sys.executable, dest, dest)
                if build_ext:
                    cmd += ' build_ext %s' % build_ext
                system(cmd)
            finally:
                os.chdir(here)
        except:
            os.rmdir(dest)
            raise
        
        return [dest]

    def update(self):
        pass


def getFromCache(url, name, download_cache=None, install_from_cache=False):
    # borrowed from zc.recipe.cmmi
    if download_cache:
        cache_fname = sha.new(url).hexdigest()
        cache_name = os.path.join(download_cache, cache_fname)
        if not os.path.isdir(download_cache):
            os.mkdir(download_cache)

    _, _, urlpath, _, _ = urlparse.urlsplit(url)
    filename = urlpath.split('/')[-1]

    # get the file from the right place
    fname = tmp2 = None
    if download_cache:
        # if we have a cache, try and use it
        logging.getLogger(name).debug(
            'Searching cache at %s' % download_cache)
        if os.path.isdir(cache_name):
            # just cache files for now
            fname = os.path.join(cache_name, filename)
            logging.getLogger(name).debug(
                'Using cache file %s' % cache_name)

        else:
            logging.getLogger(name).debug(
                'Did not find %s under cache key %s' % (filename, cache_name))

    if not fname:
        if install_from_cache:
            # no file in the cache, but we are staying offline
            raise zc.buildout.UserError(
                "Offline mode: file from %s not found in the cache at %s" %
                (url, download_cache))
        try:
            # okay, we've got to download now
            # XXX: do we need to do something about permissions
            # XXX: in case the cache is shared across users?
            tmp2 = None
            if download_cache:
                # set up the cache and download into it
                os.mkdir(cache_name)
                fname = os.path.join(cache_name, filename)
                if filename != "cache.ini":
                    now = datetime.datetime.utcnow()
                    cache_ini = open(os.path.join(cache_name, "cache.ini"), "w")
                    print >>cache_ini, "[cache]"
                    print >>cache_ini, "download_url =", url
                    print >>cache_ini, "retrieved =", now.isoformat() + "Z"
                    cache_ini.close()
                logging.getLogger(name).debug(
                    'Cache download %s as %s' % (url, cache_name))
            else:
                # use tempfile
                tmp2 = tempfile.mkdtemp('buildout-' + name)
                fname = os.path.join(tmp2, filename)
                logging.getLogger(name).info('Downloading %s' % url)
            open(fname, 'w').write(urllib2.urlopen(url).read())
        except:
            if tmp2 is not None:
               shutil.rmtree(tmp2)
            if download_cache:
               shutil.rmtree(cache_name)
            raise

    return fname
