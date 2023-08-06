# Plone Distribution Script
# by Simon Eisenmann, 2004.
# for questions contact simon@longsleep.org
#
# $Rev: 1.15 $
# $Date: 2004-05-11 19:14:24 +0200 (Tue, 11 May 2004) $
"""
This script:

 1) Gets the PloneBase-X.Y tarball (contains only CMFPlone dir, nothing
    else) from SF.net (I would like to move it away from SF, though - since
    it's not meant for public consumption).

 2) Adds the Plone Core specified products, and creates PloneCore-X.Y

 3) Adds the cross-platform additions that consitute Plone, and creates
    Plone-X.Y

 The installers are normally built on top of [3]. Plone Core[2] is for
 people who just want the minimal Plone install with minimal dependencies,
 aka. People Who Know What They Want.

 Which means any platform-specific installers:

 a) Get Plone-X.Y.tgz [3]

 b) Add their platform-specific additions (PIL, win32all, etc)

 c) Create the installer

 Read http://plone.org/development/teams/release/ for definitions and
 further explanations.

 -- Alexander Limi
"""

import itarfile as tarfile # NOTE: pythons tarfile is borked, itarfile is a patched version
import zipfile
import time
import os, getopt, sys, subprocess
import tempfile, urllib
import urlparse

from distutils.dir_util import mkpath, copy_tree, remove_tree
from distutils.file_util import move_file

from imp import find_module, load_module

__version__ = "$Revision: 1.15 $"[11:-1]

sourceforge_mirrors = ("umn osdn switch jaist heanet ovh "
                       "belnet kent easynews puzzle").split()

class Software:
    """ general software """
    type = 'Software'

    name = None
    download_url = None
    archive_rename = None
    productdir_rename = None
    filename = None
    parent = None
    version = None

    destination = 'downloads'

    def __init__(self, name, download_url, productdir=None, archive_rename=None, version=None):
        self.name = name
        self.download_url = download_url
        self.productdir_rename = productdir
        self.archive_rename = archive_rename
        self.version = version


class Bundle(Software):
    """ a archive which contains multiple other parts """

    type = 'Bundle'
    items = None

    destination = 'downloads'

    def __init__(self, name, download_url, mapping):
        # define a subfolder -> class mapping here to
        # specify the contents of this bundle

        Software.__init__(self, name, download_url)

        self.items = []
        for n, k in mapping.items():
            c = k(n, None)
            c.parent = self # set ourselfs as source for this file
            self.items.append(c)


class PyModule(Software):
    """ python module """

    type = 'PyModule'
    destination = 'lib/python'

    def post_extract(self, destination, me):
        cwd=os.getcwd()
        me=me.split('/')[0]
        os.chdir(os.path.join(destination, me))
        res=subprocess.call(["python2.4", "setup.py", "install_lib",
            "--install-dir=%s" % destination])
        if res!=0:
            raise RuntimeError, "Failed to setup package"

        os.chdir(destination)
        subprocess.call(["rm", "-rf", me])
        os.chdir(cwd)
        


class ZProduct(Software):
    """ zope product """

    type = 'ZProduct'
    destination = 'Products'


class Parameters:

    _eaten = []

    def feed(self, p, arg):
        setattr(self, p, arg)
        if not self.given(p): self._eaten.append(p)

    def given(self, p):
        return p in self._eaten


USAGE="""Plone Distribution script %s.
Usage: python dist_plone.py [--download|--build] [OPTION]...

%sParameters:
  --help                   display this usage information and exit.
  --target=TARGET          selects package definition to use.
  --modules=DIRECTORY      directory where target module is to be found (defaults to dist_plone.platforms).
  --dest=DESTINATION       destination folder (default is ./build).
  --core                   use minimal mode.
  --build                  builds tarball mode.
  --download               download only mode.
  --downloaddir            download to this directory, or use file that already exists there.

Mail bug reports and suggestions to <simon@longsleep.org>.
"""


