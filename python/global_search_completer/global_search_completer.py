# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtCore, QtGui

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

class GlobalSearchCompleter(QtGui.QCompleter):


    # emitted when shotgun has been updated
    entity_selected = QtCore.Signal(str, int)
    entity_activated = QtCore.Signal(str, int, str)

    # custom roles for the model that tracks the auto completion results
    SG_DATA_ROLE = QtCore.Qt.UserRole + 1
    MODE_ROLE = QtCore.Qt.UserRole + 2

    # different items in the auto complete list can have
    # a different meaning, so track those here too
    (MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT) = range(3)

    def __init__(self, parent=None):

        super(GlobalSearchCompleter, self).__init__(parent)

        self.setMaxVisibleItems(10)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)

        # set up some handy references
        self._bundle = sgtk.platform.current_bundle()

        self.__sg_data_retriever = None

        self._processing_id = None
        self._thumb_map = {}
        self._default_icon = QtGui.QPixmap(":/tk_framework_qtwidgets.global_search_widget/rect_512x400.png")

        # configure popup data source
        self.setModel(QtGui.QStandardItemModel(self))
        self._clear_model()

        self._entity_search_criteria = {
            "Asset": [],
            "Shot": [],
            "Task": [],
            "HumanUser": [["sg_status_list", "is", "act"]],
            "Group": [],
            "ClientUser": [["sg_status_list", "is", "act"]],
            "ApiUser": [],
            "Version": [],
            "PublishedFile": [],
        }

    def destroy(self):
        """
        Should be called before the widget is closed
        """
        if self.__sg_data_retriever:
            self.__sg_data_retriever.stop()
            self.__sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
            self.__sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
            self.__sg_data_retriever = None

    def get_current_result(self):
        model_index = self.popup().currentIndex()
        return self.get_result(model_index)

    def get_result(self, model_index):

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

            # NOTE: this data format differs from what is typically returned by
            # the shotgun python-api. this data may be formalized at some point
            # but for now, only expose the minimum information.

            return {
                "type": data["type"],
                "id": data["id"],
                "name": data["name"],
            }
        else:
            return None

    def search(self, text):
        """
        Triggers the popup to display results based on the supplied text.

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

        popup = self.popup()
        self._delegate = SearchResultDelegate(popup)
        popup.setItemDelegate(self._delegate)

        # try to disconnect and reconnect the activated signal
        # it seems this signal is lost every time the widget
        # looses focus.
        try:
            self.activated[QtCore.QModelIndex].disconnect(self._on_select)
        except:
            self._bundle.log_debug(
                "Could not disconnect global search activated signal prior to "
                "reconnect. Looks like this connection must have been "
                "discarded at some point along the way."
            )

        self.activated[QtCore.QModelIndex].connect(self._on_select)

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
            self._processing_id = self.__sg_data_retriever.execute_method(
                self._do_sg_global_search, data)
        else:
            raise sgtk.TankError(
                "Please associate this class with a background task processor.")

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.

        :param task_manager: Background task manager to use
        :type  task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager`
        """
        self.__sg_data_retriever = shotgun_data.ShotgunDataRetriever(
            self, bg_task_manager=task_manager)

        self.__sg_data_retriever.start()
        self.__sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self.__sg_data_retriever.work_failure.connect(self.__on_worker_failure)

    def set_searchable_entity_types(self, types_dict):
        """
        Specify a dictionary of entity types with optional search filters to
        limit the breadth of the widget's search.

        Use this method to override the default searchable entity types
        dictionary which looks like this:

        {
            "Asset": [],
            "Shot": [],
            "Task": [],
            "HumanUser": [["sg_status_list", "is", "act"]],    # only active users
            "Group": [],
            "ClientUser": [["sg_status_list", "is", "act"]],   # only active users
            "ApiUser": [],
            "Version": [],
            "PublishedFile": [],
        }

        :param types_dict: A dictionary of searchable types with optional filters
        """
        self._entity_search_criteria = types_dict


    ############################################################################
    # internal methods

    def _clear_model(self, add_loading_item=True):
        """
        Clears the current data in the model.

        :param add_loading_item: if true, a "loading please wait" item will
                                 be added.
        """
        # clear model
        self.model().clear()

        if add_loading_item:
            item = QtGui.QStandardItem("Loading data...")
            item.setData(self.MODE_LOADING, self.MODE_ROLE)
            self.model().appendRow(item)

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

        # constrain by project in the search
        project_ids = []
        if self._bundle.context.project:
            project_ids.append(self._bundle.context.project["id"])

        # run the query
        sg_data = sg.text_search(
            data["text"],
            self._entity_search_criteria,
            project_ids
        )

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
                self.model().appendRow(item)

            # insert new data into model
            for d in matches:
                item = QtGui.QStandardItem(d["name"])
                item.setData(self.MODE_RESULT, self.MODE_ROLE)

                item.setData(shotgun_model.sanitize_for_qt_model(d),
                             self.SG_DATA_ROLE)

                item.setIcon(self._default_icon)

                if d.get("image", None) and self.__sg_data_retriever:
                    uid = self.__sg_data_retriever.request_thumbnail(
                        d["image"],
                        d["type"],
                        d["id"],
                        "image",
                        load_image=True
                    )
                    self._thumb_map[uid] = {"item": item}

                self.model().appendRow(item)

    def _on_select(self, model_index):
        """
        Fires when an item in the completer is selected.
        This will emit an entity_selected signal for the
        global search widget

        :param model_index: QModelIndex describing the current item
        """
        data = self.get_result(model_index)
        if data:
            self.entity_selected.emit(data["type"], data["id"])
            self.entity_activated.emit(data["type"], data["id"], data["name"])


