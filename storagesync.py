# Disclaimer
# These software is provided as-is, and there are no guarantees that It is bug-free.
# Use it at your own risk!
# Require pip install pypiwin32
import os
from argparse import ArgumentParser

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

    def __init__(self, source, destination, info_logger):
        self.source = source
        self.destination = destination
        self.info_logger = info_logger
        self.filesPaths = dict()
        self.info_logger.print("Scan source and destination... please wait...")
        self.update_files_dict(source, "src")
        self.update_files_dict(destination, "dst")
        self.info_logger.print("Done.").print("Synchronize %d files... please wait..." % len(self.filesPaths))
        self.synchronize()
        self.info_logger.print("Done.")

    def update_files_dict(self, base_directory, update_value):
        for (dir_path, dir_names, file_names) in os.walk(base_directory):
            if not self.path_is_hidden(dir_path):
                for filename in file_names:
                    file_path = os.path.join(dir_path, filename)
                    # Always compare from source
                    file_source = self.change_filename_storage(file_path, self.source)
                    if file_source in self.filesPaths:
                        self.filesPaths[file_source] += "." + update_value
                    else:
                        self.filesPaths[file_path] = update_value

    @staticmethod
    def path_is_hidden(path):
        if os.name == 'nt':
            attribute = win32api.GetFileAttributes(path)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return path.startswith('.')  # linux-osx

    def synchronize(self):
        for key, value in self.filesPaths.items():
            # logger.printVerbose(key + "[" + value + "]")
            # Not exist and destination, copy it
            if ("src" in value) and ("dst" not in value):
                file_destination = self.change_filename_storage(key, self.destination)
                self.info_logger.printVerbose("Copy file from %s to %s" % (key, file_destination))
            # Exist only on destination, delete it
            if ("src" not in value) and ("dst" in value):
                file_destination = self.change_filename_storage(key, self.destination)
                self.info_logger.printVerbose("Delete file from %s" % key)

    @staticmethod
    def change_filename_storage(key, storage):
        drive, path = os.path.splitdrive(key)
        return os.path.join(storage, path)


if __name__ == "__main__":
    help_meg = "python storagesync.py arg_from arg_to\n" \
               "arg_from: letter of the source storage\n" \
               "arg_from: letter of the destination storage\n" \
               "-------------------------------------------\n" \
               "StorageSyn synchronize all files and directories from one storage\n" \
               "to another. A storage can be hard disk, usb key, etc..\n" \
               "Example: python storagesync.py E: F:\n" \
               "This will copy all files and directories of E: to F:,\n" \
               "then optionally remove all files and directories from F:\n" \
               "that are not present on E:\n" \
               "Disclaimer:\n" \
               "These software is provided as-is, and there are no guarantees that It is bug-free.\n" \
               "Use it at your own risk!\n"
    parser = ArgumentParser(usage=help_meg)
    parser.add_argument("source", help="Synchronize from this storage, example 'E:'")
    parser.add_argument("destination", help="Synchronize to this storage, example 'F:'")
    args = parser.parse_args()
    FilesPathsSync(os.path.abspath(args.source),
                   os.path.abspath(args.destination),
                   InfoLogger(True))
