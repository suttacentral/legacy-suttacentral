#!/usr/bin/env python

"""Convert Zawgyi_One encoding to Myanmar3 (Unicode 5.1+) encoding."""

import glob
import os
import os.path

for input_path in glob.glob('pass1/*.html'):
    output_path = 'pass2/{}'.format(os.path.basename(input_path))
    print('Converting {} to {}'.format(input_path, output_path))
    os.system('node conv.js < {} > {}'.format(input_path, output_path))
