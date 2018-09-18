from __future__ import print_function
import site
import logging
import os
import subprocess
import sys
import argparse
import sys
from datetime import datetime
from del_utils import calc_size, unlink, create_bat_file

site.addsitedir(r'd:\talha.ahmed\workspace\pyenv_maya\tactic')

if True:
    import auth.user

auth.user.login('tactic', 'tactic123', project='suntop_s01')

if True:
    import app.util as util

server = util.get_server()
sk = '__search_key__'


def get_sobject_deletables(sobject, versions=2, days=3, keep_current=True,
                           keep_latest=True):
    snaps = server.get_all_children(sobject[sk], 'sthpw/snapshot')
    contexts = {snap['context'] for snap in snaps}
    deletables = []
    for context in contexts:
        csnaps = [
            snap for snap in snaps
            if snap['context'] == context and snap['version'] not in [-1, 0]
        ]
        max_version = max(csnaps, key=lambda s: s['version'])
        for snap in csnaps:
            old_by_version = (snap['version'] <=
                              max_version['version'] - versions)
            old_by_timestamp = ((datetime.now() - datetime.strptime(
                snap['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')).days >
                                days)
            current_or_latest = ((snap['is_current'] and keep_current) or
                                 (snap['is_latest'] and keep_latest))
            if old_by_version and old_by_timestamp and not current_or_latest:
                paths = [
                    util.translatePath(path)
                    for path in server.get_all_paths_from_snapshot(
                        snap['code'], mode='client_repo')]
                paths = [path for path in paths if os.path.exists(path)]
                deletables.extend(paths)
    return deletables


known_stypes = [
        'vfx/asset', 'vfx/shot', 'vfx/sequences', 'vfx/asset_in_episode']

print_functions {
        'vfx/asset_in_episode': print_asset_in_episode,
}


def print_asset_in_episode(sobj):
    print (sobj.episode_code, sobj.asset_code)


def print_sobj_code(sobj):
    print (sobj.code)


def delete_from_stype(
        stype, versions=2, days=3, keep_current=True, keep_latest=True,
        print_paths=True, print_sobj=None, simulate=False, getsize=True):
    deletables = []
    sobjs = server.eval("@SOBJECT(%s)" % stype)
    if print_sobj is None:
        print_sobj = print_functions.get(stype, print_sobj_code)
    for sobj in sobjs:
        print_sobj(sobj)
        for p in get_sobject_deletables(
                sobj, versions=versions, days=days,
                keep_current=keep_current, keep_latest=keep_latest):
            deletables.append((p, os.path.getsize(p)) if getsize else p)
            if not simulate:
                unlink(p)
            logging.info(p)
            if print_paths:
                print (p)
    return deletables


def create_parser():
    parser = argparse.ArgumentParser('Delete older versions from Tactic SObjects')
    parser.add_argument('project', type=str,
                        help='The project to purge off older versions')
    parser.add_argument('--stype', '-t', type=str, nargs='+',
                        help='The Search Type to purge of older versions')
    parser.add_argument('--logdir', '-d', type=str, nargs=1,
                        help='Specify a directory to generate a logfile')
    parser.add_argument('--logfile', '-f', type=str, nargs=1,
                        help='Specify a logfile path (Overrides --logdir)')
    parser.add_argument('--keepversions', '-k', type=int,
                        help='Number of versions to keep')
    parser.add_argument('--keepdays', '-d', type=int,
                        help='Versions will not be deleted from inside this '
                             'many number of days')
    parser.add_argument('--keepcurrent', '-c', action='store_true',
                        help='Keep the current versions')
    parser.add_argument('--keeplatest', '-l', action='store_true',
                        help='Keep the latest versions')
    parser.add_argument('--batfile', '-b', type=str,
                        help='Path for a bat file generated')
    parser.add_argument('--getsize', '-z', action='store_true',
                        help='Get Size of deletable files')
    parser.add_argument('--simulate', '-s', action='store_true',
                        help='Dont actually delete files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print filenames')
    return parser


def delete_tactic_versions(argv=None):
    parser = create_parser()
    _ns = parser.parse_args(sys.argv[1:] if args is None else args)

    server.set_project(_ns.project if _ns.project else 'sthpw')
    stypes = _ns.stypes if _ns.stypes else known_stypes

    log_dir = tempfile.gettempdir()

    if namespace.logdir and not namespace.logfile:
        if os.path.isdir(namespace.logdir):
            log_dir = namespace.logdir
        else:
            print ('\nWarning: Directory %s does not exists, using %s\n' % (
                namespace.logdir, log_dir))

    if namespace.logfile:
        logfile = namespace.logfile
    else:
        _fd, logfile = tempfile.mkstemp(
                suffix='.log', prefix='tacticdel_', dir=log_dir, text=True)
        os.close(_fd)

    logging.basicConfig(
        filename=logfile, level=logging.DEBUG, format='%(message)s')

    print ('Log File: ', logfile)

    deletables = []
    for _stype in stypes:
        _del = delete_from_stypes(
                _stype, versions=_ns.keepversions,
                days=_ns.keepdays, keep_current=_ns.keepcurrent,
                keep_latest=_ns.keep_latest, print_paths=_ns.verbose,
                simulate=_ns.simulate, getsize=_ns.getsize)
        deletables.extend(_del)

    if _ns.getsize:
        print ('Total Size:', calc_size(deleted_files))
    if _ns.batfile:
        create_bat_file(delete_files, batfile)

    return deletables


if __name__ == "__main__":
    delete_tactic_versions()
