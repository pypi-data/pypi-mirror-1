
from os.path import dirname, abspath, normpath, join

__all__ = ['test_code_dir', 'test_files', 'test_output_dir', 'build_dir',
           'get_test_file',
           'get_output_file']

test_code_dir = abspath(dirname(__file__))
test_files = join(test_code_dir, 'data')
build_dir = join(dirname(dirname(test_code_dir)), 'build')
test_output_dir = join(dirname(dirname(test_code_dir)), 'build/test')

def get_test_file(filename):
    return join(test_files, filename)

def get_output_file(*filenames):
    return join(test_output_dir, *filenames)
