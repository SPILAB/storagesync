import os
import shutil
from argparse import ArgumentParser
from pathlib import Path

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

if os.name == 'nt':
    import win32api
    import win32con


class InfoLogger:

    def __init__(self, verbose):
        self.verbose = verbose

    def print(self, message):
        print(message)
        return self

    def printVerbose(self, message):
        if self.verbose:
            print(message)
        return self


class FilesPathsSync:

    def __init__(self, source, destination, dry_run, can_delete, info_logger):
        self.source = source
        self.destination = destination
        self.dry_run = dry_run
        self.can_delete = can_delete
        self.info_logger = info_logger
        self.pathsDict = dict()
        self.filesPathsDict = dict()
        self.info_logger.print("Scan source and destination... please wait...")
        self.update_files_paths_dict(source, "src")
        self.update_files_paths_dict(destination, "dst")
        self.info_logger.print("Done.").print("Synchronize %d files... please wait..." % len(self.filesPathsDict))
        self.synchronize_files()
        self.synchronize_paths()
        self.info_logger.print("Done.")

    def update_files_paths_dict(self, base_directory, update_value):
        for (dir_path, dir_names, file_names) in os.walk(base_directory):
            if not self.path_is_hidden(dir_path):
                self.update_paths_dict(dir_path, update_value)
                for filename in file_names:
                    file_path = os.path.join(dir_path, filename)
                    self.update_files_dict(file_path, update_value)

    def update_paths_dict(self, file_path, update_value):
        # Always compare from source
        if not self.path_is_hidden(file_path):
            path_source = self.change_filename_storage(file_path, self.source)
            if path_source in self.pathsDict:
                self.pathsDict[path_source] += "." + update_value
            else:
                self.pathsDict[file_path] = update_value

    def update_files_dict(self, file_path, update_value):
        # Always compare from source
        file_source = self.change_filename_storage(file_path, self.source)
        if file_source in self.filesPathsDict:
            self.filesPathsDict[file_source] += "." + update_value
        else:
            self.filesPathsDict[file_path] = update_value

    @staticmethod
    def path_is_hidden(path):
        parts = Path(path).parts
        if len(parts) < 2:
            return False
        path = os.path.join(parts[0])
        for index in range(1, len(parts)):
            path = os.path.join(path, parts[index])
            if os.name == 'nt':
                attribute = win32api.GetFileAttributes(path)
                hidden = attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
            else:
                hidden = path.startswith('.')
            if hidden:
                return True
        return False

    def synchronize_files(self):
        for key, value in self.filesPathsDict.items():
            # prepare the destination file name
            file_destination = self.change_filename_storage(key, self.destination)
            if self.should_copy_from_source_to_destination(value):
                self.info_logger.printVerbose("Copy file from %s to %s" % (key, file_destination))
                if not self.dry_run:
                    self.create_path(os.path.dirname(file_destination))
                    shutil.copyfile(key, file_destination)
            if self.should_delete_in_destination(value):
                self.info_logger.printVerbose("Delete file %s" % file_destination)
                if not self.dry_run:
                    os.remove(file_destination)

    def synchronize_paths(self):
        for key, value in self.pathsDict.items():
            # Prepare the destination path
            path_destination = self.change_filename_storage(key, self.destination)
            if self.should_copy_from_source_to_destination(value):
                self.create_path(path_destination)
            if self.should_delete_in_destination(value):
                self.info_logger.printVerbose("Delete path %s" % path_destination)
                if not self.dry_run and os.path.exists(path_destination):
                    try:
                        shutil.rmtree(path_destination)
                    except OSError:
                        self.info_logger.print("Cannot delete %s" % path_destination)

    @staticmethod
    def should_copy_from_source_to_destination(value):
        return ("src" in value) and ("dst" not in value)

    def should_delete_in_destination(self, value):
        return ("src" not in value) and ("dst" in value) and self.can_delete

    def create_path(self, path_destination):
        self.info_logger.printVerbose("Create path %s" % path_destination)
        if not self.dry_run:
            os.makedirs(path_destination, exist_ok=True)

    @staticmethod
    def change_filename_storage(key, storage):
        drive, path = os.path.splitdrive(key)
        return os.path.join(storage, path)


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
    activeVerbose = args.dryrun or args.verbose
    FilesPathsSync(os.path.abspath(args.source),
                   os.path.abspath(args.destination),
                   args.dryrun,
                   args.delete,
                   InfoLogger(activeVerbose))
