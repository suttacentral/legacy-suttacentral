#!/usr/bin/env python

"""Convert Zawgyi_One encoding to Myanmar3 (Unicode 5.1+) encoding."""

from lib import *

if __name__ == '__main__':
    makedirs()
    for input_path in pass1_dir.glob('*.html'):
        output_path = pass2_dir / input_path.name
        print('Pass 2: {} -> {}'.format(input_path, output_path))
        os.system('node conv.js < {} > {}'.format(input_path, output_path))
