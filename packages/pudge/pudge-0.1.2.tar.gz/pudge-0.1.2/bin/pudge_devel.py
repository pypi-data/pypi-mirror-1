"""
This isn't really a command line script.
It sets up the development environment.
"""

import sys
import os.path as path
from glob import glob

# put the parent directory on sys.path
devel_dir = path.normpath(path.join(path.dirname(__file__), '..'))
sys.path.insert(1, devel_dir)

# put all eggs under support directory on sys.path
for egg in glob(path.join(devel_dir, 'support', '*.egg')):
    sys.path.insert(2, egg)

if __name__ == '__main__':
    print __doc__.strip()

