
import os
import sys
import sgtk
from tank.platform.qt import QtCore, QtGui

class ShotInfoWidget(QtGui.QWidget):


        def _load_stylesheet(self):
                """
                Loads in a stylesheet from disk
                """
                qss_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
                try:
                    f = open(qss_file, "rt")
                    qss_data = f.read()
                    # apply to widget (and all its children)
                    self.setStyleSheet(qss_data)
                finally:
                    f.close()

        

        def __init__(self, parent):
                QtGui.QWidget.__init__(self, parent)
                self._bundle = sgtk.platform.current_bundle()

                self.setGeometry(QtCore.QRect(0, 0, 414, 150))
                self.setMinimumSize(QtCore.QSize(300, 150))
                self.setMaximumSize(QtCore.QSize(414, 150))
                
                self.setObjectName("shot_info_widget")
                # self.setStyleSheet("QWidget { font-size: 13px; background: rgb(36,38,41); font-family: Proxima Nova; padding: 1px; padding-left: 4px; margin: 0px;} \
                #     #thumbnail { background: #44aa33;}\
                #     #shot_name { font-size: 15px; font-weight: normal; color: rgb(200,200,200)}\
                #     #shot_details { padding-left: 0px; }")

                self.shot_hbox = QtGui.QHBoxLayout()

                self.shot_thumbnail = QtGui.QLabel()
                self.shot_thumbnail.setGeometry(QtCore.QRect(0, 0, 113, 64))
                self.shot_thumbnail.setMinimumSize(QtCore.QSize(113, 64))
                self.shot_thumbnail.setMaximumSize(QtCore.QSize(113, 64))
                self.shot_thumbnail.setText("")
                self.shot_thumbnail.setScaledContents(True)
                #self.shot_thumbnail.setAlignment(QtCore.Qt.AlignCenter)
                self.shot_thumbnail.setObjectName("thumbnail")

                self.shot_name = QtGui.QLabel()
                self.shot_name.setText("08_a-team_007")
                self.shot_name.setObjectName("shot_name")
                self.shot_name.setMinimumSize(QtCore.QSize(200, 16))

                self.shot_version = QtGui.QLabel()
                self.shot_version.setText("08_a-team_007_COMP_010")
                self.shot_version.setObjectName("shot_version")
                self.shot_version.setMinimumSize(QtCore.QSize(200, 16))

                self.shot_vbox = QtGui.QVBoxLayout()
                self.shot_vbox.setSpacing(1)
                self.shot_vbox.addWidget(self.shot_name)
                self.shot_vbox.addWidget(self.shot_version)
                self.shot_vbox.setAlignment(QtCore.Qt.AlignTop)

                self.shot_hbox.addWidget(self.shot_thumbnail)
                self.shot_hbox.setSpacing(1)
                self.shot_hbox.addLayout(self.shot_vbox)

                self.shot_hbox.setAlignment(QtCore.Qt.AlignTop)
 
                self.shot_details = QtGui.QLabel()
                self.shot_details.setText("Artist name: Lenny Kruss, a really long date and something about pork bellies and brooklyn biodiesel. At least enough to get into a third line here which should be an elipsis button.")
                self.shot_details.setObjectName("shot_details")
                self.shot_details.setWordWrap(True)

                self.shot_main_vbox = QtGui.QVBoxLayout(self)
                self.shot_main_vbox.addLayout(self.shot_hbox)
                self.shot_main_vbox.addWidget(self.shot_details)

