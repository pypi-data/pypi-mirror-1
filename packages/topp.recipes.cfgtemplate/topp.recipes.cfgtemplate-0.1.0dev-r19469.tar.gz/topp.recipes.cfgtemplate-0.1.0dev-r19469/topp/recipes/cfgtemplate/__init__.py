# -*- coding: utf-8 -*-
"""Recipe cfgtemplate"""

from ConfigParser import SafeConfigParser
from template import CurlyBraceTemplate
import os
import sys

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def get_section_map(self, config, section, merge_default=True):
        """
        Returns a dictionary of all of the options and option values
        for the specified section of the config object.  Creates the
        section if it doesn't already exist.

        If merge_default is True, then the values from the default
        section will be merged into the results.  The value that is in
        the specific section will win in a conflict.
        """
        if not config.has_section(section):
            config.add_section(section)
        section_map = dict()
        if merge_default:
            section_map = config.defaults()
        options = config.options(section)
        for option in options:
            section_map[option] = config.get(section, option)
        return section_map

    def install(self):
        """Installer"""
        subfile = self.options.get('subfile', 'cfgsubs.cfg')
        changed = False
        config = SafeConfigParser()
        if os.path.exists(subfile):
            config.read(subfile)

        for part in self.buildout:
            if part in ('buildout', self.name):
                continue
            section_map = self.get_section_map(config, part)

            for key in self.buildout[part]:
                ### XXX move to a method
                subs_matched = False
                unrendered = self.buildout[part][key]
                tmpl = CurlyBraceTemplate(unrendered)
                while not subs_matched:
                    try:
                        rendered = tmpl.substitute(section_map)
                    except KeyError:
                        exc_info = sys.exc_info()
                        missing = exc_info[1].args[0]
                        new_sub = raw_input("INPUT REQUIRED: %s:%s --> " %
                                            (part, missing))
                        config.set(part, missing, new_sub)
                        section_map = self.get_section_map(config, part)
                        changed = True
                    else:
                        subs_matched = True
                # XXX we write it back whether it changed or not, should we?
                self.buildout[part][key] = rendered

        if changed:
            outfile = open(subfile, 'w')
            config.write(outfile)
            outfile.close()
                
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        
        # XXX We return a file we didn't actually create to force this
        # recipe to be reinstalled on every run; maybe this should be
        # in the constructor or elsewhere?
        nofile = os.path.join(self.buildout["buildout"]["parts-directory"],
                              self.name)
        return (nofile,)

    def update(self):
        """Updater"""
        pass
