## -*- coding: utf-8 -*-
############################################
## File : __init__.py<2>
## Author : Sylvain Viollon
## Email : sylvain@infrae.com
## Creation Date : Fri Feb 15 17:03:31 2008 CET
## Last modification : Fri Feb 15 17:23:27 2008 CET
############################################

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: __init__.py 27685 2008-02-15 16:43:48Z sylvain $"


from zc.buildout.buildout import Buildout
import os
import os.path


class SubBuildout(Buildout):
    """Adapt buildout to run in himself.
    """

    def __init__(self, parent, config, options, **kwargs):
        """Init a buildout from his parent.
        """
        # Use same logger
        self._logger = parent._logger 
        self._log_level = parent._log_level

        # Use same option (for some of them)
        for opt in ('offline', 'verbosity', 'newest',):
            if opt in parent['buildout']:
                options.append(('buildout', opt, parent['buildout'][opt],))

        # Init the buildout.
        Buildout.__init__(self, config, options, **kwargs)

    def _setup_logging(self):
        """We don't want to setup any logging, since it's already done
        by the parent.
        """
        pass
    

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.config = options.get('config', 'buildout.cfg')

    def _run(self, bootstrap=False):
        """Run buildout.
        """
        current = os.getcwd()
        location = self.options['path']
        os.chdir(location)

        options = []
        options.append(('buildout', 'directory', location))

        if bootstrap:
            buildout = SubBuildout(self.buildout, self.config, list(options))
            buildout.bootstrap([])

        # We don't want this option when running the bootstrap to not
        # override first one buildout script.
        if self.options.get('merge-bin', False):
            options.append(('buildout', 
                            'bin-directory', 
                            self.buildout['buildout']['bin-directory']))

        buildout = SubBuildout(self.buildout, self.config, options)
        buildout.install([])

        os.chdir(current)
        return os.path.join(location, 'parts')
        

    def update(self):
        """Update the buildout tree.
        """
        return self._run()

    def install(self):
        """Install the buildout tree.
        """
        return self._run(bootstrap=True)

