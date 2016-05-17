# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtGui


class ShotgunMenuBase(QtGui.QMenu):
    """
    A base class with support for easily adding labels and groups of actions
    with a consistent styling.
    """

    def add_group(self, items, title=None, separator=True):
        """
        Adds a group of items to the menu.

        The list of items can include :class:`~PySide.QtGui.QAction` or
        :class:`~PySide.QtGui.QMenu` instances. If a ``title`` is supplied,
        a non-clickable label will be added with the supplied text at the top
        of the list of items in the menu. By default, a separator will be added
        above the group unless ``False`` is supplied for the optional ``separator``
        argument. A separator will not be included if the group is added to an
        empty menu.

        :param list items: A list of actions and/or menus to add to this menu
        :param str title: Optional text to use in a label at the top of the group
        :param bool separator: Add a separator if ``True`` (default), don't add if ``False``

        :returns: A list of all added actions including separator, label and menu
            actions if appropriate.
        :rtype: :obj:`list`
        """

        added_actions = []

        if not self.isEmpty() and separator:
            added_actions.append(self.addSeparator())

        if title:
            added_actions.append(self.add_label(title))

        for item in items:
            if isinstance(item, QtGui.QMenu):
                added_actions.append(self.addMenu(item))
            else:
                self.addAction(item)
                added_actions.append(item)

        return added_actions

    def add_label(self, title):
        """
        Add a label with the given title to the menu

        :param str title: The title of the sectional label
        """
        # build the label widget
        label = QtGui.QLabel(self)
        label.setStyleSheet("margin: 0.4em; color: gray;")
        font_style = "text-transform: uppercase;"
        label.setText("<font style='%s'>%s</font>" % (font_style, title))

        # turn it into an action
        action = QtGui.QWidgetAction(self)
        action.setDefaultWidget(label)

        self.addAction(action)
        return action
