# -*- coding: utf-8 -*- #
from ConfigParser import ConfigParser
import logging, sys, os.path
from string import join
import cssutils
import codecs

from urlparse import urlparse

logger = logging.getLogger('jstools.merge')
SUFFIX_CSS = ".css"



class MissingImport(Exception):
    """Exception raised when a listed import is not found in the lib."""

class Combiner(ConfigParser):
    def __init__(self, output_dir, defaults=None, printer=logger.info):
        ConfigParser.__init__(self, defaults)
        self.output_dir = output_dir
        self.printer = printer
        
    @classmethod
    def getCombinerFromConfig(cls, path_to_config, output_dir, defaults=None, printer=logger.info):
        """Load up a list of config filenames in our combiner"""
        combiner = cls(output_dir, defaults=defaults, printer=printer)
        if isinstance(path_to_config, basestring):
            path_to_config = path_to_config,
        fns = combiner.read(path_to_config)
        assert fns, ValueError("No valid config files: %s" %fns)
        return combiner
    
    def assemble(self, cfg, depmap=None):
        sourcedir = cfg['root'] = cfg['root'].rstrip('/')
    
        # assemble all files in source directory according to config
        exclude = cfg['exclude']
       
        self.printer("Assembling files.")
        if(cfg['include']):
            self.printer('Include variable specified. Last and first variables will be ignored.')
            cfg['first'] = []
            cfg['last'] = []
        else:
            cfg['last'] = [filepath for filepath in cfg['last'] \
                        if filepath not in cfg['first'] \
                            and filepath not in exclude]
        
            cfg['first'] = [filepath for filepath in cfg['first'] \
                        if filepath not in cfg['last'] \
                            and filepath not in exclude]
        
        first = cfg['first']
        last = cfg['last']
        
        include = cfg['include'] = [filepath for filepath in cfg['include'] \
                   if filepath not in exclude]
        
        allIncludes = (first + include + last)
        
        filesList = [filepath for filepath in getCSSFilesList(sourcedir) \
                     if filepath not in exclude]
        
        self.printer("Check existenсe files.") 
        for filepath in allIncludes:
            if filepath not in filesList:
                raise MissingImport("File '%s' not found!" % filepath)
           
        # move forced first and last files to the required position 
        self.printer("Re-ordering files.")     
        if(include):
            order = allIncludes            
        else:
            order = first + [filepath
                     for filepath in filesList
                     if filepath not in allIncludes] + last
                     
        return [os.path.join(sourcedir, filepath) for filepath in order]


    key_list = 'include', 'exclude', 'last', 'first', 
    keys = 'license', 'root',

    def getSectionConfig(self, section):
        cfg = dict(self.items(section))
        for key in self.key_list:
            val = cfg.setdefault(key, [])
            if isinstance(val, basestring):
                cfg[key]=[x for x in val.split() if not x.startswith('#')]
        for key in self.keys:
            cfg.setdefault(key, None)
        return cfg


    def run(self, minify=False, section=None, sourceencoding=None, targetencoding=None):
        sections = self.sections()
        if section is not None:
            assert section in sections, ValueError("%s not in %s" %(section, sections))
            sections = [section]
        newfiles = []
        for section in sections:            
            header = "\nBuilding section: %s" % section
            self.printer("%s\n%s" % (header, "-" * len(header)))
        
            
            cfg = self.getSectionConfig(section)          
            
            result = []
            self.printer("Assembling section.")           
            files = self.assemble(cfg)            
            result = csscombine(files,sourceencoding=sourceencoding, 
                                   targetencoding=targetencoding, minify=minify,
                                   license=cfg['license'],
                                   logger=self.printer)                
                
            self.printer("\nTotal files processed: %d " % len(files))                 
                
            if cfg.has_key('output'):
                outputfilename = cfg['output']
            else:
                outputfilename = os.path.join(self.output_dir, section)

