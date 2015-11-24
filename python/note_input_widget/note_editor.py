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
from sgtk import TankError 
 

shotgun_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

 
class NoteEditor(QtGui.QTextEdit):
    """
    A Shotgun note creation/reply editor with user and group auto
    completion.
    """
        
    # internal role constant defining where the auto completer
    # stores shotgun data
    _SG_DATA_ROLE = QtCore.Qt.UserRole + 1
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """         
        QtGui.QTextEdit.__init__(self, parent)
        
        # set up some handy references
        self._bundle = sgtk.platform.current_bundle()      
        
        # the currently processing async autocompleting lookup
        self._processing_id = None
        
        # list of users that have been pushed through via auto completion
        self._users_selected = []
        
        # have a sg data handler for submission
        self.__sg_data_retriever = None
        
        # configure our popup completer
        self._completer = QtGui.QCompleter(self)
        self._completer.setMaxVisibleItems(10)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self._completer.setWidget(self)

        # configure popup data source
        self._model = QtGui.QStandardItemModel(self) 
        self._clear_model()    
        self._completer.setModel(self._model)        

        self._completer.activated[QtCore.QModelIndex].connect(self._insert_completion)

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
        Should be called before the reply widget is closed
        """
        if self.__sg_data_retriever:
            self.__sg_data_retriever.stop()
            self.__sg_data_retriever.work_completed.disconnect(self.__on_worker_signal)
            self.__sg_data_retriever.work_failure.disconnect(self.__on_worker_failure)
            self.__sg_data_retriever = None
        
        
    ##########################################################################################
    # public interface
    
    def clear(self):
        """
        Clear editor state
        """
        self.setPlainText("")
        self._users_selected = []

    def get_recipient_links(self):
        """
        Returns the linked items user has typed in via auto completer.
        
        :returns: list of shotgun link dictionaries with name, type and id
        """
        # first get the *html* contents of the editor
        html_content = self.toHtml()
        
        links = []
        
        for sg_data in self._users_selected:
            # get the unique html id that is used in the html
            # to identify this link
            unique_id = self._create_sg_markup_id(sg_data)
            
            # now see if we can find this in the content. If not, then
            # that means that the user has deleted that reference.
            if unique_id in html_content:
                # link is still there!
                links.append( {"id": sg_data["id"],
                               "type": sg_data["type"],
                               "name": sg_data["name"]} )
                
        return links

    ##########################################################################################
    # overridden event handlers
                
    def focusInEvent(self, event):
        """
        Event that fires when the widget receives focus.
        """
        # "remind" the completer what widget it operates on
        # apparently this is needed - see 
        # http://doc.qt.io/qt-4.8/qt-tools-customcompleter-example.html
        self._completer.setWidget(self)
        # run base class
        QtGui.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        """
        Overridden keypress.
        
        Watches for @xyz style strings and pops up the auto completer 
        in those cases. 
        """
        if self._completer.popup().isVisible():
            # completer is active, so swallow all navigation key
            # strokes sent to the text editor. This is so we don't move
            # away from the object that is currently being worked on. 
            if event.key() in (QtCore.Qt.Key_Enter, 
                               QtCore.Qt.Key_Return,
                               QtCore.Qt.Key_Escape,
                               QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        # let the text edit implementation do its thing
        QtGui.QTextEdit.keyPressEvent(self, event)

        # figure out the current word
        current_word = self._text_under_cursor()
        
        # see if it is something we should care about
        if current_word.startswith("@") and len(current_word) > 3:
            
            # kick off auto completer!
            
            # remove the @ from the input and tell
            # the completer about the search phrase
            login_to_search_for = current_word[1:] 
            self._completer.setCompletionPrefix(login_to_search_for)
                        
            # now clear the model that holds the matches
            # this will also add a "now loading" placeholder item 
            self._clear_model()
    
            # clear async download queue
            if self.__sg_data_retriever:
                self.__sg_data_retriever.clear()
            
            # kick off async data request from shotgun
            # we request to run an arbitrary method in the worker thread
            # this  _do_sg_global_search method will be called by the worker 
            # thread when the worker queue reaches that point and will 
            # call out to execute it. The data dictionary specified will
            # be forwarded to the method.
            data = {"text": login_to_search_for}
            if self.__sg_data_retriever:
                self._processing_id = self.__sg_data_retriever.execute_method(self._do_sg_global_search, data)
            else:
                raise TankError("Please associate this class with a background task processor.")       
            
            # finally, show the completer and make it appear right next to 
            # where the cursor is located.
            cr = self.cursorRect()
            cr.setWidth(self._completer.popup().sizeHintForColumn(0) +
                        self._completer.popup().verticalScrollBar().sizeHint().width())
            self._completer.complete(cr)

        else:
            # we are not in completion mode
            # make sure completer is hidden
            self._completer.popup().hide()


    ##########################################################################################
    # internal methods


    def _clear_model(self, add_loading_item = True):
        """
        Clears the current data in the model.
        
        :param add_loading_item: if true, a "loading please wait" item will
                                 be added.
        """
        # clear model
        self._model.clear()
        
        if add_loading_item:
            item = QtGui.QStandardItem("Hold on, loading...")
            item.setData(None, self._SG_DATA_ROLE)
            self._model.appendRow(item)

    def _text_under_cursor(self):
        """
        Helper methods. Returns the text currently under the cursor.
        Space and \n are considered whitespace. Example:
        
        Hello @john doe! 
                ^ <---- cursor

        @john doe is my friend! 
        ^ <---- cursor

        The above examples would all return '@john'
        
        :returns: string - see above for examples
        """
        cursor_pos = self.textCursor().position()
        full_text = self.toPlainText()
        
        # extend selection forwards and backwards until we find whitespace
        start_idx = cursor_pos-1
        end_idx = cursor_pos-1
        if end_idx < 0:
            # special case for the first character
            end_idx = 0

        # go backwards to find start pos
        while start_idx >= 0 and full_text[start_idx] not in (" ", "\n"):
            start_idx = start_idx - 1
            
        # go forwards to find end pos. This is relevant if the cursor is 
        # not positioned at the end of the line
        while end_idx < len(full_text) and full_text[end_idx] not in (" ", "\n"):
            end_idx += 1
            
        current_word = full_text[start_idx+1:end_idx]
        return current_word


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
        entity_types = {}
        entity_types["HumanUser"] = [["sg_status_list", "is", "act"]]
        entity_types["Group"] = []
        sg_data = sg.text_search(data["text"], entity_types)
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

        if self._processing_id == uid:
            # all done!
            self._clear_model(add_loading_item=False)
            
            matches = data["return_value"]["matches"] 
            
            if len(matches) == 0:
                item = QtGui.QStandardItem("No matches found!")
                item.setData(None, self._SG_DATA_ROLE)
                self._model.appendRow(item)
                
            # insert new data into model
            for d in matches:
                item = QtGui.QStandardItem(d["name"])
                item.setData(shotgun_model.sanitize_for_qt_model(d), 
                             self._SG_DATA_ROLE)
                self._model.appendRow(item)

    def _create_sg_markup_id(self, sg_data):
        """
        Given a Shotgun data chunk returned from the searcher,
        generate a unique id that can be used in the QT html markup
        
        :returns: string representing a sg object
        """ 
        return "NOTE_REF_%s_%s" % (sg_data["type"], sg_data["id"]) 

    def _insert_completion(self, model_index):
        """
        Executed when the user selects one of the items 
        in the completer.
        
        :param model_index: Model index describing the selected completer item
        """
        # get the payload
        data = shotgun_model.get_sanitized_data(model_index, self._SG_DATA_ROLE)

        # make sure that the user selected an actual shotgun item.
        # if they just selected the "no items found" or "loading please hold"
        # items, just ignore it.
        if data is None:
            return

        # Example of data stored in the data role:
        #
        # {'status': 'vwd', 
        #  'name': 'bunny_010_0050_comp_v001', 
        #  'links': ['Shot', 'bunny_010_0050'], 
        #  'image': 'https://xxx', 
        #  'project_id': 65, 
        #  'type': 'Version', 
        #  'id': 99}
        
        # add it to our internal object tracking        
        self._users_selected.append(data)
        
        # now replace the @foobar string that user has typed
        # with the actual match. Color it blue and put it 
        # inside a span so we can track it later.
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.StartOfWord)
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
        tc.movePosition(QtGui.QTextCursor.EndOfWord, QtGui.QTextCursor.KeepAnchor)        
        tc.removeSelectedText()
        # note - we leave a space after the object so that QT understands that
        # when the user starts typing next, it will be a new object that 
        # will reside outside our span in the richtext structure.
        tc.insertHtml("<span id='%s' "
                      "style='color: %s'>%s</span> " % (self._create_sg_markup_id(data), 
                                                        self._bundle.style_constants["SG_HIGHLIGHT_COLOR"],
                                                        data["name"]))
