Supported options
-----------------

The recipe supports the following options:

css-command
    The script to be used for css minification. The YUI compressor is a good
    choice here. This option is not required. If it is omitted, a very simple
    whitespace stripping is done [' '.join(RESOURCE.split())]. The command 
    must write its result to the standard output.

js-command
    Same as ``css-command`` but used for JavaScript resources.

ignore
    A list of fnmatch-patters. If a filename matches one of these
    expressions, it is omitted from the minifying process.

paths
    A list of paths, which contains JavaScript and CSS resources. All files
    ending with '.js' and '.css' are considered, except those which are ignored
    explicitly (see ignore option).

suffix
    Filename suffix that is used for the copy of the original file. The default
    is ``-full``. If the orignal filename is ``style.css`` the minified version
    will be ``style.css`` and the original development version will be
    ``style-full.css``.

include-devel
    Include all packages listed in the devel-section of the buildout. This
    option is turned OFF per default.

verbose
    Set verbosity for minify runs. The allowed values are ``true``
    and ``false`` and the default is ``false``.

Example usage
-------------

A simple buildout that uses the recipe looks like this::

 >>> write('buildout.cfg',
 ... """
 ... [buildout]
 ... parts = minify
 ...
 ... [minify]
 ... recipe = collective.recipe.minify
 ... paths =
 ...    ${buildout:directory}/src/foo
 ... ignore =
 ...      firm*
 ... include-devel = false
 ... """)

Running the buildout gives us::

 >>> print system(buildout)
 Installing minify.
 Generated script '/sample-buildout/bin/minify'.
 <BLANKLINE>

Running this script minifies all JavaScript and CSS resources found in
the specfied locations. It walks all the paths specified ignoring all files
matching one of the patterns specified in ignore.
