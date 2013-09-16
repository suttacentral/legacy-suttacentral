# Common code for db.py and offline.py

import env
import os, os.path, plumbum, regex, shutil, sys, time
import config

def license_path():
    return os.path.join(config.base_dir, 'LICENSE.txt')

def export_code_dir():
    return os.path.dirname(os.path.realpath(__file__))

def export_file_date():
    return time.strftime('%Y%m%d', time.localtime())

def plumbum_chdir(path):
    # This does not work: os.chdir(path)
    plumbum.local.cwd.chdir(path)

def zip(out_path, in_path, quiet=False):
    plumbum_chdir(os.path.dirname(in_path))
    args = []
    if quiet:
        args.append('-q')
    args += ['-r', '-9', out_path, os.path.basename(in_path)]
    plumbum.local['zip'][tuple(args)] & plumbum.FG

def x7z(out_path, in_path, quiet=False):
    plumbum_chdir(os.path.dirname(in_path))
    # -mx=5 or greater uses up a lot of memory. Currently the vps
    # is memory starved so we keep this low for now.
    cmd = plumbum.local['7z']['a', '-t7z', '-mx=4', out_path,
        os.path.basename(in_path)]
    if quiet:
        cmd()
    else:
        cmd & plumbum.FG

def ensure_not_exists(path, force=False, quiet=False):
    if os.path.exists(path):
        if force:
            if not quiet:
                print('{} exists, overwriting'.format(path))
        else:
            sys.stderr.write('ERROR: {} exists\n'.format(path))
            sys.exit(1)

def update_latest_symlink(path):
    symlink_path = regex.sub(
        r'([0-9]+)(\.[a-z0-9]{1,4})$', r'latest\2', path)
    if os.path.exists(symlink_path):
        os.unlink(symlink_path)
    os.symlink(os.path.basename(path), symlink_path)
