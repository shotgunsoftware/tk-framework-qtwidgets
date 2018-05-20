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
import os.path
import sgtk
import tempfile

# local import to avoid cyclic references
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")

from sgtk.platform.qt import QtCore, QtGui

from sgtk import TankError

from .ui.note_input_widget import Ui_NoteInputWidget
from .overlaywidget import SmallOverlayWidget  
 
 
class NoteInputWidget(QtGui.QWidget):
    """
    Note creation and reply widget with built in screen capture capabilites.
    
    :signal data_updated: Emitted when a note has been successfully created or 
        replied to. 
    :signal close_clicked: Emitted if a user chooses to cancel the note 
        creation by clicking the X button.
    :signal entity_created: Emitted when a Shotgun entity is created, which
        will be either a Note or Reply entity, depending on situation. The
        entity dictionary, as provided by the API, will be sent.
    """
    
    _EDITOR_WIDGET_INDEX = 0
    _NEW_NOTE_WIDGET_INDEX = 1
    _ATTACHMENTS_WIDGET_INDEX = 2
    
    # emitted when shotgun has been updated
    data_updated = QtCore.Signal()
    close_clicked = QtCore.Signal()

    # Emitted when a Note or Reply entity is created. The
    # entity type as a string and id as an int will be
    # provided.
    #
    # dict(entity_type="Note", id=1234)
    entity_created = QtCore.Signal(object)
    
    
    def __init__(self, parent):
        """
        :param parent:              The parent QWidget for this control
        :type parent:               :class:`~PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_NoteInputWidget() 
        self.ui.setupUi(self)

        self._load_stylesheet()
        
        # set up some handy references
        self._bundle = sgtk.platform.current_bundle()        
        self._camera_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_framework_qtwidgets.note_input_widget/camera_hl.png"))
        self._trash_icon = QtGui.QIcon(QtGui.QPixmap(":/tk_framework_qtwidgets.note_input_widget/trash.png"))
        
        # initialize state variables
        self._processing_id = None      # async task id
        self._entity_type = None        # current associated entity
        self._entity_id = None        # current associated entity 
        self._pixmap = None             # 
        self._attachments = []
        self._cleanup_after_upload = []

        # set up an overlay that spins when note is submitted
        self.__overlay = SmallOverlayWidget(self)
        
        # create a separate sg data handler for submission
        self.__sg_data_retriever = None
        
        # hook up signals and slots
        self.ui.screenshot.clicked.connect(self._screenshot_or_clear)
        self.ui.submit.clicked.connect(self._submit)
        self.ui.close.clicked.connect(self._cancel)
        self.ui.close.clicked.connect(self.close_clicked)
        self.ui.attach.clicked.connect(self.open_attachments)
        self.ui.add_attachments.clicked.connect(self._apply_attachments)
        self.ui.close_attachments.clicked.connect(self._cancel_attachments)
        self.ui.add_button.clicked.connect(self._add_attachments)
        self.ui.remove_button.clicked.connect(self._remove_selected_attachments)

        # reset state of the UI
        self.pre_submit_callback = None
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
            self.__sg_data_retriever.stop()
            self.__sg_data_retriever = None
        

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        # To stop the threads in self.ui.text_entry and
        # self.__sg_data_retriever
        self.destroy()

        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(
            self,
            bg_task_manager=task_manager
        )
        
        self.__sg_data_retriever.start()
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
        
        self.ui.text_entry.set_bg_task_manager(task_manager)
        
        
        
    ###########################################################################
    # internal methods

    def mousePressEvent(self, event):
        """
        User clicks the preview part of the widget
        """
        self.open_editor()

    def _add_attachments(self):
        """
        Allows the user to browse for files to attach to the Note
        entity.
        """
        file_paths = QtGui.QFileDialog.getOpenFileNames(
            self,
            "Select files to attach.",
        )

        self.add_files_to_attachments(file_paths[0])

    def _remove_selected_attachments(self):
        """
        Removes the selected attachments.
        """
        for item in self.ui.attachment_list_tree.selectedItems():
            self.ui.attachment_list_tree.takeTopLevelItem(
                self.ui.attachment_list_tree.indexOfTopLevelItem(item)
            )

    def _apply_attachments(self):
        """
        Updates the list of file attachments for the Note based
        on the list of items provided by the user.
        """
        self._attachments = []

        for index in range(self.ui.attachment_list_tree.topLevelItemCount()):
            item = self.ui.attachment_list_tree.topLevelItem(index)
            file_path = item.text(0)
            self._attachments.append(file_path)

        self.open_editor()

    def _cancel_attachments(self):
        """
        Cancel file attachment and revert to note editing.
        """
        self.ui.attachment_list_tree.clear()
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
        
        screen_grab = self._bundle.import_module("screen_grab")
        
        if self._pixmap is None:
            # no pixmap exists - screengrab mode
            self._bundle.log_debug("Prompting for screenshot...")
            pixmap = screen_grab.ScreenGrabber.screen_capture()

            # It's possible that there's custom screencapture logic
            # happening and we won't get a pixmap back right away.
            # A good example of this is something like RV, which
            # will handle screenshots itself and provide back the
            # image asynchronously.
            if pixmap:
                self._bundle.log_debug("Got screenshot %sx%s" % (pixmap.width(), 
                                                                 pixmap.height()))
                self._set_screenshot_pixmap(pixmap)
            
        
        else:
            # there is a screenshot - that means the user clicked the trash bit 
            self._pixmap = None
            self.ui.thumbnail.hide()
            
            # turn the button into a screenshot button
            self.ui.screenshot.setIcon(self._camera_icon)
            self.ui.screenshot.setToolTip("Take Screenshot")


    def _set_screenshot_pixmap(self, pixmap):
        """
        Takes the given QPixmap and sets it to be the thumbnail
        image of the note input widget.

        :param pixmap:  A QPixmap object containing the screenshot image.
        """
        self._pixmap = pixmap
        thumb = self.__format_thumbnail(pixmap)
        self.ui.thumbnail.setPixmap(thumb)
        self.ui.thumbnail.show()

        # turn the button into a delete screenshot button
        self.ui.screenshot.setIcon(self._trash_icon)
        self.ui.screenshot.setToolTip("Remove Screenshot")
        
        
    def _submit(self):
        """
        Creates items in Shotgun and clears the widget.
        """
        
        if self.ui.text_entry.toPlainText() == "":
            QtGui.QMessageBox.information(self, 
                                          "Please Add Note",
                                          "Please add some content before submitting.")
            return
        
        # Call our pre-submit callback if we have one registered.
        if self.pre_submit_callback:
            self.pre_submit_callback(self)

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
        data["project"] = self._bundle.context.project
        data["attachments"] = self._attachments

        # ask the data retriever to execute an async callback
        if self.__sg_data_retriever:
            self._processing_id = self.__sg_data_retriever.execute_method(self._async_submit, data)
        else:
            raise TankError("Please associate this class with a background task processor.")
        
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
        Provides functionality for creating a new Reply entity
        asynchronously by providing a signature that is friendly
        for use with :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever`.

        :param sg:      A Shotgun API handle.
        :param data:    A dictionary as created by :meth:`NoteInputWidget._submit`

        :returns:       A Shotgun entity dictionary for the Reply that was created.
        """
        note_link = data["entity"]
        
        # this is an entity - so create a note and link it
        sg_reply_data = sg.create("Reply", {"content": data["text"], "entity": note_link})

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
        self.__upload_attachments(note_link, sg, data)

        return sg_reply_data
        
    def _async_submit_note(self, sg, data):
        """
        Provides functionality for creating a new Note entity
        asynchronously by providing a signature that is friendly
        for use with :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever`.

        :param sg:      A Shotgun API handle.
        :param data:    A dictionary as created by :meth:`NoteInputWidget._submit`

        :returns:       A Shotgun entity dictionary for the Note that was created.
        """
        # note - no logging in here, as I am not sure how all
        # engines currently react to log_debug() async.

        # There is lots of business logic hard coded into Shotgun
        # for now, attempt to mimic this logic in this method.

        # Extend out the link dictionary according to specific logic:

        # - if link is a version, then also include the item the version
        #   is linked to and the version's task

        # - if a link is a task, find its link and use that as the main link.
        #   set the task to be linked up to the tasks field.

        # - if link is a user, group or script then address the note TO
        #   that user rather associating the user with the note.

        # - if data["project"] is None (which typically happens when running in a null-context
        #   environment, attempt to pick up the project from the associated entity.

        # first establish defaults
        project = data["project"]
        addressings_to = data["recipient_links"]

        # If the entity we're attaching the new Note to has a HumanUser
        # that created it, we need to make sure that the user is added
        # to the list.
        entity = sg.find_one(
            self._entity_type,
            [
                ["id", "is", self._entity_id],
            ],
            fields=["created_by"],
        )

        entity_created_by = entity.get("created_by")

        if entity_created_by and entity_created_by["type"] == "HumanUser":
            addressings_to.append(entity_created_by)

        note_links = []
        note_tasks = []

        # step 1 - business logic for linking
        # now apply specific logic
        entity_link = data["entity"]
        # as we are retrieving data for the associated
        # entity, also pull down the associated project
        entity_project_link = None

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
            sg_version = sg.find_one(
                "Version",
                [["id", "is", entity_link["id"] ]],
                ["entity", "sg_task", "cached_display_name", "project"]
            )

            # first make a std sg link to the current entity - this to ensure we have a name key present
            note_links += [{"id": entity_link["id"],
                            "type": entity_link["type"],
                            "name": sg_version["cached_display_name"] }]

            # and now add the linked entity, if there is one
            if sg_version["entity"]:
                note_links += [sg_version["entity"]]

            if sg_version["sg_task"]:
                note_tasks += [sg_version["sg_task"]]

            # If we weren't able to get a project ID from the context, then
            # we know we can get it from the Version entity itself.
            if not project and sg_version["project"]:
                project = sg_version["project"]

        elif entity_link["type"] == "Task":
            # if we are adding a note to a task, link the note to the entity that is linked to the
            # task. The link the task to the note via the task link.
            sg_task = sg.find_one(
                "Task",
                [["id", "is", entity_link["id"]]],
                ["entity", "project"]
            )

            if sg_task["entity"]:
                # there is an entity link from this task
                note_links += [sg_task["entity"]]

            # If we didn't get a project ID from the context, then we know we
            # can get one from the Task entity.
            if not project and sg_task["project"]:
                project = sg_task["project"]

            # lastly, link the note's task link to this task
            note_tasks += [entity_link]

        else:
            # no special logic. Just link the note to the current entity.
            # note that because we don't have the display name for the entity,
            # we need to retrieve this
            sg_entity = sg.find_one(entity_link["type"],
                                    [["id", "is", entity_link["id"] ]],
                                    ["cached_display_name", "project"])
            note_links += [{"id": entity_link["id"],
                           "type": entity_link["type"],
                           "name": sg_entity["cached_display_name"] }]

            # store associated project for use later
            if entity_link["type"] == "Project":
                # note on a project
                entity_project_link = entity_link
            else:
                # note - some entity types may not have a project field
                # so don't assume the key exists.
                entity_project_link = sg_entity.get("project")


        # step 2 - generate the subject line. The following
        # convention exists for this:
        #
        # Tomoko's Note on aaa_00010_F004_C003_0228F8_v000 and aaa_00010
        # First name's Note on [list of entities]
        current_user = sgtk.util.get_current_user(self._bundle.sgtk)
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

        # step 3 - handle project gracefully
        if project is None:
            # attempt to pull it from the entity link
            if entity_project_link is None:
                # there is no associated project - likely this is a note
                # on a non-project entity created in the site ctx
                raise TankError(
                    "Cannot determine the project to associate the note with. "
                    "This usually happens when you submit note on a non-project "
                    "entity while running Toolkit in a Site context."
                )
            else:
                project = entity_project_link


        # this is an entity - so create a note and link it
        sg_note_data = sg.create("Note", {"content": data["text"],
                                          "subject": title,
                                          "project": project,
                                          "addressings_to": addressings_to,
                                          "note_links": note_links,
                                          "tasks": note_tasks })

        self.__upload_thumbnail(sg_note_data, sg, data)
        self.__upload_attachments(sg_note_data, sg, data)

        return sg_note_data

    def __upload_attachments(self, parent_entity, sg, data):
        """
        Uploads any generic file attachments to Shotgun, parenting
        them to the Note entity.

        :param parent_entity:   The Note entity to attach the files to in SG.
        :param sg:              A Shotgun API handle.
        :param data:            The data dict containing an "attachments" key
                                housing a list of file paths to attach.
        """
        for file_path in data.get("attachments", []):
            if os.path.exists(file_path):
                self.__upload_file(file_path, parent_entity, sg)
            else:
                self._bundle.log_warning(
                    "File does not exist and will not be uploaded: %s" % file_path
                )


    def __upload_file(self, file_path, parent_entity, sg):
        """
        Uploads any generic file attachments to Shotgun, parenting
        them to the Note entity.

        :param file_path:       The path to the file to upload to SG.
        :param parent_entity:   The Note entity to attach the files to in SG.
        :param sg:              A Shotgun API handle.
        """
        self._bundle.log_debug(
            "Uploading attachments (%s bytes)..." % os.path.getsize(file_path)
        )
        sg.upload(parent_entity["type"], parent_entity["id"], str(file_path))
        self._bundle.log_debug("Upload complete!")

        if file_path in self._cleanup_after_upload:
            self._bundle.log_debug("Cleanup requested post upload: %s" % file_path)
            try:
                os.remove(file_path)
            except Exception:
                self._bundle.log_warning("Unable to remove file: %s" % file_path)

        
    def __upload_thumbnail(self, parent_entity, sg, data):
        
        if data["pixmap"]:
            
            # save it out to a temp file so we can upload it
            png_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                   prefix="screencapture_",
                                                   delete=False).name
    
            data["pixmap"].save(png_path)
            
            # create file entity and upload file
            if os.path.exists(png_path):
                self.__upload_file(png_path, parent_entity, sg)           
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
            self._bundle.log_error("Could not create note/reply: %s" % msg)
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
            self._bundle.log_debug("Update call complete! Return data: %s" % data)
            self.data_updated.emit()
            self.entity_created.emit(data["return_value"])
            
        
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

    def add_files_to_attachments(self, file_paths, cleanup_after_upload=False, apply_attachments=False):
        """
        Adds the given list of file paths to the attachments list.

        :param file_paths:              A list of file paths to attach.
        :param cleanup_after_upload:    If True, the given files will be
                                        removed once they are uploaded to
                                        Shotgun.
        :param apply_attachments:       If True, files added to the attachments
                                        list will be applied and ready for upload.
                                        This is normally handled by the "check"
                                        button when accepting user-added files, but
                                        if this method is used to procedurally add
                                        attachments then this option must be used to
                                        ensure that the files end up attached to the
                                        Note when it is created.
        """
        for file_path in file_paths:
            self.ui.attachment_list_tree.addTopLevelItem(
                QtGui.QTreeWidgetItem([file_path])
            )

        if cleanup_after_upload:
            self._cleanup_after_upload.extend(file_paths)

        if apply_attachments:
            self._attachments.extend([os.path.normpath(f) for f in file_paths])

    def allow_screenshots(self, state):
        """
        Allows or disallows screenshots.

        :param state: Allow or disallow screenshots.
        :type  state: :class:`Boolean`
        """
        self.ui.screenshot.setVisible(bool(state))

    def open_attachments(self):
        """
        Sets the attachments editor into its "open mode" which will
        allow the user to attach files to the note.
        """
        self.ui.attachment_list_tree.clear()

        for file_path in self._attachments:
            self.ui.attachment_list_tree.addTopLevelItem(
                QtGui.QTreeWidgetItem([file_path])
            )

        self.ui.stacked_widget.setCurrentIndex(self._ATTACHMENTS_WIDGET_INDEX)
        self._adjust_ui()
        self._add_attachments()
        
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
            self.ui.stacked_widget.setStyleSheet(
                """
                #stacked_widget {
                    border: 1px solid rgba(200, 200, 200, 25%);
                    border-radius: 3px;
                }
                """
            )
             
        elif self.ui.stacked_widget.currentIndex() == self._EDITOR_WIDGET_INDEX:
            self.setMinimumSize(QtCore.QSize(0, 120))
            self.setMaximumSize(QtCore.QSize(16777215, 120))
            self.ui.stacked_widget.setStyleSheet("")

        elif self.ui.stacked_widget.currentIndex() == self._ATTACHMENTS_WIDGET_INDEX:
            self.setMinimumSize(QtCore.QSize(0, 120))
            self.setMaximumSize(QtCore.QSize(16777215, 120))
            self.ui.stacked_widget.setStyleSheet("")
             
        else:
            self._bundle.log_warning("cannot adjust unknown ui mode.")             
              
    def clear(self):
        """
        Clear any input and state and return the widget to its "closed" mode.   
        """
        self.ui.text_entry.clear()
        self.ui.attachment_list_tree.clear()

        self.ui.stacked_widget.setCurrentIndex(self._NEW_NOTE_WIDGET_INDEX)
        
        self._adjust_ui()        
        
        # reset data state
        self._processing_id = None
        self._pixmap = None
        self._attachments = []
        self._cleanup_after_upload = []
        
        # make sure the screenshot button shows the camera icon
        self.ui.thumbnail.hide()
        self.ui.hint_label.hide()
        self.ui.screenshot.setIcon(self._camera_icon)
        self.ui.screenshot.setToolTip("Take Screenshot")
        
        return True
        
    def set_current_entity(self, entity_type, entity_id):
        """
        Specify the current entity that this widget is linked against
        
        :param str entity_type: Shotgun entity type
        :param int entity_id: Shotgun entity id
        """
        self._entity_type = entity_type
        self._entity_id = entity_id


