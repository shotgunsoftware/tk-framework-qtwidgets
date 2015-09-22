# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sgtk
import tempfile

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from sgtk.platform.qt import QtCore, QtGui

from sgtk import TankError

from .ui.note_input_widget import Ui_NoteInputWidget
from .overlaywidget import SmallOverlayWidget
from .. import screen_grab  
 

 
 
 
class NoteInputWidget(QtGui.QWidget):
    """
    Widget that can be used for note and thumbnail input and creation.
    """
    
    _EDITOR_WIDGET_INDEX = 0
    _NEW_NOTE_WIDGET_INDEX = 1
    
    # emitted when shotgun has been updated
    data_updated = QtCore.Signal()
    close_clicked = QtCore.Signal()
    
    
    def __init__(self, parent):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteInputWidget() 
        self.ui.setupUi(self)

        self._load_stylesheet()
        
        # set up some handy references
        self._app = sgtk.platform.current_bundle()        
        self._camera_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/camera_hl.png"))
        self._trash_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_multi_infopanel_note_input_widget/trash.png"))
        
        # initialize state variables
        self._processing_id = None      # async task id
        self._entity_type = None        # current associated entity
        self._entity_id = None        # current associated entity 
        self._pixmap = None             # 

        # set up an overlay that spins when note is submitted
        self.__overlay = SmallOverlayWidget(self)
        
        # create a separate sg data handler for submission
        self.__sg_data_retriever = None
        
        # hook up signals and slots
        self.ui.screenshot.clicked.connect(self._screenshot_or_clear)
        self.ui.submit.clicked.connect(self._submit)
        self.ui.close.clicked.connect(self._cancel)
        self.ui.close.clicked.connect(self.close_clicked)

        # reset state of the UI
        self.clear()
        
        
    def destroy(self):
        """
        disconnect and prepare for this object
        to be garbage collected
        """
        self.ui.text_entry.destroy()
        if self.__sg_data_retriever:
            self.__sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
            self.__sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
            self.__sg_data_retriever = None
        
    def set_data_retriever(self, data_retriever):
        """
        Create a separate sg data handler for submission
        """
        self.__sg_data_retriever = data_retriever
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        
        self.ui.text_entry.set_data_retriever(data_retriever)
        
        
        
    ###########################################################################
    # internal methods

    def mousePressEvent(self, event):
        """
        User clicks the preview part of the widget
        """
        self.open_editor()

    def _cancel(self):
        """
        Cancel editing, no questions asked 
        """
        self.clear()

    def _screenshot_or_clear(self):
        """
        Screenshot button is clicked. This either means that 
        a screenshot should be taken or that it should be cleared.
        """
        if self._pixmap is None:
            # no pixmap exists - screengrab mode
            self._app.log_debug("Prompting for screenshot...")
            self._pixmap = screen_grab.screen_capture()
            self._app.log_debug("Got screenshot %sx%s" % (self._pixmap.width(), 
                                                          self._pixmap.height()))
            
            thumb = self.__format_thumbnail(self._pixmap)
            self.ui.thumbnail.setPixmap(thumb)
            self.ui.thumbnail.show()
            # turn the button into a delete screenshot button
            self.ui.screenshot.setIcon(self._trash_icon)
            self.ui.screenshot.setToolTip("Remove Screenshot")
        
        else:
            # there is a screenshot - that means the user clicked the trash bit 
            self._pixmap = None
            self.ui.thumbnail.hide()
            
            # turn the button into a screenshot button
            self.ui.screenshot.setIcon(self._camera_icon)
            self.ui.screenshot.setToolTip("Take Screenshot")
        
        
    def _submit(self):
        """
        Creates items in Shotgun and clears the widget.
        """
        
        if self.ui.text_entry.toPlainText() == "":
            QtGui.QMessageBox.information(self, 
                                          "Please Add Note",
                                          "Please add some content before submitting.")
            return
        
        
        # hide hint label for better ux.
        self.ui.hint_label.hide()
        self.__overlay.start_spin()
        
        # get all publish details from the UI
        # and submit an async request
        data = {}
        data["pixmap"] = self._pixmap
        data["text"] = self.ui.text_entry.toPlainText()
        data["recipient_links"] = self.ui.text_entry.get_recipient_links()
        data["entity"] = {"id": self._entity_id, "type": self._entity_type }
        data["project"] = self._app.context.project
        # ask the data retriever to execute an async callback
        self._processing_id = self.__sg_data_retriever.execute_method(self._async_submit, data)
        
    def _async_submit(self, sg, data):
        """
        Actual payload for creating things in shotgun.
        Note: This runs in a different thread and cannot access
        any QT UI components.
        
        :param sg: Shotgun instance
        :param data: data dictionary passed in from _submit()
        """
        entity_link = data["entity"]
        if entity_link["type"] == "Note":
            # we are replying to a note - create a reply
            return self._async_submit_reply(sg, data)
        else:
            # create a new note
            return self._async_submit_note(sg, data)
        
    def _async_submit_reply(self, sg, data):
        """
        Create a new reply
        """
        
        note_link = data["entity"]
        
        # this is an entity - so create a note and link it
        sg.create("Reply", {"content": data["text"], "entity": note_link})

        # if there are any recipients, make sure they are added to the note
        # but as CCs
        if data["recipient_links"]:
            existing_to = sg.find_one("Note", 
                                      [["id", "is", note_link["id"]]], 
                                      ["addressings_cc"]).get("addressings_cc")
            
            updated_links = data["recipient_links"] + existing_to 
            
            sg.update("Note", 
                      note_link["id"], 
                      {"addressings_cc": updated_links})
            
            
        self.__upload_thumbnail(note_link, sg, data)        
                
        
    def _async_submit_note(self, sg, data):
        # note - no logging in here, as I am not sure how all 
        # engines currently react to log_debug() async.
        
        # step 1 - extend out the link dictionary according to specific logic.
        # - if link is a version, then also include the item the version 
        #   is linked to and the version's task
        
        # - if a link is a task, find its link and use that as the main link. 
        #   set the task to be linked up to the tasks field.
        
        # - if link is a user, group or script then address the note TO 
        #   that user rather associating the user with the note. 
        
        
        # first establish defaults        
        project = data["project"]
        addressings_to = data["recipient_links"]
        note_links = []
        note_tasks = []
        
        
        # now apply specific logic
        entity_link = data["entity"]
        
        if entity_link["type"] in ["HumanUser", "ApiUser", "Group"]:            
            # for users, scripts and groups,
            # address the note TO the entity
            addressings_to.append(entity_link)

            # Also link the note to the user. This is to get the 
            # activity stream logic to work.
            # note that because we don't have the display name for the entity,
            # we need to retrieve this
            sg_entity = sg.find_one(entity_link["type"], 
                                    [["id", "is", entity_link["id"] ]], 
                                    ["cached_display_name"])
            note_links += [{"id": entity_link["id"], 
                           "type": entity_link["type"], 
                           "name": sg_entity["cached_display_name"] }] 
            
        
        elif entity_link["type"] == "Version":
            # if we are adding a note to a version, link it with the version 
            # and the entity that the version is linked to.
            # if the version has a task, link the task to the note too.  
            sg_version = sg.find_one("Version", 
                                     [["id", "is", entity_link["id"] ]], 
                                     ["entity", "sg_task", "cached_display_name"])
            
            # first make a std sg link to the current entity - this to ensure we have a name key present
            note_links += [{"id": entity_link["id"], 
                            "type": entity_link["type"], 
                            "name": sg_version["cached_display_name"] }] 
            
            # and now add the linked entity, if there is one
            if sg_version["entity"]:
                note_links += [sg_version["entity"]]
            
            if sg_version["sg_task"]:
                note_tasks += [sg_version["sg_task"]]
            
        elif entity_link["type"] == "Task":
            # if we are adding a note to a task, link the note to the entity that is linked to the
            # task. The link the task to the note via the task link.
            sg_task = sg.find_one("Task", 
                                  [["id", "is", entity_link["id"] ]], 
                                  ["entity"])
            
            if sg_task["entity"]:
                # there is an entity link from this task
                note_links += [sg_task["entity"]]
            
            # lastly, link the note's task link to this task            
            note_tasks += [entity_link]
        
        else:
            # no special logic. Just link the note to the current entity.
            # note that because we don't have the display name for the entity,
            # we need to retrieve this
            sg_entity = sg.find_one(entity_link["type"], 
                                    [["id", "is", entity_link["id"] ]], 
                                    ["cached_display_name"])
            note_links += [{"id": entity_link["id"], 
                           "type": entity_link["type"], 
                           "name": sg_entity["cached_display_name"] }] 
        
        
        
        
        # step 2 - generate the subject line. The following
        # convention exists for this:
        #
        # Tomoko's Note on aaa_00010_F004_C003_0228F8_v000 and aaa_00010
        # First name's Note on [list of entities]
        current_user = sgtk.util.get_current_user(self._app.sgtk)
        if current_user:
            if current_user.get("firstname"):
                # not all core versions support firstname,
                # so double check that we have that key
                first_name = current_user.get("firstname")
            else:
                # compatibility with older cores
                # for older cores, just split on the first space
                # Sorry Mary Jane Watson!
                first_name = current_user.get("name").split(" ")[0]
                
            title = "%s's Note" % first_name 
        else:
            title = "Unknown user's Note"
        
        if len(note_links) > 0:
            note_names = [x["name"] for x in note_links]
            title += " on %s" % (", ".join(note_names))

        # this is an entity - so create a note and link it
        sg_note_data = sg.create("Note", {"content": data["text"],
                                          "subject": title, 
                                          "project": project,
                                          "addressings_to": addressings_to,
                                          "note_links": note_links,
                                          "tasks": note_tasks })
        
        self.__upload_thumbnail(sg_note_data, sg, data)
        
        
    def __upload_thumbnail(self, parent_entity, sg, data):
        
        if data["pixmap"]:
            
            # save it out to a temp file so we can upload it
            png_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                   prefix="screencapture_",
                                                   delete=False).name
    
            data["pixmap"].save(png_path)
            
            # create file entity and upload file
            if os.path.exists(png_path):
                self._app.log_debug("Uploading attachment (%s bytes)..." % os.path.getsize(png_path))
                sg.upload(parent_entity["type"], parent_entity["id"], png_path)
                self._app.log_debug("Upload complete!")            
                os.remove(png_path)
        
    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        
        :param uid: Unique id for request that failed
        :param msg: Error message
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)

        if self._processing_id == uid:        
            self._app.log_error("Could not create note/reply: %s" % msg)
            full_msg = "Could not submit note update: %s" % msg
            QtGui.QMessageBox.critical(None, "Shotgun Error", msg)
    

    def __on_worker_signal(self, uid, request_type, data):
        """
        Signaled whenever the worker completes something.
        This method will dispatch the work to different methods
        depending on what async task has completed.

        :param uid: Unique id for request
        :param request_type: String identifying the request class
        :param data: the data that was returned 
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        data = shotgun_model.sanitize_qt(data)

        if self._processing_id == uid:
            # all done!
            self.__overlay.hide()
            self.clear()
            self._app.log_debug("Update call complete! Return data: %s" % data)
            self.data_updated.emit()
            
        
    def __format_thumbnail(self, pixmap_obj):
        """
        Given a screengrab, create a thumbnail object, scaled to 96x75 px
        and with a subtle rounded frame.
        
        :param pixmap_obj: input screenshot
        :returns: 96x75px pixmap 
        """
        CANVAS_WIDTH = 96
        CANVAS_HEIGHT = 75
        CORNER_RADIUS = 6
    
        # get the 512 base image
        base_image = QtGui.QPixmap(CANVAS_WIDTH, CANVAS_HEIGHT)
        base_image.fill(QtCore.Qt.transparent)
        
        # scale it down to fit inside a frame of maximum 512x512
        thumb_scaled = pixmap_obj.scaled(CANVAS_WIDTH, 
                                         CANVAS_HEIGHT, 
                                         QtCore.Qt.KeepAspectRatioByExpanding, 
                                         QtCore.Qt.SmoothTransformation)  

        # now composite the thumbnail on top of the base image
        # bottom align it to make it look nice
        thumb_img = thumb_scaled.toImage()
        brush = QtGui.QBrush(thumb_img)
        
        painter = QtGui.QPainter(base_image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(brush)

        pen = QtGui.QPen(QtGui.QColor("#2C93E2"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        # note how we have to compensate for the corner radius
        painter.drawRoundedRect(0,  
                                0, 
                                CANVAS_WIDTH, 
                                CANVAS_HEIGHT, 
                                CORNER_RADIUS, 
                                CORNER_RADIUS)
        
        painter.end()
        
        return base_image        
        
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
        
        
    ###########################################################################
    # public interface
        
    def open_editor(self):
        """
        Set the editor into its "open mode"
        where a user can type in stuff
        """
        self.ui.stacked_widget.setCurrentIndex(self._EDITOR_WIDGET_INDEX)
        self.ui.hint_label.show()
        self._adjust_ui()        
        self.ui.text_entry.setFocus()
        
    def _adjust_ui(self):
        """
        adjust the UI to be optimal size depending on view
        """
        if self.ui.stacked_widget.currentIndex() == self._NEW_NOTE_WIDGET_INDEX:
            self.setMinimumSize(QtCore.QSize(0, 80))
            self.setMaximumSize(QtCore.QSize(16777215, 80))
             
        elif self.ui.stacked_widget.currentIndex() == self._EDITOR_WIDGET_INDEX:
            self.setMinimumSize(QtCore.QSize(0, 120))
            self.setMaximumSize(QtCore.QSize(16777215, 120))
             
        else:
            self._app.log_warning("cannot adjust unknown ui mode.")             
              
    def clear(self):
        """
        Clear any input and state        
        """
        self.ui.text_entry.clear()

        self.ui.stacked_widget.setCurrentIndex(self._NEW_NOTE_WIDGET_INDEX)
        
        self._adjust_ui()        
        
        # reset data state
        self._processing_id = None
        self._pixmap = None
        
        # make sure the screenshot button shows the camera icon
        self.ui.thumbnail.hide()
        self.ui.hint_label.hide()
        self.ui.screenshot.setIcon(self._camera_icon)
        self.ui.screenshot.setToolTip("Take Screenshot")
        
        return True
        
    def set_current_entity(self, entity_type, entity_id):
        """
        Specify the current entity that this widget is linked against
        
        :param entity_link: Std entity link dictionary with type and id
        """
        self._entity_type = entity_type
        self._entity_id = entity_id


