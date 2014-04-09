# Common code for offline.py

import pathlib
import plumbum
import regex
import shutil
import sys
import time

import env

import sc

license_path = sc.base_dir / 'LICENSE.txt'
export_code_dir = pathlib.Path(__file__).parent

def export_file_date():
    # Use the most recent modification time of the git repositories
    # so a new build is created only after updates to the server.
    try:
        time1 = (sc.base_dir / '.git').stat().st_mtime
        time2 = (sc.data_dir / '.git').stat().st_mtime
        time_to_use = time.gmtime(time1 if time1 > time2 else time2)
    except FileNotFoundError:
        time_to_use = time.localtime()
    return time.strftime('%Y-%m-%d_%H:%M:%S', time_to_use)

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
        # Use 'ultra' settings except dictionary size to reduce
        # memory use (~40mb rather than ~600mb) while still getting
        # close to maximum compression.
        cmd = plumbum.local['7z']['a', '-t7z', '-mx=9', '-md=1m',
                str(out_path), in_path.name]
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
