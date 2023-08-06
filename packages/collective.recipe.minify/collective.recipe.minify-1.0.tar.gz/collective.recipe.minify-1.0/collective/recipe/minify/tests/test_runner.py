import unittest
import os.path
import sys
import shutil

from collective.recipe.minify.runner import minify
from collective.recipe.minify.runner import dirwalk

samplepath = os.path.join(
    sys.modules["collective.recipe.minify.tests"].__path__[0], "sample")

class DirWalkerTestCase(unittest.TestCase):
    """ Tests for the dirwalker method """

    def walk(self, *args, **kwargs):
        return sorted([path[len(samplepath)+1:]
                    for path in dirwalk(samplepath, *args, **kwargs)])

    def test_walk(self):
        self.assertEqual(
            self.walk(),
            ['another.js',
             'resources/scripts/bar.js',
             'resources/scripts/foo.js',
             'resources/styles/beautiful.css',
             'resources/styles/foo.css'])

    def test_exclude(self):
        self.assertEqual(self.walk(exclude=['foo*']),
                         ['another.js',
                          'resources/scripts/bar.js',
                          'resources/styles/beautiful.css'])

    def test_extensions(self):
        self.assertEqual(self.walk(extensions=['.css']),
                         ['resources/styles/beautiful.css',
                          'resources/styles/foo.css'])


class MinifyTestCase(unittest.TestCase):

    suffix = '-full'

    def read(self, *args):
        return open(os.path.join(samplepath, *args)).read()

    def test_minify(self):
        origjs = self.read('another.js')
        minify({}, [samplepath])

        self.assertEqual(origjs, self.read('another%s.js' % self.suffix))
        self.assertEqual(self.read('another.js'), 'var z = 6;')

    def test_doublerun(self):
        origcss = self.read('resources', 'styles', 'beautiful.css')

        # first run
        minify({}, [samplepath])

        minicss = self.read('resources', 'styles', 'beautiful.css')

        self.assertEqual(origcss,
            self.read('resources', 'styles', 'beautiful%s.css' % self.suffix))

        # second run
        minify({}, [samplepath])

        self.assertEqual(origcss,
            self.read('resources', 'styles', 'beautiful%s.css' % self.suffix))

        self.assertEqual(minicss,
            self.read('resources', 'styles', 'beautiful.css'))


    def tearDown(self):
        """ restore everything as it was before minifying """

        def walk(path):
            for f in os.listdir(path):
                fullpath = os.path.join(path,f)
                # no exclusion found
                if os.path.isdir(fullpath) and \
                   not os.path.islink(fullpath):
                    for x in walk(fullpath):
                        # recurse into subdir
                        yield x
                else:
                        yield fullpath

        for path in walk(samplepath):
            if not os.path.isfile(path):
                continue

            name, ext = os.path.splitext(path)
            if name.endswith(self.suffix):
                newname = name[:-len(self.suffix)] + ext
                shutil.move(path, newname)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
