# qcamera
A webcam application.

Free to use and modify.

Requirements:
- pyqt6
- glib python binding

How to use:
just execute qcamera.sh
or
python3 qcamera.py

Options:
qcamera.sh WIDTH HEIGHT
or
python3 qcamera.py WIDTH HEIGHT
WIDTH and HEIGHT is the right resolution of the webcam, otherwise the best resolution will be used.

Commands:
* Mouse: context menu with the right button
* Keyboard:
- toggle window borders (Meta+t)
- record (Meta+a) (the videos with audio will be saved in the user Videos folder or in the main user folder)
- snapshot (Meta+c) (the pictures will be saved in the user Pictures folder or in the main user folder)
- exit (Meta+e)

The webcam format/resolution can be changed through the context menu.

This program does not support very old webcams (v4l1).
