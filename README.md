# storagesync for Windows

|           1           |           2           |           3           |
|-----------------------|-----------------------|-----------------------|
|![flash](https://github.com/SPILAB/storagesync/blob/master/Nuvola_devices_usbpendrive_unmount.png)![flash](https://github.com/SPILAB/storagesync/blob/master/Nuvola_devices_usbpendrive_unmount.png)|python storagesync.py A: B: --delete|![flash](https://github.com/SPILAB/storagesync/blob/master/Nuvola_devices_usbpendrive_unmount.png)![flash](https://github.com/SPILAB/storagesync/blob/master/Nuvola_devices_usbpendrive_unmount.png)|
|Storage A              |Storage A              |Storage A              |
|dog.png                |dog.png                |dog.png                |
|sound.mp3              |sound.mp3              |sound.mp3              |
|new.txt                |new.txt                |new.txt                |
|                       |                       |                       |
|Storage B              |Storage B              |Storage B              |
|cat.png                |-cat.png               |dog.png                |
|sound.mp3              |+dog.png               |sound.mp3              |
|                       |=sound.mp3             |new.txt                |
|                       |+new.txt               |                       |

# Setup
storagesync require pypiwin32
<code>pip install pypiwin32</code>

# Usage
<pre><code>
python storagesync.py arg_from arg_to
</code>
arg_from: letter of the source storage
arg_from: letter of the destination storage

Example: python storagesync.py E: F:
</pre>
StorageSyn synchronize all files and directories from one storage to another. A storage can be an hard disk, flash drive, etc...
This will copy all files and directories of 'E:' to 'F:'
Then optionally remove all files and directories from 'F:' that are not present on 'E:'
Do not use it to backup hidden files or operating system.

# Disclaimer

These software is provided as-is, and there are no guarantees that It is bug-free.
Use it at your own risk!
