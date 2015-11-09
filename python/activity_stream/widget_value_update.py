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

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.value_update_widget import Ui_ValueUpdateWidget

from .data_manager import ActivityStreamDataHandler

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

from . import utils

class ValueUpdateWidget(ActivityStreamBaseWidget):
    """
    Activity stream widget that displays a value update indication. 
    """
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """

        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_ValueUpdateWidget() 
        self.ui.setupUi(self)
        
        # make sure clicks propagate upwards in the hierarchy
        self.ui.footer.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)
        self.ui.user_thumb.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))

    ##############################################################################
    # public interface        

    def set_info(self, data):
        """
        Populate text fields for this widget
        
        Example of data chunk:
        
            {'created_at': 1437322671.0,
             'created_by': {'id': 38,
                            'image': '',
                            'name': 'Manne Ohrstrom',
                            'status': 'act',
                            'type': 'HumanUser'},
             'id': 112,
             'meta': {'attribute_name': 'sg_status_list',
                      'entity_id': 769,
                      'entity_type': 'Asset',
                      'field_data_type': 'status_list',
                      'new_value': 'ip',
                      'old_value': 'fin',
                      'type': 'attribute_change'},
             'primary_entity': {'id': 769,
                                'image': '',
                                'name': 'Alice',
                                'status': 'hld',
                                'type': 'Asset'},
             'read': False,
             'update_type': 'update'}
        
        :param data: data dictionary with activity stream info. 
        """
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        # make the user icon clickable
        self.ui.user_thumb.set_shotgun_data(data["created_by"])
        
        # set standard date and header fields
        self._set_timestamp(data, self.ui.date)
        
        entity_url = self._generate_entity_url(data["primary_entity"])
        
        if data["meta"]["type"] == "attribute_change":

            field_name = data["meta"]["attribute_name"]
            entity_type = data["meta"]["entity_type"]
            
            # Values can change in different ways
            # for simple data types, values are just set
            # for lists, values are added or removed 
            new_value = data["meta"].get("new_value")
            added = data["meta"].get("added") or []
            removed = data["meta"].get("removed") or []

            # set the first line with summary
            field_display_name = shotgun_globals.get_field_display_name(entity_type, field_name)
            full_str = "<b>%s</b> changed on %s" % (field_display_name, entity_url)
            
            # set the second line with details around the update
            if new_value:
                # a simple data type value was updated
                if field_name == "sg_status_list":
                    new_value = shotgun_globals.get_status_display_name(new_value)

                self.ui.footer.setText("New <b>%s</b>: %s" % (field_display_name, new_value))
            
            if len(added) > 0 or len(removed) > 0:
                
                text = ""
                
                if len(added) > 0:
                    text += "Added %s" % ", ".join([self._generate_entity_url(e, display_type=False) for e in added])
                
                if len(removed) > 0:
                    text += "Removed %s" % ", ".join([self._generate_entity_url(e, display_type=False) for e in removed])
                
                self.ui.footer.setText(text)
            
        else:
            # something changed, not clear what :)
            full_str = "%s was updated" % entity_url 
        
        self.ui.header_left.setText(full_str)
        
    def apply_thumbnail(self, data):
        """
        Populate the UI with the given thumbnail
        
        :param image: QImage with thumbnail data
        :param thumbnail_type: thumbnail enum constant:
            ActivityStreamDataHandler.THUMBNAIL_CREATED_BY
            ActivityStreamDataHandler.THUMBNAIL_ENTITY
            ActivityStreamDataHandler.THUMBNAIL_ATTACHMENT
        """        
        activity_id = data["activity_id"]
        
        if activity_id != self.activity_id:
            return
        
        thumbnail_type = data["thumbnail_type"]
        image = data["image"]
                
        if thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_CREATED_BY:
            thumb = utils.create_round_thumbnail(image)          
            self.ui.user_thumb.setPixmap(thumb)
        
