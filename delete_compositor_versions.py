from __future__ import print_function

import os
import re
import logging
import tempfile
import argparse
import sys

from del_utils import calc_size, unlink, create_bat_file

base_path = (r'\\renders2\Storage\Projects\external\Prince_Choc_5'
             r'\02_production\2D\Output\EP001\Output')
version_pattern = re.compile('^v(\d+)$')


def clean_dir(directory, simulate=False, doprint=True, get_size=True):
    files_deleted = []
    for _file in os.listdir(directory):
        _path = os.path.join(directory, _file)
        if os.path.isfile(_path):
            size = os.path.getsize(_path)
            if not simulate:
                unlink(_path)
            if doprint:
                if get_size:
                    print (_path, 'SIZE:', size)
                else:
                    print (_path)
            logging.info(_path)
            if get_size:
                files_deleted.append((_path, size))
            else:
                files_deleted.append(_path)
    return files_deleted


def get_deletable_dirs(dirs, keep_versions=1):
    '''return: list of str'''
    version_dirs = []
    for _dir in dirs:
        match = version_pattern.match(_dir)
        if match:
            version_dirs.append((_dir, int(match.group(1))))
    return [_dir[0] for _dir in sorted(version_dirs,
            key=lambda x: x[1], reverse=True)[keep_versions:]]


def delete_compositor_versions(
        base_path, simulate=False, doprint=True, get_size=True,
        remove_directories=False, keep_versions=1, batfile=None):
    deleted_files = []

    for path, dirs, files in os.walk(base_path):
        del_dirs = get_deletable_dirs(dirs, keep_versions)
        for _dir in del_dirs:
            vdir = os.path.join(path, _dir)
            files = clean_dir(vdir, simulate, doprint)
            deleted_files.extend(files)
            if remove_directories:
                try:
                    if not simulate:
                        os.rmdir(vdir)
                    deleted_files.append((vdir, 0) if get_size else vdir)
                except (IOError, WindowsError):
                    pass

    if get_size:
        print ('Total Size:', calc_size(deleted_files))
    if batfile:
        create_bat_file(deleted_files, batfile)
    return deleted_files


def create_parser():
    parser = argparse.ArgumentParser(
            'Clear out Version dirs under found under a given path')
    parser.add_argument(
            'basedir', type=str,
            help='The main directory to look for versions')
    parser.add_argument(
            '--logdir', '-d', type=str, nargs=1,
            help='Specify a directory to generate a logfile')
    parser.add_argument(
            '--logfile', '-f', type=str, nargs=1,
            help='Specify a logfile path (Overrides --logdir)')
    parser.add_argument(
            '--simulate', '-s', action='store_true',
            help='Don\'t actually delete files')
    parser.add_argument(
            '--verbose', '-v', action='store_true', help='print file names')
    parser.add_argument(
            '--removedirs', '-r', action='store_true',
            help='Don\'t just delete files also delete directories')
    parser.add_argument(
            '--getsize', '-z', action='store_true',
            help='print file size and total size of deleted files')
    parser.add_argument(
            '--keepversions', '-k', type=int, default=1,
            help='number of versions to keep')
    parser.add_argument(
            '--batfile', '-b', type=int, default=1, help='generate bat file')
    return parser


def main(args=None):
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:] if args is None else args)

    if namespace.basedir is None or not os.path.isdir(namespace.basedir):
        print ('\nError: No Valid directory provided!\n')
        parser.print_help()
        sys.exit(1)

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
                suffix='.log', prefix='compdel_', dir=log_dir, text=True)
        os.close(_fd)

    logging.basicConfig(
        filename=logfile, level=logging.DEBUG, format='%(message)s')

    print ('Log File: ', logfile)

    delete_compositor_versions(
            namespace.basedir, namespace.simulate, namespace.verbose,
            namespace.getsize, namespace.keepversions, namespace.batfile)


if __name__ == "__main__":
    try:
        sys.path.insert(0, os.path.dirname(__file__))
    except NameError:
        sys.path.insert(0, '.')
    main()
