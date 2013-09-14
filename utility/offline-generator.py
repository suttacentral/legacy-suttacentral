#!/usr/bin/env python

"""SuttaCentral Offline Generator"""

from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(realpath(__file__))), 'python'))

import argparse, plumbum, os, os.path, shutil, tempfile, time
import config

def parse_args():
    parser = argparse.ArgumentParser(
        description='SuttaCentral Offline Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', type=str, help='the host to crawl')
    parser.add_argument('-f', '--force', action='store_true',
        help='overwrite existing output')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='suppress non-errors from output')
    return parser.parse_args()

def crawl(host, out_dir):
    global quiet
    cmd_path = join(config.base_dir, 'utility', 'crawl.py')
    args = []
    if quiet:
        args.append('--quiet')
    args += [host, out_dir]
    if host == 'suttacentral.net':
        args += ['--wait', '0.1']
    plumbum.local[cmd_path][tuple(args)] & plumbum.FG

def zip(output, path):
    global quiet
    args = []
    if quiet:
        args.append('-q')
    args += ['-r', '-9', output, path]
    plumbum.local['zip'][tuple(args)] & plumbum.FG

def x7z(output, path):
    global quiet
    cmd = plumbum.local['7z']['a', '-t7z', '-mx=9', output, path]
    if quiet:
        cmd()
    else:
        cmd & plumbum.FG

def check_file(path, force, quiet):
    if os.path.exists(path):
        if force:
            if not quiet:
                print('{} exists, overwriting'.format(path))
            os.unlink(path)
        else:
            sys.stderr.write('ERROR: {} exists\n'.format(path))
            sys.exit(1)

if __name__ == '__main__':

    date = time.strftime('%Y%m%d', time.localtime())
    basename = 'suttacentral-offline-{}'.format(date)
    output_zip = join(config.offline_exports_root, basename + '.zip')
    output_7z = join(config.offline_exports_root, basename + '.7z')

    args = parse_args()
    host = args.host
    force = args.force
    quiet = args.quiet

    check_file(output_zip, force, quiet)
    check_file(output_7z, force, quiet)

    tmp_dir = tempfile.mkdtemp(prefix=basename)
    base_tmp_dir = join(tmp_dir, basename)
    os.mkdir(base_tmp_dir)
    base_index_path = join(base_tmp_dir, 'index.html')
    open(base_index_path, 'w').write("""<!DOCTYPE html>
<html><head><meta http-equiv="refresh" content="0; url=sc/index.html">
<title></title</head><body></body></html>""")
    crawler_output_dir = join(base_tmp_dir, 'sc')

    crawl(host, crawler_output_dir)

    # This does not work: os.chdir(tmp_dir)
    plumbum.local.cwd.chdir(tmp_dir)

    zip(output_zip, basename)
    x7z(output_7z, basename)
    
    shutil.rmtree(tmp_dir)

    latestname = 'suttacentral-offline-latest'
    latest_zip = join(config.offline_exports_root, latestname + '.zip')
    latest_7z = join(config.offline_exports_root, latestname + '.7z')
    if os.path.exists(latest_zip):
        os.unlink(latest_zip)
    os.symlink(basename + '.zip', latest_zip)
    if os.path.exists(latest_7z):
        os.unlink(latest_7z)
    os.symlink(basename + '.7z', latest_7z)
