# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

from tank.platform.qt import QtCore, QtGui
from .ui.browser import Ui_Browser
from .worker import Worker

MAX_WIDGETS_TO_DISPLAY = 75


class BrowserWidget(QtGui.QWidget):

    ######################################################################################
    # SIGNALS

    # when the selection changes
    selection_changed = QtCore.Signal()

    # when someone double clicks on an item
    action_requested = QtCore.Signal()

    # called when the list contents have been modified:
    list_modified = QtCore.Signal()

    ######################################################################################
    # Init & Destruct

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # set up the UI
        self.ui = Ui_Browser()
        self.ui.setupUi(self)

        # hide the overlays
        self.ui.main_pages.setCurrentWidget(self.ui.items_page)

        self._app = None
        self._worker = None
        self._current_work_id = None
        self._dynamic_widgets = []
        self._multi_select = False
        self._search = True

        # spinner
        self._spin_icons = []
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/progress_bar_1.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/progress_bar_2.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/progress_bar_3.png")
        )
        self._spin_icons.append(
            QtGui.QPixmap(":/tk_framework_qtwidgets.browser_widget/progress_bar_4.png")
        )
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_spinner)
        self._current_spinner_index = 0

        # search
        self.ui.search.textEdited.connect(self._on_search_box_input)

        # load all items
        self.ui.load_all_top.clicked.connect(self._on_load_all_clicked)
        self.ui.load_all_bottom.clicked.connect(self._on_load_all_clicked)
        # reset the deferred loading counters and settings
        self._reset_load_more()

        # style:
        self._title_base_style = {
            "border": "none",
            "border-color": "rgb(32,32,32)",
            "border-top-left-radius": "3px",
            "border-top-right-radius": "3px",
            "border-bottom-left-radius": "0px",
            "border-bottom-right-radius": "0px",
        }
        self._title_styles = {
            "gradient": {
                "background": "qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(97, 97, 97, 255), stop:1 rgba(49, 49, 49, 255));"
            },
            "none": {},
        }
        self._title_margins = {"gradient": [12, 3, 12, 3], "none": [3, 3, 3, 3]}

        self._current_title_style = "none"
        self.title_style = "gradient"

    def _reset_load_more(self):
        """
        set the load more buttons to a disabled state
        """
        self._num_visible_widgets = 0
        self._show_all_mode_enabled = False
        self.ui.load_all_top.setVisible(False)
        self.ui.load_all_bottom.setVisible(False)

    def _compute_load_button_visible(self, total_num_widgets):
        """
        Enable/disable the "load more" buttons based on the number of items loaded.
        """
        if (
            self._num_visible_widgets > MAX_WIDGETS_TO_DISPLAY
            and not self._show_all_mode_enabled
        ):
            msg = "Showing %d of %d items. Click to show all." % (
                MAX_WIDGETS_TO_DISPLAY,
                total_num_widgets,
            )
            self.ui.load_all_top.setText(msg)
            self.ui.load_all_bottom.setText(msg)
            self.ui.load_all_top.setVisible(True)
            self.ui.load_all_bottom.setVisible(True)

        else:
            self.ui.load_all_top.setVisible(False)
            self.ui.load_all_bottom.setVisible(False)

    # @property
    def _get_title_style(self):
        """
        title_style property getter
        """
        return self._current_title_style

    # @title.setter
    def _set_title_style(self, value):
        """
        title_style property setter
        """
        if value != self._current_title_style and value in self._title_styles.keys():
            # change style sheet:
            self._current_title_style = value
            style = self._title_base_style.copy()
            style.update(self._title_styles[self._current_title_style])
            ss = self._style_as_string("#browser_header", style)
            self.ui.browser_header.setStyleSheet(ss)

            # change margins:
            margins = self._title_margins.get(self._current_title_style)
            if margins:
                self.ui.browser_header.layout().setContentsMargins(
                    margins[0], margins[1], margins[2], margins[3]
                )

    title_style = property(_get_title_style, _set_title_style)

    def enable_multi_select(self, enable):
        """
        Should we enable multi select
        """
        self._multi_select = enable

    def enable_search(self, status):
        """
        Toggle the search bar (on by default)
        """
        self.ui.search.setVisible(status)

    def destroy(self):
        if self._worker:
            self._worker.stop()

    def set_app(self, app):
        """
        associate with an app object
        """
        self._app = app
        # set up worker queue
        self._worker = Worker(app)
        self._worker.notifier.work_completed.connect(self._on_worker_signal)
        self._worker.notifier.work_failure.connect(self._on_worker_failure)

        self._worker.start()

    def set_label(self, label):
        """
        Sets the text next to the search button
        """
        self.ui.label.setText("<big>%s</big>" % label)

    ######################################################################################
    # Public Methods

    def load(self, data):
        """
        Loads data into the browser widget.
        Called by outside code
        """
        # start spinning
        self.ui.main_pages.setCurrentWidget(self.ui.loading_page)
        self._timer.start(100)
        # queue up work
        self._current_work_id = self._worker.queue_work(self.get_data, data, asap=True)

        self.list_modified.emit()

    def clear(self):
        """
        Clear widget of its contents.
        """

        # reset load more buttons..
        self._reset_load_more()

        # clear search box
        # commented out as of #23302 take 2
        # the search field will not be cleared as the widget is cleared.
        # self.ui.search.setText("")

        # hide overlays
        self.ui.main_pages.setCurrentWidget(self.ui.items_page)

        # also reset any jobs that are processing. No point processing them
        # if their requestors are gone.
        if self._worker:
            self._worker.clear()

        for x in self._dynamic_widgets:
            # remove widget from layout:
            self.ui.scroll_area_layout.removeWidget(x)
            # set it's parent to None so that it is removed from the widget hierarchy
            x.setParent(None)
            # mark it to be deleted when event processing returns to the main loop
            x.deleteLater()
        self._dynamic_widgets = []

        self.list_modified.emit()

    def set_message(self, message):
        """
        Replace the list of items with a single message
        """
        self.ui.main_pages.setCurrentWidget(self.ui.status_page)
        self.ui.status_message.setText(message)

    def clear_selection(self):
        """
        Clears the selection
        """
        for x in self._dynamic_widgets:
            x.set_selected(False)

    def get_selected_item(self):
        """
        Gets the last selected item, None if no selection
        """
        for widget in self._dynamic_widgets:
            if widget.is_selected():
                return widget
        return None

    def get_selected_items(self):
        """
        Returns entire selection
        """
        selected_items = []
        for widget in self._dynamic_widgets:
            if widget.is_selected():
                selected_items.append(widget)
        return selected_items

    def get_items(self):
        return self._dynamic_widgets

    def select(self, item):
        """
        Select an item and ensure it is visible
        """
        self._on_item_clicked(item)
        self._ensure_item_is_visible(item)

    ##########################################################################################
    # Protected stuff - implemented by deriving classes

    def get_data(self, data):
        """
        Needs to be implemented by subclasses
        """
        raise Exception("not implemented!")

    def process_result(self, result):
        """
        Needs to be implemented by subclasses
        """
        raise Exception("not implemented!")

    ##########################################################################################
    # Internals

    def _style_as_string(self, name, style_dict):
        style_elements = ["%s: %s;" % (key, value) for key, value in style_dict.items()]
        return "%s { %s }" % (name, "".join(style_elements))

    def _on_search_box_input(self):
        """
        When text is typed into the search box
        """
        # first make sure that we reset the load more buttons, since the search is changing
        self._show_all_mode_enabled = False
        # now update our list
        self._update_items_based_on_search_box()

    def _update_items_based_on_search_box(self):
        """
        Cull items displayed in list based on search box
        """
        from . import list_item

        # if we are currently on the items listing page
        # (and not on a message page)
        # start the spinner and turn it off after load
        if self.ui.main_pages.currentWidget() == self.ui.items_page:
            running_spinner = True
        else:
            running_spinner = False

        if running_spinner:
            self.ui.main_pages.setCurrentWidget(self.ui.loading_page)
            self._timer.start(100)

        # track how many widgets we could display if culling was off
        total_num_widgets = 0
        self._num_visible_widgets = 0

        # get the text in the search bar
        text = self.ui.search.text()

        if text == "":
            # show all items
            for i in self._dynamic_widgets:
                total_num_widgets += 1
                if (
                    isinstance(i, list_item.ListItem)
                    and self._show_all_mode_enabled == False
                    and self._num_visible_widgets > MAX_WIDGETS_TO_DISPLAY
                ):
                    i.setVisible(False)
                    i.setEnabled(False)

                else:
                    self._num_visible_widgets += 1
                    i.setVisible(True)
                    i.setEnabled(True)

        elif len(text) > 2:  # cull by string for strings > 2 chars

            # if running PyQt, convert QString to str
            if not isinstance(text, str):
                # convert QString to str
                text = str(text)

            # now we have a str or unicode object which has the lower() method
            lower_text = text.lower()

            for i in self._dynamic_widgets:

                details = i.get_details()

                # if running PyQt, convert QString to str
                details_lower = details
                if not isinstance(details_lower, str):
                    details_lower = str(details_lower)
                # now we have a str or unicode object which has the lower() method
                details_lower = details_lower.lower()

                if details is None:  # header
                    i.setVisible(True)

                elif lower_text in details_lower:
                    # match!
                    total_num_widgets += 1
                    if (
                        self._num_visible_widgets > MAX_WIDGETS_TO_DISPLAY
                        and self._show_all_mode_enabled == False
                    ):
                        i.setEnabled(False)
                        i.setVisible(False)
                    else:
                        self._num_visible_widgets += 1
                        i.setVisible(True)
                        i.setEnabled(True)
                else:
                    # no match!
                    i.setVisible(False)
                    i.setEnabled(False)

        # see if we need to turn on the load more buttons
        self._compute_load_button_visible(total_num_widgets)

        # and if there is a selection, try to scroll to it!
        si = self.get_selected_item()
        if si:
            self._ensure_item_is_visible(si)

        # turn off spinner
        if running_spinner:
            self.ui.main_pages.setCurrentWidget(self.ui.items_page)
            self._timer.stop()

    def _on_worker_failure(self, uid, msg):
        """
        The worker couldn't execute stuff
        """
        if self._current_work_id != uid:
            # not our job. ignore
            return

        # finally, turn off progress indication and turn on display
        self.ui.main_pages.setCurrentWidget(self.ui.items_page)
        self._timer.stop()

        # show error message
        self.set_message(msg)

    def _on_worker_signal(self, uid, data):
        """
        Signalled whenever the worker completes something
        """
        if self._current_work_id != uid:
            # not our job. ignore
            return

        # process - this will typically add items using add_item()
        self.process_result(data)

        # if currently showing progress, switch to items page:
        if self.ui.main_pages.currentWidget() == self.ui.loading_page:
            self.ui.main_pages.setCurrentWidget(self.ui.items_page)

        # stop timer:
        self._timer.stop()

        # display items in the UI, based on the search criteria
        self._update_items_based_on_search_box()

        # and just in case the list has been modified
        self.list_modified.emit()

    def _update_spinner(self):
        """
        Animate spinner icon
        """
        self.ui.progress_bar.setPixmap(self._spin_icons[self._current_spinner_index])
        self._current_spinner_index += 1
        if self._current_spinner_index == 4:
            self._current_spinner_index = 0

    def _ensure_item_is_visible(self, item):
        """
        Ensure the item is visible by scrolling to it.
        """
        # make sure it is visible and enabled
        # it may have been turned off by the culling or the searching
        item.setVisible(True)
        item.setEnabled(True)
        # in order for the scroll to happen during load, first give
        # the scroll area  chance to resize it self by processing its event queue.
        QtCore.QCoreApplication.processEvents()
        # and focus on the selection
        self.ui.scroll_area.ensureWidgetVisible(item)

    def _on_load_all_clicked(self):
        """
        Triggered when someone clicks the "show all records" button
        """
        self._show_all_mode_enabled = True
        self._update_items_based_on_search_box()

    def _on_item_clicked(self, item):

        if item.supports_selection() == False:
            # not all items are selectable
            return

        if self._multi_select:
            # invert selection:
            item.set_selected(not item.is_selected())
        else:
            # single select
            self.clear_selection()
            item.set_selected(True)

        self.selection_changed.emit()

    def _on_item_double_clicked(self, item):
        self.action_requested.emit()

    def add_item(self, item_class):
        """
        Adds a list item. Returns the created object.
        """
        widget = item_class(self._app, self._worker, self)
        widget.setVisible(False)
        widget.setEnabled(False)
        self.ui.scroll_area_layout.addWidget(widget)
        self._dynamic_widgets.append(widget)
        widget.clicked.connect(self._on_item_clicked)
        widget.double_clicked.connect(self._on_item_double_clicked)
        self.list_modified.emit()

        return widget
