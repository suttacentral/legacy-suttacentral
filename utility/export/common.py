# Common code for offline.py

import pathlib
import plumbum
import regex
import shutil
import sys
import time

import env
import config

license_path = config.base_dir / 'LICENSE.txt'
export_code_dir = pathlib.Path(__file__).parent

def export_file_date():
    return time.strftime('%Y%m%d', time.localtime())

def copy(src, dst):
    shutil.copyfile(str(src), str(dst))

def zip(out_path, in_path, quiet=False):
    with plumbum.local.cwd(str(in_path.parent)):
        args = []
        if quiet:
            args.append('-q')
        args += ['-r', '-9', str(out_path), in_path.name]
        plumbum.local['zip'][tuple(args)] & plumbum.FG

def x7z(out_path, in_path, quiet=False):
    with plumbum.local.cwd(str(in_path.parent)):
        # -mx=5 or greater uses up a lot of memory. Currently the vps
        # is memory starved so we keep this low for now.
        cmd = plumbum.local['7z']['a', '-t7z', '-mx=4', str(out_path),
            in_path.name]
        if quiet:
            cmd()
        else:
            cmd & plumbum.FG

def ensure_not_exists(path, force=False, quiet=False):
    if path.exists():
        if force:
            if not quiet:
                print('{} exists, overwriting'.format(path))
        else:
            sys.stderr.write('ERROR: {} exists\n'.format(path))
            sys.exit(1)

def update_latest_symlink(path):
    symlink_path = pathlib.Path(regex.sub(
        r'([0-9]+)(\.[a-z0-9]{1,4})$', r'latest\2', str(path)))
    if symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to(path)