class Plone:

    version = None

    parameters = None
    data = []

    # getopt command line parameters
    short_options = ""
    long_options = ["help", "target=", "modules=", "dest=", "core", "build", "download", "downloaddir="]

    def setup(self):
        self.basefolder = tempfile.mkdtemp()
        # cheat to get a temp dir with proper mode (755)
        os.rmdir(self.basefolder)
        os.mkdir(self.basefolder)

        if not self.parameters.given('dest'):
            dest = os.path.join(self.parameters.dest, 'build')
            try: os.mkdir(dest)
            except: pass
            self.parameters.feed('dest', dest)

    def run(self, command):
        command = " ".join(command)
        print "command is %s" % repr(command)
        os.system(command)

    def usage(self, s=''):
        print USAGE % (__version__.strip(), s)

    def main(self):

        try:
            opts, args = getopt.getopt(sys.argv[1:],
                                       self.short_options,
                                       self.long_options,
                                       )
        except getopt.GetoptError:
            # print help information and exit
            self.usage()
            sys.exit(1)

        # default parameter values
        dest = os.getcwd()
        target = 'independent'
        modules = None
        parameters = Parameters()
        parameters.dest = dest
        parameters.target = target
        parameters.modules = modules

        # go through each cmd line argument
        for cmd, arg in opts:

            if cmd in ('--help',):
                self.usage()
                sys.exit()

            if cmd in ('--dest',):
                dest = arg
                assert os.path.isdir(dest)
                parameters.feed('dest', dest)

            if cmd in ('--core',):
                core = True
                parameters.feed('core', core)

            if cmd in ('--build',):
                build = True
                parameters.feed('build', build)

            if cmd in ('--target',):
                target = arg
                parameters.feed('target', target)

            if cmd in ('--modules',):
                modules = arg
                parameters.feed('modules', modules)

            if cmd in('--download',):
                download = True
                parameters.feed('download', download)

            if cmd in('--downloaddir',):
                downloaddir = arg
                parameters.feed('downloaddir', downloaddir)

        # check for errors
        errors = []
        if parameters.given('download') and parameters.given('build'):
            errors.append('Either --download or --build mode is allowed')
        if not parameters.given('download') and not parameters.given('build'):
            errors.append('You need to give either --download or --build')

        # get distribution
        if not modules:
            load='platforms.%s' % target
            try: Distribution = __import__(load, globals(), locals(), 'Distribution')
            except:
                raise
                Distribution = None
        else:
            try:
                fp, pathname, description = find_module(target, [modules])
                try:
                    Distribution = load_module(target, fp, pathname, description)
                finally:
                    if fp: fp.close()
            except ImportError:
                errors.append("Target module '%s' cannot be found in '%s'" % (target, modules))
                Distribution = None
        if Distribution:
            Distribution = Distribution.Distribution
            dist=Distribution()
        else:
            errors.append('Platform %s is not supported' % target)

        # got errors?
        if len(errors):
            errors = map(lambda x: 'GetoptError: %s.' % str(x), errors)
            errors = '\n'.join(errors)
            errors = '%s\n\n' % errors
            self.usage(errors)
            sys.exit(1)

        parameters.feed('dist', dist)
        # remember parameters
        self.parameters = parameters

        self.setup()
        self.download()
        self.build()
        self.cleanup()


    def download(self):

        download_destination = self.basefolder
        if not self.parameters.given('build') and self.parameters.given('dest'):
            download_destination=self.parameters.dest
        if self.parameters.given('downloaddir'):
            download_destination=self.parameters.downloaddir
        if not os.path.exists(download_destination):
            os.makedirs(download_destination)

        contents = os.path.join(download_destination, 'CONTENTS.txt')
        contents = open(contents, "w")
        contents.write("The following packages were downloaded at %s.\n" % time.asctime())

        data = []
        def dl_callback(ob):
            if ob.archive_rename:
                filename = ob.archive_rename
            else:
                filename = os.path.split(ob.download_url)[1]
            filename = os.path.join(download_destination, filename)
            source = ob.download_url
            if not os.path.isfile(filename):
                print "Retrieving %s.\n" % ob.name,
                print "--> %s" % source
                print "to:", filename
                source = retrieve_file(source, filename)
                print
            else:
                print "Not retrieving %s." % ob.name,
                print filename, "already exists."
            ob.filename = filename
            contents.write("%s - %s\n" % (ob.name, source))
            data.append(ob)

        # walk with our callback
        for product in self.walk_products():
            dl_callback(product)

        for package in self.walk_packages():
            dl_callback(package)

        # close log file
        contents.close()

        # store our data
        self.data = data


    def walk_products(self):
        dist = self.parameters.dist
        walk = ('core',)
        if not self.parameters.given('core'):
            walk=walk+('addons', )

        for w in walk:
            for c in getattr(dist, w, []):
                yield c


    def walk_packages(self):
        dist = self.parameters.dist
        walk = ('core_packages',)
        if not self.parameters.given('core'):
            walk=walk+('addons_packages', )

        for w in walk:
            for c in getattr(dist, w, []):
                yield c


    def build(self):
        if not self.parameters.given('build'):
            return

        got = self.data

        items = []
        def expand(ob):
            if hasattr(ob,  'items'):
                for item in ob.items:
                    expand(item)
            else:
                items.append(ob)

        # expand bundles
        for item in got:
            expand(item)

        # check if we have products only
        products = [x for x in items if x.type=='ZProduct']

        # check if we only got products
        if len(products) == len(items):
            # if we only have products reset their destination
            for ob in items:
                ob.destination=''

        # move stuff to their destinations
        for ob in items:
            destination = os.path.join(self.basefolder, ob.destination)
            move = None
            visible_name = ob.name

            search = None
            if ob.parent:
                search = ob.name
                ob=ob.parent
                move=os.path.join(destination, search)
                destination=os.path.join(self.basefolder, ob.destination)

            filename = ob.filename

            # make the path (including all anchestors)
            mkpath(destination, verbose=1)

            # extract the files
            print "Processing %s %s\n%s" % (ob.type, visible_name, filename)

            # determine type
            if tarfile.is_tarfile(filename):
                ar = tarfile.TarFileCompat(filename,'r',tarfile.TAR_GZIPPED)
            elif zipfile.is_zipfile(filename):
                ar = zipfile.ZipFile(filename)
            else:
                raise IOError, "file '%s' is of unusable archive type. Only ZIP and compressed TAR files can be handled." % filename

            # do extraction
            productdir_rename = ob.productdir_rename
            base=''
            for f in ar.namelist():
                # zipfile returns dirs, tarfile compat does not. ignore dirs
                if not os.path.split(f)[1]:
                    continue
                need=1
                if search:           # do we need to include this directory?
                    need=0
                    name = f.split('/')
                    if len(name):
                        if name[0] == search:
                            need=1
                        elif len(name)>1 and name[1] == search:
                            need=1
                if need:
                    try: base=name[0]
                    except: pass

                    # do Product directory rename if needed
                    if productdir_rename and f.find(productdir_rename) == 0:
                        new_f = f[len(productdir_rename)+1:]
                        new_f = os.path.join(ob.name, new_f)
                        ext_fname = os.path.join(destination,new_f)
                    else:
                        ext_fname = os.path.join(destination,f)

                    # make destination directories and do extraction
                    try: os.makedirs(os.path.split(ext_fname)[0])
                    except OSError: pass
                    data = ar.read(f)
                    dest = open(ext_fname,'w')
                    dest.write(data)
                    dest.close()
                else:
                    continue

            # close archive file
            ar.close()

            if hasattr(ob, 'post_extract'):
                maindir=os.path.split(f)[0]
                ob.post_extract(destination, maindir)

            # move directory if needed
            if move:
                source = os.path.join(destination,base,search)
                destination = move
                copy_tree(source, destination)
                remove_tree(os.path.split(source)[0])
            else:
                destination = os.path.join(destination, ob.name)

            # check version.txt
            try:
                contents = os.listdir(destination)
                check = [x.lower() for x in contents]
                index=check.index('version.txt')
            except:
                index = []
            if index != []:
                # found a version
                version = contents[index]
                fp = open(os.path.join(destination, version), 'r')
                version = fp.read().strip()
                fp.close()
                print "--> Version %s." % str(version)
            else:
                version = 'unkownn'
                print "--> NO VERSION."

            # store version
            if visible_name in ('CMFPlone', ):
                # XXX: hack Plone package version
                version = version.split()[0]
                self.version = version
                self.plonepackage = destination
                print "--> Used as Plone Package Version."

        # Copy some documentation from inside CMFPlone to the toplevel
        docs = getattr(self.parameters.dist, 'documentation', ['README.txt'])
        for doc in docs:
            subprocess.call(["cp", os.path.join(self.plonepackage, doc), self.basefolder])
        
        # cleanup for packaging
        if not self.parameters.given('downloaddir'):
            for ob in self.data:
                filename = ob.filename
                os.unlink(filename)

        # Remove generate .pyc files
        subprocess.call(["find", self.basefolder, "-name", "*.pyc",
            "-exec", "rm", "{}", ";"])

        # check for empty folders in base
        for f in os.listdir(self.basefolder):
            f=os.path.join(self.basefolder, f)
            if not os.path.isdir(f): continue
            else:
                if not len(os.listdir(f)):
                    # remove empty folders
                    remove_tree(f)

        # XXX: hack
        # actually remove PloneTranslations
        #if "PloneTranslations" in os.listdir(self.basefolder):
        #    f = os.path.join(self.basefolder, "PloneTranslations")
        #    remove_tree(f)

        # create new package
        name = getattr(self.parameters.dist, 'name', 'Plone')
        version = getattr(self.parameters.dist, 'version', self.version)
        if self.parameters.given('core'): name="%sCore" % name
        target = self.parameters.dist.target.lower()
        name = "%s-%s" % (name, version)
        if target not in ('independent',):
            name="%s-%s" % (name, target)
        filename = "%s.tar.gz" % name
        print "Creating Tarball %s." % filename
        filename = os.path.join(self.parameters.dest, filename)

        # make tar
        tar = tarfile.open(filename, 'w:gz')
        tar.posix = False
        tar.add(self.basefolder, '/%s' % name)
        tar.close()

        print "Wrote Tarball to %s" % filename



    def cleanup(self):
        print "Cleaning up %s." % self.basefolder
        remove_tree(self.basefolder)
        pass

