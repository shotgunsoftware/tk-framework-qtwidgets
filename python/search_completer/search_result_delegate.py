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

# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


views = sgtk.platform.current_bundle().import_module("views")

from .search_result_widget import SearchResultWidget
from .utils import CompleterPixmaps


class SearchResultDelegate(views.WidgetDelegate):
    """
    Delegate which renders search match entries in the global
    search completer.
    """

    def __init__(self, view, text=None):
        """
        :param view: The view where this delegate is being used
        """
        super(SearchResultDelegate, self).__init__(view)

        self._pixmaps = CompleterPixmaps()
        self._text = text

        self.selection_model = view.selectionModel()

        if self.selection_model:
            self.selection_model.selectionChanged.connect(self._on_selection_changed)

        self.__current_index = None

    def _on_selection_changed(self, selected, deselected):
        """
        Signal triggered when someone changes the selection in the view.

        :param selected:    A list of the indexes in the model that were selected
        :type selected:     :class:`~PySide.QtGui.QItemSelection`
        :param deselected:  A list of the indexes in the model that were deselected
        :type deselected:  :class:`~PySide.QtGui.QItemSelection`
        """
        # clean up
        selected_indexes = selected.indexes()

        if len(selected_indexes) > 0:
            # get the currently selected model index
            model_index = selected_indexes[0]
            self.__current_index = model_index

    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.

        :param parent: Parent object for the widget
        """
        return SearchResultWidget(parent)

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Called by the base class when the associated widget should be
        painted in the view. This method should implement setting of all
        static elements (labels, pixmaps etc) but not dynamic ones (e.g. buttons)

        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """
        # note: local import to avoid cyclic dependencies
        from .search_completer import SearchCompleter

        widget.set_selected(model_index == self.__current_index)

        mode = shotgun_model.get_sanitized_data(model_index, SearchCompleter.MODE_ROLE)

        if mode == SearchCompleter.MODE_LOADING:
            widget.set_text("Hold on, loading search results...")
            widget.set_thumbnail(self._pixmaps.loading)

        elif mode == SearchCompleter.MODE_NOT_ENOUGH_TEXT:
            widget.set_text("Type at least %s characters..." % (
                SearchCompleter.COMPLETE_MINIMUM_CHARACTERS,))
            widget.set_thumbnail(self._pixmaps.keyboard)

        elif mode == SearchCompleter.MODE_NOT_FOUND:
            widget.set_text("Sorry, no matches found!")
            widget.set_thumbnail(self._pixmaps.no_matches)

        elif mode == SearchCompleter.MODE_RESULT:
            self._render_result(widget, model_index)
        else:
            widget.set_text("Unknown mode!")

    def _underline_search_term(self, matching):
        """
        Generates a text string with the searched text underlined.

        :param str matching: String that potentially matched the search term.

        :returns: The exact same string with the search term underlined. If the search term
            was not present, the string is returned as is.
        """
        # Previous version of the API didn't take a text string in. If we don't have one,
        # we can't highlight
        if not self._text:
            return matching

        match_start = matching.lower().find(self._text.lower())
        if match_start == -1:
            return matching

        match_end = match_start + len(self._text)

        return "%s<span style='text-decoration:underline;'>%s</span>%s" % (
            matching[: match_start], matching[match_start: match_end], matching[match_end:]
        )

    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.

        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        return SearchResultWidget.calculate_size()