#            if cfg['license']:
#                self.printer("Adding license file: %s" %cfg['license'])
#                result = file(cfg['license']).read() + result

            self.printer("Writing to %s (%d KB).\n" % (outputfilename, int(len(result) / 1024)))
            file(outputfilename, "w").write(result)
            newfiles.append(outputfilename)
        return newfiles



def getCSSFilesList(sourcedir, suffix=SUFFIX_CSS):
    for root, dirs, files in os.walk(sourcedir):
        for filename in files:        
            if filename.endswith(suffix) and not filename.startswith("."):
                filepath = os.path.join(root, filename)[len(sourcedir)+1:]
                filepath = filepath.replace("\\", "/")
                yield filepath

def resolveImports(sheet, target=None, baseUrl=None):
    """Recurcively combine all rules in given `sheet` into a `target` sheet.

    :param sheet:
        in this given :class:`cssutils.css.CSSStyleSheet` all import rules are
        resolved and added to a resulting *flat* sheet.
    :param target:
        A :class:`cssutils.css.CSSStyleSheet` object which will be the resulting
        *flat* sheet if given
    :returns: given `target` or a new :class:`cssutils.css.CSSStyleSheet` object
    """
    if not target:
        target = cssutils.css.CSSStyleSheet()
   
    if not baseUrl:
        baseUrl = os.path.split(urlparse(sheet.href)[2])[0]
        
    sheetBaseUrl = urlparse(sheet.href)[2]
    if(sheetBaseUrl.startswith(baseUrl)):
        path = sheetBaseUrl[len(baseUrl)+1:]
    else:
        path = sheet.href

    target.add(cssutils.css.CSSComment(cssText=u'/* START %s */' % path))
    for rule in sheet.cssRules:
        if rule.type == rule.CHARSET_RULE:
            pass
        elif rule.type == rule.IMPORT_RULE:
            cssutils.log.info(u'Processing @import %r' % rule.href, neverraise=True)
            if rule.styleSheet:
                resolveImports(rule.styleSheet, target, baseUrl)
            else:
                cssutils.log.error(u'Cannot get referenced stylesheet %r' %
                          rule.href, neverraise=True)
                target.add(rule)
        else:
            target.add(rule)
    target.add(cssutils.css.CSSComment(cssText=u'/* END %s */' % path))
    return target

def csscombine(files, sourceencoding=None, targetencoding=None, minify=True, 
               license=None, logger=logger.info):
    """Combine sheets referred to by @import rules in given CSS proxy sheet
    into a single new sheet.

    :returns: combined cssText, normal or minified
    :Parameters:
        `files`
            files to a CSSStyleSheet which imports other sheets which
            are then combined into one sheet
        `targetencoding`
            encoding of the combined stylesheet, default 'utf-8'
        `minify`
            defines if the combined sheet should be minified, default True
    """       
    licenseText = ''

    if license:
        licenseText = "/*\n%s\n*/" %codecs.open(license, "r", "utf-8").read()                   
        
    results = []
    for path in files:         
        logger('Processing file: %r' % path)
        if sourceencoding is not None:
            cssutils.log.info(u'Using source encoding %r' % sourceencoding,
                              neverraise=True)
       
        if path:
            src = cssutils.parseFile(path, encoding=sourceencoding)
        else:
            sys.exit('Path or URL must be given')        
                
        result = resolveImports(src)    
        
        #exclude @charset directive and license text
        if(not results and not minify):
            if license:     
                logger("Adding license file: %r" % license)           
                result.insertRule(cssutils.css.CSSComment(cssText=licenseText), index=0)                
            result.encoding = targetencoding      
        
        logger(u'Using target encoding: %r' % targetencoding)

        if minify:
            # save old setting and use own serializer
            oldser = cssutils.ser
            cssutils.setSerializer(cssutils.serialize.CSSSerializer())
            cssutils.ser.prefs.useMinified()
            cssText = result.cssText
            cssutils.setSerializer(oldser)
        else:
            cssText = result.cssText
            
         
        results.append(cssText)        
        
    result = join(results, not minify and "\n" or "")
    
    if license and minify:
        logger("Adding license file: %r" % license)
        result += '\n'+licenseText            
    
    return result

