# Copyright (c) 2016 Shotgun Software Inc.
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

from .utils import create_rectangular_thumbnail, CompleterPixmaps


class SearchCompleter(QtGui.QCompleter):
    """
    A standalone :class:`PySide.QtGui.QCompleter` class for matching SG entities to typed text.

    :modes: ``MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT`` - Used to identify the
        mode of an item in the completion list

    :model role: ``MODE_ROLE`` - Stores the mode of an item in the completion
        list (see modes above)

    :model role: ``SG_DATA_ROLE`` - Role for storing shotgun data in the model

    Derived classes are expected to implement the following methods:
        - :method:``_handle_search_results``
        - :method:``_on_select``
        - :method:``_launch_sg_search``
        - :method:``_set_item_delegate``
        - :method:``get_result``
    """

    # custom roles for the model that tracks the auto completion results
    MODE_ROLE = QtCore.Qt.UserRole + 1
    SG_DATA_ROLE = QtCore.Qt.UserRole + 2

    COMPLETE_MINIMUM_CHARACTERS = 3

    # different items in the auto complete list can have
    # a different meaning, so track those here too
    (MODE_LOADING, MODE_NOT_FOUND, MODE_RESULT, MODE_NOT_ENOUGH_TEXT) = range(4)

    def __init__(self, parent=None):
        """
        :param parent: Parent widget
        :type parent: :class:`~PySide.QtGui.QWidget`
        """

        super(SearchCompleter, self).__init__(parent)

        self._pixmaps = CompleterPixmaps()

        self.setMaxVisibleItems(10)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)

        # set up some handy references
        self._bundle = sgtk.platform.current_bundle()

        self._sg_data_retriever = None

        self._processing_id = None
        self._thumb_map = {}

        # configure popup data source
        self.setModel(QtGui.QStandardItemModel(self))
        self._clear_model()

        # the result widgets are 300 pixels wide. the widget using this
        # completer may be relatively small, but the results can show a lot of
        # info. so for now, just force the popup to be at least the same as the
        # results
        self.popup().setMinimumWidth(300)

        # ensure the icon size is consistent
        self.popup().setIconSize(QtCore.QSize(48, 38))

    def clear(self):
        """
        Manually clear the contents of the completer's popup view.
        """
        self._clear_model(add_loading_item=False, add_more_text_item=True)

    def destroy(self):
        """
        Should be called before the widget is closed
        """
        if self._sg_data_retriever:
            self._sg_data_retriever.stop()
            self._sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
            self._sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
            self._sg_data_retriever = None

    def search(self, text):
        """
        Triggers the popup to display results based on the supplied text.

        :param text: current contents of editor
        """
        if len(text) < self.COMPLETE_MINIMUM_CHARACTERS:
            # global search wont work with shorter than 3 len strings
            # for these cases, clear the auto completer model fully
            # there is no more work to do
            self.clear()
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

        self._set_item_delegate(self.popup(), text)

        # try to disconnect and reconnect the activated signal
        # it seems this signal is lost every time the widget
        # looses focus.
        try:
            self.activated[QtCore.QModelIndex].disconnect(self._on_select)
        except Exception:
            self._bundle.log_debug(
                "Could not disconnect activated signal prior to "
                "reconnect. Looks like this connection must have been "
                "discarded at some point along the way."
            )

        self.activated[QtCore.QModelIndex].connect(self._on_select)

        # now clear the model
        self._clear_model()

        # clear thumbnail map
        self._thumb_map = {}

        # kick off async data request from shotgun
        # we request to run an arbitrary method in the worker thread
        # this  _do_sg_global_search method will be called by the worker
        # thread when the worker queue reaches that point and will
        # call out to execute it. The data dictionary specified will
        # be forwarded to the method.
        if self._sg_data_retriever:
            # clear download queue and do the new search
            self._sg_data_retriever.clear()
            self._processing_id = self._launch_sg_search(text)
        else:
            raise sgtk.TankError(
                "Please associate this class with a background task manager.")

    def get_current_result(self):
        """
        Returns the result from the current item in the completer popup or ``None``
        if there is no current item.

        :returns: The entity dict for the current result
        :rtype: :obj:`dict`: or ``None``
        """
        model_index = self.popup().currentIndex()
        return self.get_result(model_index)

    def get_first_result(self):
        """
        Returns the first result from the current item in the completer popup
        or ``None`` if there are no results.

        :returns: The entity dict for the first result
        :rtype: :obj:`dict`: or ``None``
        """
        result = None
        model_index = self.popup().model().index(0, 0)
        if model_index.isValid():
            result = self.get_result(model_index)
        return result

    def set_bg_task_manager(self, task_manager):
        """
        Specify the background task manager to use to pull
        data in the background. Data calls
        to Shotgun will be dispatched via this object.

        :param task_manager: Background task manager to use
        :type  task_manager: :class:`~tk-framework-shotgunutils:task_manager.BackgroundTaskManager`
        """
        self._sg_data_retriever = shotgun_data.ShotgunDataRetriever(
            self, bg_task_manager=task_manager)

        self._sg_data_retriever.start()
        self._sg_data_retriever.work_completed.connect(self.__on_worker_signal)
        self._sg_data_retriever.work_failure.connect(self.__on_worker_failure)

    ############################################################################
    # internal methods

    def _clear_model(self, add_loading_item=True, add_more_text_item=False):
        """
        Clears the current data in the model.

        :param add_loading_item: if true, a "loading please wait" item will
            be added.
        :param add_more_text_item: if true, a "type at least 3 characers..."
            item will be added.
        """
        # clear model
        self.model().clear()

        if add_loading_item:
            item = QtGui.QStandardItem("Loading search results...")
            item.setData(self.MODE_LOADING, self.MODE_ROLE)
            self.model().appendRow(item)
            item.setIcon(QtGui.QIcon(self._pixmaps.loading))
        if add_more_text_item:
            item = QtGui.QStandardItem("Type at least %s characters..." % (
                self.COMPLETE_MINIMUM_CHARACTERS,)
            )
            item.setData(self.MODE_NOT_ENOUGH_TEXT, self.MODE_ROLE)
            item.setIcon(QtGui.QIcon(self._pixmaps.keyboard))
            self.model().appendRow(item)

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
            item = self._thumb_map[uid]["item"]
            if thumbnail:
                thumb = QtGui.QPixmap.fromImage(thumbnail)
                item.setIcon(create_rectangular_thumbnail(thumb))
            else:
                # probably won't hit here, but just in case, use default/empty
                # thumbnail
                item.setIcon(self._pixmaps.no_thumbnail)

        if self._processing_id == uid:
            # all done!
            self._clear_model(add_loading_item=False)
            self._handle_search_results(data)

    ############################################################################
    # Abstract methods

    def _set_item_delegate(self, popup, text):
        """
        Sets the item delegate for the pop-up associated with the completer.

        Derived classes are expected to provide a :class:`~PySide.QtGui.QAbstractItemDelegate` derived
        object in this method.

        :param popup: Popup instance from the completer.
        :type popup: :class:`~PySide.QtGui.QAbstractItemView`

        :param str text: Text used for completion.
        """
        raise NotImplementedError

    def _launch_sg_search(self, text):
        """
        Launches a search on the Shotgun server.

        Is is expected that the search is launched using the
        :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever` and than the job
        id is returned to the called.

        :param str text: Text to search for.

        :returns: The :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever`'s job id.
        """
        raise NotImplementedError

    def _handle_search_result(self, data):
        """
        Populates the model associated with the completer with the data coming back from Shotgun.

        :param dict data: Data received back from the job sent to the
            :class:`~tk-framework-shotgunutils:shotgun_data.ShotgunDataRetriever` in :method:``_launch_sg_search``.
        """
        raise NotImplementedError

    def _on_select(self, model_index):
        """
        Fires when an item in the completer is selected.

        :param model_index: Index describing the current item
        :type model_index: :class:`~PySide.QtCore.QModelIndex`
        """
        raise NotImplementedError

    def get_result(self, model_index):
        """
        Returns an item from the list of results.

        This method will be called by :method:``get_current_result`` and :method:``get_first_result``

        :param model_index: The index of the model to return the result for.
        :type model_index: :class:`~PySide.QtCore.QModelIndex`

        :return: The dict for the supplied model index.
        :rtype: :obj:`dict`: or ``None``
        """
        raise NotImplementedError
