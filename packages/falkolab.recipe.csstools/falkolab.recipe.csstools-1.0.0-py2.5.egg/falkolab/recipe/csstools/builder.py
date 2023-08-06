# -*- coding: utf-8 -*- #
from falkolab.recipe.csstools import combiner

class CSSBuilder(object):
    def __init__(self, buildout, name, options):
        self.defaults = {'resource-dir':options.get('resource-dir')}
        
        self.options = { 'targetencoding': 'utf-8',
                         'compress': False}
        
        self.options.update(options)
        
        self.defaults.update(self.options)
        
        self.buildout = buildout
        if self.options.get('output-name') is not None:
            #@@ detect if config only has 1 section
            assert self.options.get('section'), ValueError('output-name var requires "section" var to select config section')

        self.minify = self.options.get('compress', False)
        if self.minify not in ('True', 'true', '1'):
            self.minify = False
        else:
            self.minify = True
        
        self.section = self.options.get('section', None)
        self.sourceencoding = self.options.get('sourceencoding', None)
        self.targetencoding = self.options.get('targetencoding', None)

    
    def install(self):
        self.combiner = combiner.Combiner.getCombinerFromConfig(self.options.get('config'),
                                          output_dir=self.options.get('output-dir'),
                                          defaults=self.defaults,
                                          printer=self.buildout._logger.info) 
        files = self.combiner.run(minify=self.minify, section=self.section,
                               sourceencoding=self.sourceencoding, 
                               targetencoding=self.targetencoding)
        return files
    
    update = install
        