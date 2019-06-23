import logging
import os
import shutil
from argparse import ArgumentParser
from pathlib import Path

if os.name == 'nt':
    import win32api
    import win32con

usage_meg = """python storagesync.py arg_from arg_to
arg_from: letter of the source storage
arg_from: letter of the destination storage
-------------------------------------------
StorageSyn synchronize all files and directories from one storage
to another. A storage can be an hard disk, flash drive, etc..
Example: python storagesync.py E: F:
This will copy all files and directories of E: to F:,
then optionally remove all files and directories from F:
that are not present on E:
Disclaimer:
These software is provided as-is, and there are no guarantees that It is bug-free.
Use it at your own risk!
"""


class OSPath:

    def is_hidden(self, path):
        if os.name == 'nt':
            attribute = win32api.GetFileAttributes(path)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return path.startswith('.')


class FilesPathsSync:

    def __init__(self, source, destination, dry_run, can_delete, logger, os_path):
        self.source = source
        self.destination = destination
        self.dry_run = dry_run
        self.can_delete = can_delete
        self.logger = logger
        self.os_path = os_path
        self.pathsDict = dict()
        self.filesPathsDict = dict()
        self.logger.info('Scan source and destination... please wait...')
        self.update_files_paths_dict(source, "src")
        self.update_files_paths_dict(destination, "dst")
        self.logger.info('Done.')
        self.logger.info("Synchronize %d files... please wait..." % len(self.filesPathsDict))
        self.synchronize_files()
        self.synchronize_paths()
        self.logger.info('Done.')

    def update_files_paths_dict(self, base_directory, update_value):
        for (dir_path, dir_names, file_names) in os.walk(base_directory):
            if not self.path_is_hidden(dir_path):
                self.update_paths_dict(dir_path, update_value)
                for filename in file_names:
                    file_path = os.path.join(dir_path, filename)
                    self.update_files_dict(file_path, update_value)

    def update_paths_dict(self, file_path, update_value):
        if not self.path_is_hidden(file_path):
            self.update_dict(self.pathsDict, file_path, update_value)

    def update_files_dict(self, file_path, update_value):
        self.update_dict(self.filesPathsDict, file_path, update_value)

    def update_dict(self, dict_to_update, file_path, update_value):
        source_storage = self.change_filename_storage(file_path, self.source)
        if source_storage in dict_to_update:
            dict_to_update[source_storage] += "." + update_value
        else:
            dict_to_update[file_path] = update_value

    def path_is_hidden(self, path):
        parts = Path(path).parts
        if len(parts) < 2:
            return False
        path = os.path.join(parts[0])
        for index in range(1, len(parts)):
            path = os.path.join(path, parts[index])
            if self.os_path.is_hidden(path):
                return True
        return False

    def synchronize_files(self):
        for key, value in self.filesPathsDict.items():
            # prepare the destination file name
            file_destination = self.change_filename_storage(key, self.destination)
            if self.should_copy_from_source_to_destination(value):
                self.logger.debug("Copy file from %s to %s" % (key, file_destination))
                if not self.dry_run:
                    self.create_path(os.path.dirname(file_destination))
                    shutil.copyfile(key, file_destination)
            if self.should_delete_in_destination(value):
                self.logger.debug("Delete file %s" % file_destination)
                if not self.dry_run:
                    os.remove(file_destination)

    def synchronize_paths(self):
        for key, value in self.pathsDict.items():
            # Prepare the destination path
            path_destination = self.change_filename_storage(key, self.destination)
            if self.should_copy_from_source_to_destination(value):
                self.create_path(path_destination)
            if self.should_delete_in_destination(value):
                self.logger.debug("Delete path %s" % path_destination)
                if not self.dry_run and os.path.exists(path_destination):
                    try:
                        shutil.rmtree(path_destination)
                    except OSError:
                        self.logger.info("Cannot delete %s" % path_destination)

    @staticmethod
    def should_copy_from_source_to_destination(value):
        return ("src" in value) and ("dst" not in value)

    def should_delete_in_destination(self, value):
        return ("src" not in value) and ("dst" in value) and self.can_delete

    def create_path(self, path_destination):
        self.logger.debug("Create path %s" % path_destination)
        if not self.dry_run:
            os.makedirs(path_destination, exist_ok=True)

    @staticmethod
    def change_filename_storage(key, storage):
        if os.name == 'nt':
            drive, path = os.path.splitdrive(key)
            return os.path.join(storage, path)
        else:
            path = os.path.join(storage, Path(*Path(key).parts[1:]))
            return path


if __name__ == "__main__":
    parser = ArgumentParser(usage=usage_meg)
    parser.add_argument("source", help="Synchronize from this storage, example 'E:'")
    parser.add_argument("destination", help="Synchronize to this storage, example 'F:'")
    parser.add_argument("--verbose", action='store_true', help="verbose mode")
    parser.add_argument("--dryrun", action='store_true',
                        help="Print all operations in the console without affecting files or paths")
    parser.add_argument("--delete", action='store_true',
                        help="Delete files and paths present in destination but not in source")
    args = parser.parse_args()

    log_level = logging.DEBUG if (args.dryrun or args.verbose) else logging.INFO
    logging.basicConfig(format='%(message)s', level=log_level)
    log = logging.getLogger(__name__)
    FilesPathsSync(os.path.abspath(args.source),
                   os.path.abspath(args.destination),
                   args.dryrun,
                   args.delete,
                   log,
                   OSPath())
