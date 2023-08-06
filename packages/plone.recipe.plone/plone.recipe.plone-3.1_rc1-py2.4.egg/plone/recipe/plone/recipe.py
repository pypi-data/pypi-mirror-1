import os.path
import re

import plone.recipe.distros
import zc.recipe.egg

import dist_plone.platforms.independent

egg_name_re = re.compile(r'(\S+?)([=<>!].+)')

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        
        self.dist = dist_plone.platforms.independent.Distribution()
        
        # These options are passed onto the plone.recipe.distros recipe
        
        download_data = self.plone_downloads()
        
        options.setdefault('urls', download_data['urls'])
        options.setdefault('nested-packages', download_data['nested'])
        options.setdefault('version-suffix-packages', download_data['suffixed'])
        
        self.distros = plone.recipe.distros.Recipe(buildout, name, options)
        
        # These are passed onto zc.recipe.egg.
        options['eggs'] = self.plone_eggs()
        
        global_links = buildout['buildout'].get('find-links')
        find_links = "%s\n%s" % (global_links, 'http://dist.plone.org',)
        options.setdefault('find-links', find_links)
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        # These options are set, but not used. Another recipe may reference it
        # to know which version of Zope Plone prefers
        options.setdefault('zope2-url', self.dist.zope.download_url)
        options.setdefault('python-url', self.dist.python.download_url)
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['location'] = options['products'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name
            )

    def install(self):
        options = self.options
        location = options['location']
        
        self.egg.install()
        self.distros.install()
        
        return location

    def update(self):
        pass

    def plone_eggs(self):
        """Read the eggs from dist_plone
        """
        
        egg_spec = self.options.get('eggs', '')
        explicit_eggs = {}
        for spec in egg_spec.split():
            name = spec
            version = ''
            match = egg_name_re.match(spec)
            if match:
                name = match.groups(1)
                version = match.groups(2)
            explicit_eggs[name] = version
        
        eggs = []
        for pkg in self.dist.core_packages:
            name = pkg.name
            if name in explicit_eggs:
                eggs.append(name + explicit_eggs[name])
                del explicit_eggs[name]
            else:
                if pkg.version is not None:
                    name += "==%s" % pkg.version
                eggs.append(name)
        
        for name, version in explicit_eggs.items():
            eggs.append(name + version)
        
        return '\n'.join(eggs)
        
    def plone_downloads(self):
        """Get all Plone product tarballs to download
        """
        urls = []
        nested = []
        suffixed = []
        
        for pkg in self.dist.core + self.dist.addons:
            url = pkg.download_url
            name = url.split('/')[-1]
            
            urls.append(url)
            
            # XXX: This isn't entirely right - there may be another reason
            # why we rename the package, but plone.recipe.distros isn't any 
            # smarter
            if pkg.productdir_rename:
                suffixed.append(name)
                
            # XXX: Similarly, it's not given that all bundles work like this
            if pkg.type.lower() == 'bundle':
                nested.append(name)
        
        return dict(urls='\n'.join(urls),
                    nested='\n'.join(nested),
                    suffixed='\n'.join(suffixed))