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
    fmtstr = '%Y-%m-%d_%H:%M:%S'
    try:
        from sc.scm import scm
        return scm.last_commit_time.strftime(fmtstr)
    except:
        raise
        
    return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())

def copy(src, dst):
    shutil.copyfile(str(src), str(dst))

def move(src, dst):
    shutil.move(str(src), str(dst))

def zip(out_path, in_path, quiet=False):
    with plumbum.local.cwd(str(in_path.parent)):
        args = []
        if quiet:
            args.append('-q')
        args += ['-r', '-9', str(out_path), in_path.name]
        plumbum.cmd.nice['-20',
            plumbum.local['zip'][tuple(args)]] & plumbum.FG

def x7z(out_path, in_path, quiet=False):
    with plumbum.local.cwd(str(in_path.parent)):
        # These settings chosen after some testing, -mx=3 is 6x faster
        # than -mx=5, and 15% larger. 10 minutes to do the compression
        # is more reasonable than 1 hour.
        cmd = plumbum.cmd.nice['-20',
                plumbum.local['7z']['a', '-t7z', '-mx=3', '-md=1m', '-mmt=off',
                    str(out_path), in_path.name]]
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

def update_latest_symlink(path, basestem):
    symlink_path = path.parent / (basestem + '-latest' + path.suffix)
    # Note: Path.exists() returns False for a broken symlink
    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()
    symlink_path.symlink_to(path)
