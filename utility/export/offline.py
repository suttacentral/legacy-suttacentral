#!/usr/bin/env python

"""SuttaCentral Offline Export Generator"""

import argparse
import pathlib
import plumbum
import tempfile

import env

from sc import config

from common import *

index_html_path = export_code_dir / 'offline_index.html'
readme_path = export_code_dir / 'offline_readme.txt'

def crawl(host, out_dir, wait=0.0, quiet=False):
    cmd_path = config.base_dir / 'utility' / 'crawl.py'
    args = ['--wait', str(wait)]
    if quiet:
        args.append('--quiet')
    args += [host, out_dir]
    plumbum.local[str(cmd_path)][tuple(args)] & plumbum.FG

def generate(host, wait=0.0, force=False, quiet=False):
    basename = 'sc-offline-{}'.format(export_file_date())
    output_zip = config.exports_dir / (basename + '.zip')
    output_7z = config.exports_dir / (basename + '.7z')

    # Check the targets to make sure they don't exist, unless we're force mode
    ensure_not_exists(output_zip, force=force, quiet=quiet)
    ensure_not_exists(output_7z, force=force, quiet=quiet)

    # Create a temporary directory to do our work
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = pathlib.Path(tmp_dir_str)

        # Create the containing folder
        output_dir = tmp_dir / basename
        output_dir.mkdir(mode=0o755)

        # Copy some extra files
        copy(index_html_path, output_dir / 'index.html')
        copy(readme_path, output_dir / 'README.txt')
        copy(license_path, output_dir / 'LICENSE.txt')

        # Crawl website... (go get a cup of tea)
        crawler_output_dir = output_dir / 'sc'
        crawl(host, crawler_output_dir, wait=wait, quiet=quiet)

        tmp_output_zip = tmp_dir / (basename + '.zip')
        tmp_output_7z = tmp_dir / (basename + '.7z')

        # Compress the output to the temporary directory
        zip(tmp_output_zip, output_dir, quiet=quiet)
        x7z(tmp_output_7z, output_dir, quiet=quiet)

        # Copy the files to the final location
        copy(tmp_output_zip, output_zip)
        copy(tmp_output_7z, output_7z)

    # Update the latest symlinks to point to the files we just created
    update_latest_symlink(output_zip)
    update_latest_symlink(output_7z)

def parse_args():
    parser = argparse.ArgumentParser(
        description='SuttaCentral Offline Export Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', type=str, help='the host to crawl')
    parser.add_argument('-w', '--wait', type=float, default=0.0,
        help='time to wait between crawl requests in seconds')
    parser.add_argument('-f', '--force', action='store_true',
        help='overwrite existing output')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='suppress non-errors from output')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    generate(args.host, wait=args.wait, force=args.force, quiet=args.quiet)
