import unittest

import os
import shutil

import bezel.resources

class ResourcesTestCase(unittest.TestCase):
    def setUp(self):
        os.mkdir('.tmp')
        self.loader = bezel.resources.Loader()

    def tearDown(self):
        self.loader = None
        shutil.rmtree('.tmp', ignore_errors=True)

    def test_none(self):
        self.loader.index('.tmp')
        assert self.loader._index == {}
        assert self.loader._cached_files == {}
        assert self.loader._path == ['.tmp']

    def test_single(self):
        # Create test file
        test_file = os.path.join('.tmp', 'test.xyz')
        test_string = 'Testing...\nBlah\r.'
        file(test_file, 'w').write(test_string)

        # Load test file
        self.loader.index('.tmp')
        assert not 'xyz' in self.loader.file_loaders
        assert self.loader._index == {}
        assert self.loader._cached_files == {}
        assert self.loader._path == ['.tmp']

        # Ensure it is indexed.
        self.loader.file_loaders['xyz'] = lambda x: file(x).read()
        self.loader.index_all()
        assert test_file in self.loader._index

        # Test if it can be loaded again.
        assert self.loader.load(test_file) == test_string

    def test_cache(self):
        # Create test file
        test_file = os.path.join('.tmp', 'test.xyz')
        test_string = 'Testing...\nBlah\r.'
        file(test_file, 'w').write(test_string)

        # Load test file
        count = []
        def load(filename):
            count.append(True)
            return file(filename).read()

        self.loader.file_loaders['xyz'] = load
        self.loader.index('.tmp')
        assert test_file in self.loader._index

        assert self.loader._cached_files == {}
        assert self.loader.load(test_file) == test_string
        assert len(count) == 1 # Ensure that our function has been called.

        full_path = self.loader._index[test_file]
        assert self.loader._cached_files[full_path] == test_string

        assert self.loader.load(test_file) == test_string
        assert len(count) == 1 # Ensure that the cache is being used.

suite = unittest.makeSuite(ResourcesTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

