# Webqam
A webcam application.

Free to use and modify.

Requirements:
- pyqt6
- glib python binding

How to use:
just execute webqam.sh
or
python3 webqam.py

Options:
webqam.sh WIDTH HEIGHT
or
python3 webqam.py WIDTH HEIGHT

WIDTH and HEIGHT is one of the resolutions supported by your webcam, otherwise the saved resolution or the best resolution will be used.

Mouse:
- context menu with the right button

Options:
- video resolutions (supported by the webcams)
- snapshot delay in seconds, from 0 (no delay) to 5
- toggle window decoration

Keyboard:
- toggle window borders (Meta+t)
- record (Meta+a) (the videos with audio will be saved in the user Videos folder or in the main user folder)
- snapshot (Meta+c) (the pictures will be saved in the user Pictures folder or in the main user folder)
- exit (Meta+e)

Other options:
- the last resolution used will be used as default at start
- left mouse click in the window to show/hide the icons for snapshot and video record funzionality.

This program does not support very old webcams (v4l1).

qcamera is the previous implementation.

