================================
CSS Tools recipe for ZC Buildout
================================

falkolab.recipe.csstools is a zc.buildout recipe for building (validation, compressing) 
 css style sheet sources.  The buildout works to writing concatenated 
and compressed files from a declarative config.

Buildout Format
===============

Variables
---------

 * output-dir -- path to where result should be written.

 * config -- path to builder config file

 * resource-dir -- not required, used for interpolation of builder config

 * section -- output concatenated file for only this section of the 'config'

 * output-name -- (for use with 'section') write file to this name
 
 * sourceencoding (optional) -- encoding of the source stylesheet
 
 * targetencoding (optional) -- encoding of the combined stylesheet, default 'utf-8'

 * compress -- defines if the combined sheet should be minified, default True
 
Configuration Format
--------------------

A config file may have multiple uniquely named output files (ie
multiple sections).

A section is formatted in the following fashion::

[styles.css]
root=path/to/where/files/are
license=path/to/license/for/these/libs
include =
first=
      styles/color.css
      styles/typography.js
      styles/layout.js

last=
     core/main.js

exclude=
      debug/layout-debug.css
#...


The files listed in the `first` variable will be forced to load
*before* all other files (in the order listed). The files in `last`
variable will be forced to load *after* all the other files (in the
order listed).

The files list in the `exclude` section will not be imported. 
If you set `include` variable then `first` and `last` variable will be ignored. 

The configuration allows for the interpolation of variables defined in
the config file.  '%(resource-dir)s' 

Lines commented using '#' will be ignored.

Resolving imports
------------------

Contained  import directives in style sheets will be resolved and repleced
by referenced files or urls content:

@import url("color.css");
@import "layout.css";

Imports can't be controlled by bildout configuration 
(e.g. first, last, include, exclude lists).


Examples
--------
from file buildout.cfg:

...

[css-builder]
recipe=falkolab.recipe.csstools:builder
resource-dir=${buildout:directory}/src/path/to/package/resources
config=css-builder.cfg
output-dir=${css-builder:resource-dir}/styles
compress=True 
targetencoding=utf-8

[css-builder-debug]
recipe=falkolab.recipe.csstools:builder
config=${css-builder:config}
resource-dir=${css-builder:resource-dir}
output-dir=${css-builder:output-dir}
output=${css-builder:output-dir}/ts-debug.css
compress=False 
section=ts.css
...