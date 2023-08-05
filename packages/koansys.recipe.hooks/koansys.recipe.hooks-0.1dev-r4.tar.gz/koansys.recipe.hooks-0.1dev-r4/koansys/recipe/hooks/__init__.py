import zc.buildout
import logging
import os
import imp

class Recipe:
    """zc.buildout recipe for running hooks"""

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.log = logging.getLogger(self.name)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options['prefix'] = options['location']

    def update(self):
        pass

    def call_script(self, script):
        """This method is copied from z3c.recipe.runscript.

        See http://pypi.python.org/pypi/z3c.recipe.runscript for details.
        """
        filename, callable = script.split(':')
        filename = os.path.abspath(filename)
        module = imp.load_source('script', filename)
        # Run the script with all options
        getattr(module, callable.strip())(self.options, self.buildout)

    def install(self):
        hooks = self.options.get('hooks')
        if not hooks:
            msg = "No 'hooks' specified"
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)
        for hook in hooks.strip().split():
            self.log.info('Executing hook=%s' % hook)
            try:
                self.call_script(hook)
            except Exception, e:
                self.log.error('Compilation error. Exception=%s' % e)
                raise
        return []                       # I don't know what this is for

    def update(self):
        self.log.info("Update simply calls the install hooks")
        install(self)
