#!/usr/bin/python3

# version 0.1.1

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import *
from PyQt6.QtGui import *
import os,sys
from PyQt6.QtMultimediaWidgets import *
import time
from datetime import datetime
from gi.repository import GLib

class firstMessage(QWidget):
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon("icons/.svg"))
        box = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        box.setContentsMargins(2,2,2,2)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()

APP_TITLE = "QCamera"


PICTURES_PATH = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
VIDEOS_PATH = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS)

WINW = 720
WINH = 405
dialWidth = 300

try:
    with open("winsize.cfg", "r") as ifile:
        fcontent = ifile.readline()
    aw, ah = fcontent.split(";")
    WINW = int(aw)
    WINH = int(ah)
except:
    try:
        with open("winsize.cfg", "w") as ifile:
            ifile.write("-1;-1")
    except:
        fm = firstMessage("Error", "The file winsize.cfg cannot be read/created.")
        sys.exit(app.exec())


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.pixel_ratio = max(1,self.devicePixelRatio())
        
        global WINW
        global WINH
        self.resize(int(WINW/self.pixel_ratio), int(WINH/self.pixel_ratio))
        
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon("icons/qcamera.svg"))
        
        # self.setObjectName("mainwindow")
        
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # self.setStyleSheet("#mainwindow {background-color: #00000000;}")
        # self.setStyleSheet("#mainwindow {background-color: #000000;}")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        self._widget = QWidget()
        self._widget.setLayout(self.layout)
        self.setCentralWidget(self._widget)
        self.show()
        
        self.NEW_WIDTH = -1
        self.NEW_HEIGHT = -1
        if len(sys.argv) > 1:
            if sys.argv[1] == "--help":
                print("Usage: qcamera.py WIDTH HEIGHT\n")
                MyDialog("Error", "Usage: qcamera.py WIDTH HEIGHT\n", self)
            else:
                try:
                    if not isinstance(int(sys.argv[1]), int) or not isinstance(int(sys.argv[2]), int):
                        print("Usage: qcamera.py WIDTH HEIGHT\n")
                        MyDialog("Error", "Usage: qcamera.py WIDTH HEIGHT\n", self)
                    else:
                        self.NEW_WIDTH = int(sys.argv[1])
                        self.NEW_HEIGHT = int(sys.argv[2])
                except:
                    print("Usage: qcamera.py WIDTH HEIGHT\n")
                    MyDialog("Error", "Usage: qcamera.py WIDTH HEIGHT\n", self)
        #
        self.md=QMediaDevices(self)
        self.mc = QMediaCaptureSession()
        self._rec = QMediaRecorder()
        #######
        self.cameras = self.md.videoInputs()
        # 
        self.list_cams = []
        self.cam = None
        # [[cam,format,resolution,max_framerate,min_framerate]]
        self.camera_data = []
        for el in self.cameras:
            if not el.isNull():
                self.cam = QCamera()
                self.cam.setCameraDevice(el)
                # self.cam.setActive(True)
                self.list_cams.append(self.cam)
                #
                vvf = el.videoFormats()
                for vf in vvf:
                    _f = str(vf.pixelFormat())
                    _r = vf.resolution()
                    _mf = vf.minFrameRate()
                    _Mf = vf.maxFrameRate()
                    self.camera_data.append([self.cam,_f,_r,_mf,_Mf])
        #
        self.vw = QVideoWidget()
        # self.vw.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.vw.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.layout.addWidget(self.vw)
        self.vw.show()
        #
        self._menu = QMenu(self)
        # toggle titlebar
        act0 = QAction("Show/hide titlebar (Meta+t)", self)
        act0.triggered.connect(self.on_act0)
        self._menu.addAction(act0)
        # # toggle always on top
        # act1 = QAction("Toggle always on top (Meta+o)", self)
        # act1.triggered.connect(self.on_act1)
        # self._menu.addAction(act1)
        #
        self._menu.addSeparator()
        #
        self.sub_menu1 = QMenu(self)
        self.sub_menu1.setTitle("Webcams")
        self._menu.addMenu(self.sub_menu1)
        #
        self.act_rec = QAction("Record (Meta+a)", self)
        self.act_rec.triggered.connect(self.on_video_record)
        self.act_rec.dev = self.cam
        self._menu.addAction(self.act_rec)
        #
        self.act_img = QAction("Snapshot (Meta+c)", self)
        self.act_img.triggered.connect(self.on_image_capture)
        self.act_img.dev = self.cam
        self._menu.addAction(self.act_img)
        #
        self._menu.addSeparator()
        act_quit = QAction("Exit (Meta+q)", self)
        act_quit.triggered.connect(self.close)
        self._menu.addAction(act_quit)
        #
        self.list_actions = []
        if self.list_cams:
            # add and populate the context menu
            self.pop_menu_camera()
            #
            if self.cam:
                ret_cam, ret_mic = self.get_permissions()
                if ret_cam:
                    #
                    ret = self.find_best_resolution()
                    if ret:
                        try:
                            self.cam.setCameraFormat(ret)
                        except:
                            pass
                    #
                    self.on_set_webcam(ret_mic)
        #
        self.md.videoInputsChanged.connect(self.camera_changed)
        
    
    def find_best_resolution(self):
        _list = []
        _lt = None
        _l = None
        el = self.cam.cameraDevice()
        vvf = el.videoFormats()
        ### find the higher resolution
        # find the resolution requested
        if self.NEW_WIDTH > 0 and self.NEW_HEIGHT > 0:
            _res = (self.NEW_WIDTH,self.NEW_HEIGHT)
            for vf in vvf:
                _w = vf.resolution().width()
                _h = vf.resolution().height()
                _t = (_w,_h)
                if _t == _res:
                    _l = vf
                    _lt = _t
                    break
        #
        # then find the best 16/9 resolution
        if _l == None:
            for vf in vvf:
                _w = vf.resolution().width()
                _h = vf.resolution().height()
                _t = (_w,_h)
                if _t not in _list:
                    if _t[0]/_t[1] > 1.7:
                        _list.append(_t)
                        _lt = _t
                        _l = vf
                else:
                    if _t > _lt:
                        if _t[0]/_t[1] > 1.7:
                            _list.append(_t)
                            _lt = _t
                            _l = vf
        # find the best resolution
        if _l == None:
            _lt = None
            for vf in vvf:
                _w = vf.resolution().width()
                _h = vf.resolution().height()
                _t = (_w,_h)
                if _t not in _list:
                    _list.append(_t)
                    _lt = _t
                    _l = vf
                else:
                   if _t > _lt:
                        _list.append(_t)
                        _lt = _t
                        _l = vf
        #
        self.resize(int(_lt[0]/self.pixel_ratio), int(_lt[1]/self.pixel_ratio))
        # reset
        self.NEW_WIDTH = -1
        self.NEW_HEIGHT = -1
        return _l
        
        
    def pop_menu_camera(self):
        for _cam in self.list_cams:
            self.on_pop_menu_camera(_cam)
        
    def on_pop_menu_camera(self, _cam):
        act2 = QAction(_cam.cameraDevice().description(), self)
        act2.triggered.connect(self.on_act2)
        act2.dev = _cam
        self.sub_menu1.addAction(act2)
        self.list_actions.append([_cam, act2])
        #
        menu1 = QMenu(self)
        menu1.setTitle(_cam.cameraDevice().description() + " 2")
        act2.setMenu(menu1)
        #
        menu2 = QMenu(self)
        menu2.setTitle("Format")
        menu1.addMenu(menu2)
        #########
        # list of all list_cam_type_tmp
        list_cam_type = []
        # [format,resolution,Mf,mf]
        list_cam_type_tmp = []
        #
        list_formats = []
        #
        # [[cam,format,resolution,max_framerate,min_framerate]]
        # self.camera_data
        for _d in self.camera_data:
            if _d[0] == _cam:
                if list_cam_type_tmp == [] or _d[1] == list_cam_type_tmp[0][0]:
                    list_cam_type_tmp.append(_d[1:])
                    #
                    if not _d[1] in list_formats:
                        list_formats.append(_d[1])
                else:
                    list_cam_type.append(list_cam_type_tmp)
                    list_cam_type_tmp = []
        #
        # adding the last list
        list_cam_type.append(list_cam_type_tmp)
        list_cam_type_tmp = []
        #
        for _f in list_formats:
            _txt = _f.split("_")[1]
            actf = QAction(_txt, self)
            actf._f = _f
            actf.triggered.connect(self.on_actf)
            menu2.addAction(actf)
        # 
        # if list_formats:
            actfm = QMenu(self)
            actf.setMenu(actfm)
            _type = None
            # type iteration
            for _el in list_cam_type:
                # element iteration
                for ell in _el:
                    if ell[0] == _type:
                        continue
                    if _type == None:
                        _type = ell[0]
                    #
                    _size_w = ell[1].width()
                    _size_h = ell[1].height()
                    _txt = "{}x{}".format(_size_w,_size_h)
                    #
                    act3 = QAction(_txt, self)
                    act3._f = ell
                    act3.dev = _cam
                    actfm.addAction(act3)
                    act3.triggered.connect(self.on_act3)
        
    def on_actf(self):
        print("ACTf", self.sender()._f)
        
    def on_act3(self):
        _sender_data = self.sender()._f
        el = self.cam.cameraDevice()
        vvf = el.videoFormats()
        for vf in vvf:
            if str(vf.pixelFormat()) == _sender_data[0]:
                if vf.resolution() == _sender_data[1]:
                    # _w = _sender_data[1].width()
                    # _h = _sender_data[1].height()
                    self.cam.setCameraFormat(vf)
                    self.on_act2(vf)
                    break
    
    def get_permissions(self):
        ret_cam = 1
        ret_mic = 0
        #
        # cam_permission = QCameraPermission()
        # cam_permission_status = QApplication.instance().checkPermission(cam_permission)
        # ret_cam = int(cam_permission_status == Qt.PermissionStatus.Granted)
        #
        if not self.cam.isAvailable():
            ret_cam = 0
        #
        # microphone_permission = QMicrophonePermission()
        # microphone_permission_status = QApplication.instance().checkPermission(microphone_permission)
        # ret_mic = int(microphone_permission_status == Qt.PermissionStatus.Granted)
        #
        return (ret_cam, ret_mic)
    
    def on_set_webcam(self, ret_mic):
        self.cam.start()
        #
        self.mc.setCamera(self.cam)
        self.mc.setVideoOutput(self.vw)
        ##### video rec
        self.mc.setRecorder(self._rec)
        #
        medf = QMediaFormat()
        medf.setVideoCodec(QMediaFormat.VideoCodec.MPEG4)
        self._rec.setMediaFormat(medf)
        # ######### optional
        # self._rec.setVideoBitRate(800000)
        # NormalQuality HighQuality VeryHighQuality LowQuality VeryLowQuality
        # self._rec.setQuality(QMediaRecorder.Quality.NormalQuality)
        self._rec.setQuality(QMediaRecorder.Quality.HighQuality)
        # self._rec.setVideoResolution(640,360)
        ##### audio rec
        # if ret_mic:
        self.ai = QAudioInput()
        self.mc.setAudioInput(self.ai)
        # # NormalQuality HighQuality VeryHighQuality LowQuality VeryLowQuality
        self._rec.setQuality(QMediaRecorder.Quality.NormalQuality)
        #
        ########## image capture
        self.ic =  QImageCapture(self.cam)
        self.mc.setImageCapture(self.ic)
        self.ic.setFileFormat(QImageCapture.FileFormat.JPEG)
        # self.ic.setResolution(320,240)
    
    def on_video_record(self):
        if self.cam == None or self.cam.cameraDevice().isNull():
            return
        # StoppedState PausedState RecordingState
        _state = self._rec.recorderState()
        if _state == QMediaRecorder.RecorderState.RecordingState:
            self._rec.stop()
            self.act_rec.setText("Record (Meta+a)")
            self.setWindowTitle(APP_TITLE)
        else:
            unix_time = time.time()
            _date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d_%H:%M:%S')
            _name = "Record-"+_date
            global VIDEOS_PATH
            if not os.path.exists(VIDEOS_PATH) or not os.access(VIDEOS_PATH, os.W_OK):
                VIDEOS_PATH = os.path.expanduser("~")
            self._rec.setOutputLocation(QUrl.fromLocalFile("{}/{}".format(VIDEOS_PATH,_name)))
            self._rec.record()
            self.act_rec.setText("Recording... (Meta+a)")
            self.setWindowTitle("{} - Recording...".format(APP_TITLE))
    
    def on_image_capture(self):
        if self.cam == None or self.cam.cameraDevice().isNull():
            return
        ########## image capture
        unix_time = time.time()
        _date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d_%H:%M:%S')
        _name = "Snapshot-"+_date+".jpg"
        #
        global PICTURES_PATH
        if not os.path.exists(PICTURES_PATH) or not os.access(PICTURES_PATH, os.W_OK):
            PICTURES_PATH = os.path.expanduser("~")
        self.ic.captureToFile("{}/{}".format(PICTURES_PATH, _name))
        self.ic.capture()
    
    # camera added or removed
    def camera_changed(self):
        self.cameras = self.md.videoInputs()
        cam = None
        # add a new camera
        for el in self.cameras:
            if not el.isNull():
                cam = QCamera()
                cam.setCameraDevice(el)
                if not cam in self.list_cams:
                    self.list_cams.append(cam)
                    self.on_pop_menu_camera(cam)
                else:
                    del cam
        # remove a no more available camera
        for _c in self.list_cams[:]:
            el = _c.cameraDevice()
            if el not in self.cameras:
                self.list_cams.remove(_c)
                # [cam, action]
                for ell in self.list_actions:
                    if isinstance(ell[1], QAction):
                        _cam = ell[0]
                        if _cam == _c:
                            self.sub_menu1.removeAction(ell[1])
                            if _c.isActive():
                                _c.stop()
                            # del _c
        #
        if self.cam == None or self.cam.cameraDevice().isNull():
            self.cam = cam
            if len(self.list_cams) == 1:
                # self.cam.start()
                ret_cam,ret_mic = self.get_permissions()
                if ret_cam:
                    ret = self.find_best_resolution()
                    if ret:
                        try:
                            self.cam.setCameraFormat(ret)
                        except:
                            pass
                    self.on_set_webcam(ret_mic)
        else:
            if self.cam.cameraDevice().isNull() or self.list_cams == []:
                self.cam = None
    
    # toggle window titlebar
    def on_act0(self):
        if self.windowFlags() & Qt.WindowType.FramelessWindowHint:
            self.setWindowFlags( self.windowFlags() & ~Qt.WindowType.FramelessWindowHint )
        else:
            self.setWindowFlags( self.windowFlags() | Qt.WindowType.FramelessWindowHint )
        self.show()
        
    # toggle stay on top
    def on_act11(self):
        if self.windowFlags() & Qt.WindowType.CustomizeWindowHint:
            self.setWindowFlags( self.windowFlags() & ~Qt.WindowType.CustomizeWindowHint )
        else:
            self.setWindowFlags( Qt.WindowType.CustomizeWindowHint )
        self.show()
    
    # toggle stay on top
    def on_act1(self):
        # if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            # self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        # else:
            # self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        # self.show()
        
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            self.setWindowFlags(~Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
            # self.setWindowFlags(self.windowFlags() | Qt.WindowType.X11BypassWindowManagerHint | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
    
    # activate a new camera/change resolution
    def on_act2(self, _data=None):
        _cam = self.sender().dev
        # if _cam == self.cam:
            # print("SAME CAM")
            # return
        _isActive = _cam.isActive()
        for _c in self.list_cams:
            if _c.isActive():
                _c.stop()
        # if _isActive:
            # _cam.stop()
        #
        if not _cam.cameraDevice().isNull():
            self._cam = _cam
            ret_cam, ret_mic = self.get_permissions()
            if ret_cam:
                if _data != None:
                    self.cam.setCameraFormat(_data)
                    ret = _data.resolution()
                    self.resize(int(ret.width()/self.pixel_ratio), int(ret.height()/self.pixel_ratio))
                self.on_set_webcam(ret_mic)
        
    def mousePressEvent(self, event):
        if event.button() ==  Qt.MouseButton.RightButton:
            self._menu.popup(self.mapToGlobal(event.pos()))
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.MetaModifier:
            key = event.key()
            # exit
            if key == Qt.Key.Key_Q:
                self.close()
                event.accept()
            # toggle window decoration
            elif key == Qt.Key.Key_T:
                self.on_act0()
                event.accept()
            # # toggle always on top
            # elif key == Qt.Key.Key_O:
                # self.on_act1()
                # event.accept()
            # video recordint
            elif key == Qt.Key.Key_A:
                self.on_video_record()
                event.accept()
            # image capture
            elif key == Qt.Key.Key_C:
                self.on_image_capture()
                event.accept()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        new_w = int(event.size().width()*self.pixel_ratio)
        new_h = int(event.size().height()*self.pixel_ratio)
        if new_w != int(WINW) or new_h != int(WINH):
            try:
                ifile = open("winsize.cfg", "w")
                ifile.write("{};{}".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                MyDialog("Error", str(E), self)
                
    def closeEvent(self, event):
        app.instance().quit()


# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Icon.Information)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Icon.Critical)
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Icon.Question)
            self.setStandardButtons(QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)
        # self.setWindowIcon(QIcon("icons/.svg"))
        self.setWindowTitle(args[0])
        self.resize(dialWidth,100)
        self.setText(args[1])
        retval = self.exec()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 
        return result



#################
if __name__ == '__main__':
    app = QApplication([])
    QGuiApplication.setDesktopFileName("qcamera")
    window = MainWindow()
    app.exec()
