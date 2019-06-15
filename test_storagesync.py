import io
import logging
import os
import unittest
from unittest.mock import Mock

from pyfakefs.fake_filesystem_unittest import TestCase

import storagesync


# Test data
#
# A:\
# |-- dog.png
# |-- sound.mp3
# |-- new.txt
# |-- music
# |   `-- music.mp3
# |-- tools
# |   `-- office.exe
# |-- new_empty
#
# B:\
# |-- cat.png
# |-- sound.mp3
# |-- old_music
# |   `-- old_music.mp3
# |-- tools
# |   `-- office.exe
#
# A:\ and B:\ merged
# |-- cat.png
# |-- dog.png
# |-- sound.mp3
# |-- music
# |   `-- music.mp3
# |-- old_music
# |   `-- old_music.mp3
# |-- tools
# |   `-- office.exe
# |-- new_empty

class TestStorageSync(TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        self.create_drive_a()
        self.create_drive_b()
        self.logger = self.create_logger()
        self.os_path = Mock()
        self.os_path.is_hidden.return_value = False

    def test_synchronization_with_dry_run_should_not_update_destination(self):
        expected_a = self.print_tree('A:/')
        expected_b = self.print_tree('B:/')
        self.filesPathsSync = storagesync.FilesPathsSync('A:/', 'B:/', True, False, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree('A:/'))
        self.assertEqual(expected_b, self.print_tree('B:/'))

    def test_synchronization_without_delete_should_merge_source_in_destination(self):
        expected_a = self.print_tree('A:/')
        expected_b = """B:\\
B:\\cat.png
B:\\sound.mp3
B:\\dog.png
B:\\new.txt
B:\\old_music
B:\\old_music\\old_music.mp3
B:\\tools
B:\\tools\\office.exe
B:\\music
B:\\music\\music.mp3
B:\\new_empty
"""
        self.filesPathsSync = storagesync.FilesPathsSync('A:/', 'B:/', False, False, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree('A:/'))
        self.assertEqual(expected_b, self.print_tree('B:/'))

    def test_synchronization_with_delete_should_mirror_source_to_destination(self):
        expected_a = self.print_tree('A:/')
        expected_b = """B:\\
B:\\sound.mp3
B:\\dog.png
B:\\new.txt
B:\\tools
B:\\tools\\office.exe
B:\\music
B:\\music\\music.mp3
B:\\new_empty
"""
        self.filesPathsSync = storagesync.FilesPathsSync('A:/', 'B:/', False, True, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree('A:/'))
        self.assertEqual(expected_b, self.print_tree('B:/'))

    @staticmethod
    def print_tree(root):
        sio = io.StringIO()
        for root, dirs, files in os.walk(root):
            print(root, file=sio)
            for file in files:
                print(os.path.join(root, file), file=sio)
        return sio.getvalue()

    def create_drive_a(self):
        self.fs.create_file('A:/dog.png')
        self.fs.create_file('A:/sound.mp3')
        self.fs.create_file('A:/new.txt')
        self.fs.create_file('A:/music/music.mp3')
        self.fs.create_file('A:/tools/office.exe')
        self.fs.create_dir('A:/new_empty')

    def create_drive_b(self):
        self.fs.create_file('B:/cat.png')
        self.fs.create_file('B:/sound.mp3')
        self.fs.create_file('B:/old_music/old_music.mp3')
        self.fs.create_file('B:/tools/office.exe')

    @staticmethod
    def create_logger():
        logging.basicConfig(format='%(message)s')
        return logging.getLogger(__name__)


if __name__ == '__main__':
    unittest.main()
