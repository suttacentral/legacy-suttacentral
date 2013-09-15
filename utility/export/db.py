#!/usr/bin/env python

"""SuttaCentral Database Export Generator"""

import env
from common import *
import argparse, plumbum, os, os.path, shutil, tempfile
import config

def readme_path():
    return os.path.join(export_code_dir(), 'db_readme.txt')

def export_db(out_path, quiet=False):
    args = [ '-h', config.mysql['host'],
             '-P', str(config.mysql['port']),
             '-u', config.mysql['user'],
             '-p' + config.mysql['password'],
             '-r', out_path,
             config.mysql['db'] ]
    plumbum.local['mysqldump'][tuple(args)] & plumbum.FG

def generate(force=False, quiet=False):
    basename = 'sc-db-{}'.format(export_file_date())
    output_zip = os.path.join(config.exports_root, basename + '.zip')
    output_7z = os.path.join(config.exports_root, basename + '.7z')

    # Check the targets to make sure they don't exist, unless we're force mode
    ensure_not_exists(output_zip, force=force, quiet=quiet)
    ensure_not_exists(output_7z, force=force, quiet=quiet)

    # Create a temporary directory to do our work
    tmp_dir = tempfile.mkdtemp(prefix=basename)

    # Create the containing folder
    output_dir = os.path.join(tmp_dir, basename)
    os.mkdir(output_dir)

    # Copy some extra files
    shutil.copy(readme_path(),
        os.path.join(output_dir, 'README.txt'))
    shutil.copy(license_path(),
        os.path.join(output_dir, 'LICENSE.txt'))

    # Create the database export
    export_db(os.path.join(output_dir, 'suttacentral.sql'))

    # Compress the output directory to the targets
    ensure_not_exists(output_zip, force=True, quiet=True)
    zip(output_zip, output_dir, quiet=quiet)
    ensure_not_exists(output_7z, force=True, quiet=True)
    x7z(output_7z, output_dir, quiet=quiet)

    # Remove the temporary directory and the generated files
    shutil.rmtree(tmp_dir)

    # Update the latest symlinks to point to the files we just created
    update_latest_symlink(output_zip)
    update_latest_symlink(output_7z)

def parse_args():
    parser = argparse.ArgumentParser(
        description='SuttaCentral Database Export Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--force', action='store_true',
        help='overwrite existing output')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='suppress non-errors from output')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    force = args.force
    quiet = args.quiet
    generate(force=args.force, quiet=args.quiet)
