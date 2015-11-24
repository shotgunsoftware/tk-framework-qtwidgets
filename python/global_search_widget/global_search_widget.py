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

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from sgtk.platform.qt import QtCore, QtGui
from sgtk import TankError
 
class GlobalSearchWidget(QtGui.QLineEdit):
    """
    A QT Widget deriving from :class:`~PySide.QtGui.QLineEdit` that creates
    a global search input box with auto completion.
    
    :signal entity_selected(str, int): Fires when someone selects an entity inside
            the search results. The returned parameters are entity type and entity id.
    """
    
    # custom roles for the model that tracks the auto completion results
    SG_DATA_ROLE = QtCore.Qt.UserRole + 1
    MODE_ROLE = QtCore.Qt.UserRole + 2
    
    # different items in the auto complete list can have 
    # a different meaning, so track those here too
    (MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT) = range(3)
    
    # emitted when shotgun has been updated
    entity_selected = QtCore.Signal(str, int)
    
    def __init__(self, parent):
        """
        :param parent: Qt parent object
        :type parent: :class:`~PySide.QtGui.QWidget`        
        """
 
        # first, call the base class and let it do its thing.
        QtGui.QLineEdit.__init__(self, parent)

        # set up some handy references
        self._bundle = sgtk.platform.current_bundle()
        
        self.__sg_data_retriever = None
        
        self._processing_id = None
        self._thumb_map = {}
        self._default_icon = QtGui.QPixmap(":/tk_framework_qtwidgets.global_search_widget/rect_512x400.png")
                
        # configure our popup completer
        self._completer = QtGui.QCompleter(self)
        self._completer.setMaxVisibleItems(10)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self._completer)

        # configure popup data source
        self._model = QtGui.QStandardItemModel(self) 
        self._clear_model()        
        self._completer.setModel(self._model)        
        
        # hook up completer and trigger reload on keypress
        self.textEdited.connect(self._on_text_changed)
        
    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.
        
        :param task_manager: Background task manager to use
        :type  task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager` 
        """
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(self, 
                                                                     bg_task_manager=task_manager)
        
        self.__sg_data_retriever.start()
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)
           
    def destroy(self):
        """
        Should be called before the widget is closed
        """
        if self.__sg_data_retriever:
            self.__sg_data_retriever.stop()
            self.__sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
            self.__sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
            self.__sg_data_retriever = None
           
    ############################################################################
    # internal methods
                
    def _clear_model(self, add_loading_item=True):
        """
        Clears the current data in the model.
        
        :param add_loading_item: if true, a "loading please wait" item will
                                 be added.
        """
        # clear model
        self._model.clear()
        
        if add_loading_item:
            item = QtGui.QStandardItem("Loading data...")
            item.setData(self.MODE_LOADING, self.MODE_ROLE)
            self._model.appendRow(item)
        
    def _on_text_changed(self, text):
        """
        Callback that fires when the user types something into
        the text editor.
        
        :param text: current contents of editor
        """
        if len(text) < 3:
            # global search wont work with shorter than 3 len strings
            # for these cases, clear the auto completer model fully
            # there is no more work to do
            self._clear_model(add_loading_item=False)
            return
        
        # now we are about to populate the model with data 
        # and therefore trigger the completer to pop up.
        #
        # The completer seems to have some internal properties
        # which are transitory and won't last between sessions.
        # for these, we have to set them up every time the 
        # completion process is about to start it seems.
        
        # tell completer to render matches using our delegate
        # configure how the popup should look
        
        # deferred import to help documentation generation.
        from .search_result_delegate import SearchResultDelegate
        
        self._popup = self._completer.popup()
        self._delegate = SearchResultDelegate(self._popup)
        self._completer.popup().setItemDelegate(self._delegate)
        
        # try to disconnect and reconnect the activated signal
        # it seems this signal is lost every time the widget
        # looses focus.
        try:
            self._completer.activated[QtCore.QModelIndex].disconnect(self._on_completer_select)
        except:
            self._bundle.log_debug("Could not disconnect global search activated "
                                "signal prior to reconnect. Looks like this connection "
                                "must have been discarded at some point along the way.")
                
        self._completer.activated[QtCore.QModelIndex].connect(self._on_completer_select)
        
        # now clear the model
        self._clear_model()

        # clear download queue
        if self.__sg_data_retriever:
            self.__sg_data_retriever.clear()
        
        # clear thumbnail map
        self._thumb_map = {}
        
        # kick off async data request from shotgun 
        # we request to run an arbitrary method in the worker thread
        # this  _do_sg_global_search method will be called by the worker 
        # thread when the worker queue reaches that point and will 
        # call out to execute it. The data dictionary specified will
        # be forwarded to the method.        
        data = {"text": text}
        if self.__sg_data_retriever:
            self._processing_id = self.__sg_data_retriever.execute_method(self._do_sg_global_search, data)
        else:
            raise TankError("Please associate this class with a background task processor.")        
        
    def _do_sg_global_search(self, sg, data):
        """
        Actual payload for running a global search in Shotgun.
        
        Note: This runs in a different thread and cannot access
        any QT UI components. It should not do any logging and should
        be as minimal as possible.
        
        :param sg: Shotgun instance
        :param data: data dictionary passed in from _submit(). This dict
            carries the options payload and is forwarded over by the 
            sg_data.execute_method() method. In our case, the dictionary
            holds a single 'text' key which contains the search phrase.
        """
        
        # TODO: Make this configuration configurable
        
        entity_types = {}
        entity_types["Asset"] = []
        entity_types["Shot"] = []
        entity_types["Task"] = []
        entity_types["HumanUser"] = [["sg_status_list", "is", "act"]]
        entity_types["Group"] = []
        entity_types["ClientUser"] = [["sg_status_list", "is", "act"]]
        entity_types["ApiUser"] = []
        entity_types["Version"] = []
        entity_types["PublishedFile"] = []
        
        # constrain by project in the search
        project_ids = []
        if self._bundle.context.project:
            project_ids.append(self._bundle.context.project["id"])
        
        # run the query
        sg_data = sg.text_search(data["text"], entity_types, project_ids)
        return sg_data
        
    def __on_worker_failure(self, uid, msg):
        """
        Asynchronous callback - the worker thread errored.
        
        :param uid: Unique id for request that failed
        :param msg: Error message
        """
        uid = shotgun_model.sanitize_qt(uid) # qstring on pyqt, str on pyside
        msg = shotgun_model.sanitize_qt(msg)
        if self._processing_id == uid:
            self._bundle.log_warning("Could not retrieve search results: %s" % msg)
    
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

        if uid in self._thumb_map:
            thumbnail = data["image"]
            if thumbnail:
                item = self._thumb_map[uid]["item"]
                thumb = QtGui.QPixmap.fromImage(thumbnail)
                item.setIcon(thumb)
        

        if self._processing_id == uid:
            # all done!
            self._clear_model(add_loading_item=False)
            
            matches = data["return_value"]["matches"] 
            
            if len(matches) == 0:
                item = QtGui.QStandardItem("No matches found!")
                item.setData(self.MODE_NOT_FOUND, self.MODE_ROLE)
                self._model.appendRow(item)
                
            # insert new data into model
            for d in matches:
                item = QtGui.QStandardItem(d["name"])
                item.setData(self.MODE_RESULT, self.MODE_ROLE)                
                
                item.setData(shotgun_model.sanitize_for_qt_model(d), 
                             self.SG_DATA_ROLE)
                
                item.setIcon(self._default_icon)
                
                if d["image"] and self.__sg_data_retriever:
                    uid = self.__sg_data_retriever.request_thumbnail(d["image"], 
                                                                    d["type"], 
                                                                    d["id"], 
                                                                    "image",
                                                                    load_image=True)
                    self._thumb_map[uid] = {"item": item}
                
                self._model.appendRow(item)
            
        
        
    def _on_completer_select(self, model_index):
        """
        Fires when an item in the completer is selected.
        This will emit an entity_selected signal for the
        global search widget
        
        :param model_index: QModelIndex describing the current item
        """        
        # make sure that the user selected an actual shotgun item.
        # if they just selected the "no items found" or "loading please hold"
        # items, just ignore it.
        mode = shotgun_model.get_sanitized_data(model_index, self.MODE_ROLE)
        if mode == self.MODE_RESULT:

            # get the payload
            data = shotgun_model.get_sanitized_data(model_index, self.SG_DATA_ROLE)

            # Example of data stored in the data role:
            #
            # {'status': 'vwd', 
            #  'name': 'bunny_010_0050_comp_v001', 
            #  'links': ['Shot', 'bunny_010_0050'], 
            #  'image': 'https://xxx', 
            #  'project_id': 65, 
            #  'type': 'Version', 
            #  'id': 99}            
            
            # send out new signal
            self.entity_selected.emit(data["type"], data["id"])
        
