from __future__ import print_function

import os
import re
import logging
import tempfile
import argparse
import sys

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
                os.unlink(_path)
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


def delete_compositor_versions(
        base_path, simulate=False, doprint=True, get_size=True,
        remove_directories=False, keep_versions=1):
    deleted_files = []
    for path, dirs, files in os.walk(base_path):
        version_dirs = [_dir for _dir in dirs if version_pattern.match(_dir)]
        if version_dirs:
            max_dir = max(version_dirs)
            if doprint:
                print (path, max_dir)
            for _dir in version_dirs:
                if _dir == max_dir:
                    continue
                vdir = os.path.join(path, _dir)
                files = clean_dir(vdir, simulate, doprint)
                deleted_files.extend(files)
                if remove_directories:
                    try:
                        if simulate:
                            os.rmdir(vdir)
                        deleted_files.append((vdir, 0) if get_size else vdir)
                    except (IOError, WindowsError):
                        pass

    if get_size:
        print ('Total Size:', calc_size(deleted_files))
    return deleted_files


def calc_size(files):
    if not files:
        return 0
    sizes = []
    for _file in files:
        if isinstance(_file, tuple) or isinstance(_file, list):
            sizes.append(_file[1])
        else:
            sizes.append(os.path.getsize(_file))
    return sum(sizes)


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
            help='Dont just delete files also delete directories')
    parser.add_argument(
            '--getsize', '-z', action='store_true',
            help='print file size and total size of deleted files')
    parser.add_argument(
            '--keepversions', '-k', type=int, default=1,
            help='number of versions to keep')
    return parser


def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

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
            namespace.getsize, namespace.keepversions)


if __name__ == "__main__":
    main()
