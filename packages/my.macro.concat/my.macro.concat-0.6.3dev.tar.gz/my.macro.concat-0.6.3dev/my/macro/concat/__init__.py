# -*- coding: utf-8 -*-
"""Recipe concat"""

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.target=options.get("target", None)
        self.option=options.get("option", None)
        self.parts = options.pop('parts', name).strip().split()
        #self.parts=options.get("parts", None)

        if not (self.target and self.option and self.parts):
            self.logger.error("""You need to specify a target part, an option
                    and parts from which concat the option on the target part""")
            raise zc.buildout.UserError("options missing")

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        result = []
        for part in self.parts:
            result.append(self.buildout[part][self.option])
        self.buildout[self.target][self.option] = '\n'.join(result)
        return self.buildout #tuple()

    update = install

    #def update(self):
    #    """Updater"""
    #    pass
