import fnmatch
import logging
import os
import shutil
from subprocess import Popen, PIPE

ALLOWED_EXTENSIONS = frozenset(['.css', '.js'])

logger = logging.getLogger('minify')

def dirwalk(path, exclude=None, extensions=ALLOWED_EXTENSIONS):
    "walk a directory tree, using a generator"
    if exclude is None:
        exclude = []
    for f in os.listdir(path):
        fullpath = os.path.join(path,f)
        for excl in exclude:
            if fnmatch.fnmatch(f, excl) or \
               fnmatch.fnmatch(fullpath, excl):
                break
        else:
            # no exclusion found
            if os.path.isdir(fullpath) and \
               not os.path.islink(fullpath):
                for x in dirwalk(fullpath, exclude, extensions):
                    # recurse into subdir
                    yield x
            else:
                name, extension = os.path.splitext(f)
                if extension.lower() in extensions:
                    yield fullpath

def minify(commands, paths, ignore=None, suffix='-full'):
    """ Minify CSS/JavaScript-resources

    This method walks recursively the paths given and minifies all the
    CSS/JavaScript-resource file it finds.
    """
    if ignore is None:
        ignore = []

    total = {'.css': 0, '.js': 0}
    for path in paths:
        logger.info('Walking resource path: %s', path)
        for subdir in dirwalk(path, ignore):
            if not os.path.isfile(subdir):
                continue

            name, ext = os.path.splitext(subdir)
            if name.endswith(suffix):
                logger.debug("Don't minify orignal version of resource %s",
                             subdir)
                # don't minify full resources from a previous run
                continue

            newname = name + suffix + ext
            if os.path.exists(newname):
                logger.debug("Resource %s is minified already", subdir)

                # minified already
                continue

            # backing up original file
            shutil.copy(subdir, newname)

            command = commands.get(ext, None)
            if command is None:
                # VERY simple default minifier. Only use one space for all
                # other withespaces.
                # ATTENTION !!! Whitespaces in strings are minified too!
                full = open(subdir).read()
                minified = ' '.join(full.split())
            else:
                command = ' '.join([command, subdir])
                logger.debug("Minifying command: %s ",command)
                p = Popen(command, shell=True, stdout=PIPE)
                minified = p.communicate()[0]
            f = open(subdir, 'w')
            f.write(minified)
            total[ext] += 1

    logger.info('Minified %s CSS and %s JavaScript-files',
             total['.css'], total['.js'])