class TheHook:

    def __init__(self):
        self.seen = 0
        self.finished = False

    def __call__(self, blocknum, bs, size):
        self.seen += bs
        if blocknum == 0 or self.finished:
            # Ignore first call, it calls our hook before reading anything.
            return
        if self.seen > size:
            # Unfortnately, 'bs' is the block size, not the 'read
            # bytes', so this can easily exceed the size reported in
            # 'slow reads'.
            sys.stdout.write(' ' * (71 - (blocknum % 70)))
            sys.stdout.write(' [%3d%%]\n' % 100)
            sys.stdout.flush()
            self.finished = True
            return
        sys.stdout.write('.')
        sys.stdout.flush()
        if not blocknum % 70 or self.seen == size:
            if self.seen == size:
                sys.stdout.write(' ' * (71 - (blocknum % 70)))
                self.finished = True
            done = (float(self.seen) / size) * 100
            sys.stdout.write(' [%3d%%]\n' % done)
            sys.stdout.flush()

def retrieve_file(source, filename):
    mirrors = None
    while True:
        try:
            urllib.urlretrieve(source, filename, reporthook=TheHook())
        except IOError, msg:
            print "Failed to retrieve '%s'" % source
            if not source.find('sourceforge') > 0:
                raise
            if mirrors is None:
                mirrors = iter(sourceforge_mirrors)
            scheme, netloc, path, query, fragment = urlparse.urlsplit(source)
            parts = netloc.split('.')
            try:
                netloc = '.'.join([mirrors.next()] + parts[1:])
            except StopIteration:
                raise IOError, msg
            source = urlparse.urlunsplit((scheme, netloc, path,
                                          query, fragment))
            print "Retrying with '%s'" % source
        else:
            break
    return source

# main class
if __name__ == '__main__':
    plone=Plone()
    plone.main()


