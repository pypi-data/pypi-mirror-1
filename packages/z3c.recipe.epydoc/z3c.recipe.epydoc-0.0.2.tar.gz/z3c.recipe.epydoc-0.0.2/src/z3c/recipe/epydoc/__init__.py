"""
Generates epydoc recipe
@author: Andrew Mleczko
"""

import sys
import os
from os.path import join, dirname, isdir

import zc.recipe.egg
import zc.buildout.easy_install
import pkg_resources

class EpyDoc(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = join(buildout['buildout']['bin-directory'],
                                 options.get('script', self.name))
        self.egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)
        self.doc = options['doc']

    def install(self):
        installed = []
        eggs, workingSet = self.egg.working_set()
        # Create parts directory for configuration files.
        installDir = join(self.buildout['buildout']['parts-directory'], self.name)
        if not isdir(installDir):
            os.mkdir(installDir)

        args = {'doc' : self.doc, 'output' : installDir}

        #for each egg listed as a buildout option, create a configuration space.  
        installed.extend(zc.buildout.easy_install.scripts(
            [(self.options['script'],
              'z3c.recipe.epydoc',
              'main'),
             ],
            workingSet,
            self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments = "%r" % args,
            ))

        return installed

    update = install


def main(args):
    from epydoc.cli import cli
    from zope.dottedname.resolve import resolve
    path =  resolve(args['doc']).__path__[0]
    argv = [sys.argv[0], '-o', args['output'], path, '-v', '--debug'] + sys.argv[1:]
    sys.argv = argv
    print "building docs for", args['doc']
    cli()
