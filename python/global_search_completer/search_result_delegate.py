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
 
# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


views = sgtk.platform.current_bundle().import_module("views")

from .search_result_widget import SearchResultWidget
from .utils import CompleterPixmaps


class SearchResultDelegate(views.EditSelectedWidgetDelegate):
    """
    Delegate which renders search match entries in the global 
    search completer.
    """

    def __init__(self, view):
        """
        :param view: The view where this delegate is being used
        """                
        views.EditSelectedWidgetDelegate.__init__(self, view)

        self._pixmaps = CompleterPixmaps()

    def _create_widget(self, parent):
        """
        Widget factory as required by base class. The base class will call this
        when a widget is needed and then pass this widget in to the various callbacks.
        
        :param parent: Parent object for the widget
        """
        return SearchResultWidget(parent)
    
    def _on_before_selection(self, widget, model_index, style_options):
        """
        Called when the associated widget is selected. This method 
        implements all the setting up and initialization of the widget
        that needs to take place prior to a user starting to interact with it.
        
        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """
        # do std drawing first
        self._on_before_paint(widget, model_index, style_options)        
        widget.set_selected(True)
    
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
        from .global_search_completer import GlobalSearchCompleter
        
        mode = shotgun_model.get_sanitized_data(model_index, GlobalSearchCompleter.MODE_ROLE)
        
        if mode == GlobalSearchCompleter.MODE_LOADING:
            widget.set_text("Hold on, loading search results...")
            widget.set_thumbnail(self._pixmaps.loading)

        elif mode == GlobalSearchCompleter.MODE_NOT_ENOUGH_TEXT:
            widget.set_text("Type at least %s characters..." % (
                GlobalSearchCompleter.COMPLETE_MINIMUM_CHARACTERS,))
            widget.set_thumbnail(self._pixmaps.keyboard)

        elif mode == GlobalSearchCompleter.MODE_NOT_FOUND:
            widget.set_text("Sorry, no matches found!")
            widget.set_thumbnail(self._pixmaps.no_matches)
            
        elif mode == GlobalSearchCompleter.MODE_RESULT:

            icon = shotgun_model.get_sanitized_data(model_index, QtCore.Qt.DecorationRole)
            if icon:
                thumb = icon.pixmap(512)
                widget.set_thumbnail(thumb)
            else:
                # probably won't hit here, but just in case, use default/empty
                # thumbnail
                widget.set_thumbnail(self._pixmaps.no_thumbnail)

            data = shotgun_model.get_sanitized_data(model_index, GlobalSearchCompleter.SG_DATA_ROLE)
            # Example of data stored in the data role:
            # {'status': 'vwd', 
            #  'name': 'bunny_010_0050_comp_v001', 
            #  'links': ['Shot', 'bunny_010_0050'], 
            #  'image': 'https://xxx', 
            #  'project_id': 65, 
            #  'type': 'Version', 
            #  'id': 99}            

            entity_type_display_name = shotgun_globals.get_type_display_name(data["type"])



            content = ""
            et_url = shotgun_globals.get_entity_type_icon_url(data["type"])
            if et_url:
                # present thumbnail icon and name
                content += "<img src='%s'/>&nbsp;&nbsp;<b style='color: rgb(48, 167, 227)';>%s</b>" % (et_url, data["name"])
            else:
                # present type name name
                content += "%s" % data["name"]  
    
            content += "<br>%s" % entity_type_display_name
    
            links = data["links"]
            # note users return weird data so ignore it.
            if links and links[0] != "" and links[0] != "HumanUser" and links[0] != "ClientUser":
                # there is a referenced entity
                et_url = shotgun_globals.get_entity_type_icon_url(links[0])
                if et_url:
                    # present thumbnail icon and name
                    content += " on <img align=absmiddle src='%s'/>  %s" % (et_url, links[1])
                else:
                    # present type name name
                    link_entity_type = links[0]
                    content += " on %s %s" % (shotgun_globals.get_type_display_name(link_entity_type), links[1])
            
            widget.set_text(content)
        
        else:
            widget.set_text("Unknown mode!")
        
    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.
        
        :param style_options: QT style options
        :param model_index: Model item to operate on
        """
        return SearchResultWidget.calculate_size()
             
