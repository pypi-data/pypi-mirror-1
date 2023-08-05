import logging, os

import pkg_resources

import zc.buildout
import zc.recipe.egg

logger = logging.getLogger('iwm.recipe.svncheckout')


class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options.setdefault('revision', 'HEAD')

        self.revision = options.get('revision')
        self.location = options['location']
        self.url = options['url']
	self.target = options.get('target', self.location)
        self.newest = (
            buildout['buildout'].get('offline', 'false') == 'false'
            and
            buildout['buildout'].get('newest', 'true') == 'true'
            )
	self.root_directory = buildout['buildout']['directory']

    def update(self):
        """Update the zope.file checkout.

        Does nothing if buildout is in offline mode.

        """
        if not self.newest:
            return self.target

        os.chdir(self.target)
        stdin, stdout = os.popen4('svn up -r %s' % self.revision)
        stdin.close()
        stdout.read()
        stdout.close()

        return self.target

    def install(self):
        """Checkout a Zope 3 working copy.

        Fails if buildout is running in offline mode.

        """
        os.chdir(self.root_directory)

        assert os.system('svn co -r %s %s %s' % (
            self.revision, self.url, self.target)) == 0
        return self.target
