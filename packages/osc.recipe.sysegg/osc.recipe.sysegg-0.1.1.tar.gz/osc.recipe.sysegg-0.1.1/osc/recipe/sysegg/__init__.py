import os
import logging
import pkg_resources

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options.setdefault('eggs', '')

    def install(self):
        log = logging.getLogger(self.name)
        eggs = self.options['eggs']
        eggs = eggs.split('\n')
        
        dev_egg_dir = self.buildout['buildout']['develop-eggs-directory']
        
        for egg in eggs:
            try:
                dist = pkg_resources.require(egg)[0]
                egg_egg_link = os.path.join(dev_egg_dir,
                                                '%s.egg-link' % dist.project_name)
                f = open(egg_egg_link, 'w')
                f.write(dist.location)
                f.close()
                log.info('Using %s for %s' % (dist.location, egg))
            except pkg_resources.DistributionNotFound:
                log.warn('No system distribution for %s found.' % egg)
        return ()

    update = install