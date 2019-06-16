import io
import logging
import os
import unittest
from unittest.mock import Mock

from pyfakefs.fake_filesystem_unittest import TestCase

import storagesync

logger = logging.getLogger(__name__)

if os.name == 'nt':
    drive_a = 'A:/'
    drive_b = 'B:/'
    expected_b_merge_with_a = """B:\\
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
expected_b_mirror_of_a = """B:\\
B:\\sound.mp3
B:\\dog.png
B:\\new.txt
B:\\tools
B:\\tools\\office.exe
B:\\music
B:\\music\\music.mp3
B:\\new_empty
"""

if os.name == 'posix':
    drive_a = 'media_a'
    drive_b = 'media_b'
    expected_b_merge_with_a = """media_b
media_b/cat.png
media_b/sound.mp3
media_b/dog.png
media_b/new.txt
media_b/old_music
media_b/old_music/old_music.mp3
media_b/tools
media_b/tools/office.exe
media_b/music
media_b/music/music.mp3
media_b/new_empty
"""
    expected_b_mirror_of_a = """media_b
media_b/sound.mp3
media_b/dog.png
media_b/new.txt
media_b/tools
media_b/tools/office.exe
media_b/music
media_b/music/music.mp3
media_b/new_empty
"""


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
        expected_a = self.print_tree(drive_a)
        expected_b = self.print_tree(drive_b)

        self.filesPathsSync = storagesync.FilesPathsSync(drive_a, drive_b, True, False, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree(drive_a))
        self.assertEqual(expected_b, self.print_tree(drive_b))
        self.assertTrue(True)

    def test_synchronization_without_delete_should_merge_source_in_destination(self):
        expected_a = self.print_tree(drive_a)
        self.filesPathsSync = storagesync.FilesPathsSync(drive_a, drive_b, False, False, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree(drive_a))
        self.assertEqual(expected_b_merge_with_a, self.print_tree(drive_b))

    def test_synchronization_with_delete_should_mirror_source_to_destination(self):
        expected_a = self.print_tree(drive_a)
        self.filesPathsSync = storagesync.FilesPathsSync(drive_a, drive_b, False, True, self.logger, self.os_path)
        self.assertEqual(expected_a, self.print_tree(drive_a))
        self.assertEqual(expected_b_mirror_of_a, self.print_tree(drive_b))

    @staticmethod
    def print_tree(root):
        sio = io.StringIO()
        for root, dirs, files in os.walk(root):
            print(root, file=sio)
            for file in files:
                print(os.path.join(root, file), file=sio)
        return sio.getvalue()

    def create_drive_a(self):
        self.fs.create_file(os.path.join(drive_a, 'dog.png'))
        self.fs.create_file(os.path.join(drive_a, 'sound.mp3'))
        self.fs.create_file(os.path.join(drive_a, 'new.txt'))
        self.fs.create_file(os.path.join(drive_a, 'music/music.mp3'))
        self.fs.create_file(os.path.join(drive_a, 'tools/office.exe'))
        self.fs.create_dir(os.path.join(drive_a, 'new_empty'))

    def create_drive_b(self):
        self.fs.create_file(os.path.join(drive_b, 'cat.png'))
        self.fs.create_file(os.path.join(drive_b, 'sound.mp3'))
        self.fs.create_file(os.path.join(drive_b, 'old_music/old_music.mp3'))
        self.fs.create_file(os.path.join(drive_b, 'tools/office.exe'))

    @staticmethod
    def create_logger():
        logging.basicConfig(format='%(message)s')
        return logging.getLogger(__name__)


if __name__ == '__main__':
    unittest.main()
