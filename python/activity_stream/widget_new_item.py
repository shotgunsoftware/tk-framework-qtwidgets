# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtCore, QtGui

from .widget_activity_stream_base import ActivityStreamBaseWidget
from .ui.new_item_widget import Ui_NewItemWidget
from .ui.simple_new_item_widget import Ui_SimpleNewItemWidget

from .data_manager import ActivityStreamDataHandler
from . import utils

class NewItemWidget(ActivityStreamBaseWidget):
    """
    Activity stream widget that shows a UI representing a newly
    created object, for example a version or a publish.
    """
    
    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """

        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_NewItemWidget() 
        self.ui.setupUi(self)
        self._interactive = True
        
        # thumbnails are hidden by default, only to appear
        # for created objects that have them set 
        self.ui.details_thumb.setVisible(False)
        
        # make sure that click on hyperlinks bubble up
        self.ui.footer.linkActivated.connect(self._entity_request_from_url)
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)
        self.ui.details_thumb.playback_clicked.connect(
            lambda sg_data: self.playback_requested.emit(sg_data)
        )
        self.ui.user_thumb.entity_requested.connect(
            lambda entity_type, entity_id: self.entity_requested.emit(
                entity_type,
                entity_id,
            )
        )

    ##############################################################################
    # properties

    @property
    def user_thumb(self):
        """
        The user thumbnail widget.
        """
        return self.ui.user_thumb

    def _get_interactive(self):
        """
        Whether the new item label is interactive, showing a play icon.
        """
        return self._interactive

    def _set_interactive(self, state):
        self._interactive = bool(state)
        self.ui.details_thumb.interactive = self._interactive

        if self._interactive:
            self.user_thumb.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.user_thumb.setCursor(QtCore.Qt.ArrowCursor)

    interactive = QtCore.Property(
        bool,
        _get_interactive,
        _set_interactive,
    )
        
    ##############################################################################
    # public interface
        
    def set_info(self, data):
        """
        Populate text fields for this widget.
        
        Example of data:
        
            {'created_at': 1437322777.0,
             'created_by': {'id': 38,
                            'image': '',
                            'name': 'Manne Ohrstrom',
                            'status': 'act',
                            'type': 'HumanUser'},
             'id': 116,
             'meta': {'entity_id': 6007, 'entity_type': 'Version', 'type': 'new_entity'},
             'primary_entity': {'description': 'testing testing\n\n1\n\n2\n\n3',
                                'id': 6007,
                                'image': '',
                                'name': 'note_addressing',
                                'sg_uploaded_movie': {'content_type': 'video/quicktime',
                                                      'id': 180,
                                                      'link_type': 'upload',
                                                      'name': 'note_addressing.mov',
                                                      'type': 'Attachment',
                                                      'url': ''},
                                'status': 'rev',
                                'type': 'Version'},
             'read': False,
             'update_type': 'create'}
        
        
        
        :param data: data dictionary with activity stream info. 
        """
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        # make the user icon clickable
        self.ui.user_thumb.set_shotgun_data(data["created_by"])
        
        # set standard date and header fields
        self._set_timestamp(data, self.ui.date)
        
        primary_entity = data["primary_entity"]
        entity_url = self._generate_entity_url(primary_entity, this_syntax=False)        
        
        header = "%s was created" % entity_url
        
        # add link if there is a link field that is populated
        if "entity" in primary_entity and primary_entity["entity"]:
            link_url = self._generate_entity_url(primary_entity["entity"])
            header += " on %s" % link_url
        
        self.ui.header_left.setText(header)

        # set the footer area to contain the description                
        if primary_entity.get("description"):
            self.ui.footer.setText("%s" % primary_entity.get("description"))
        else:
            # hide footer fields
            self.ui.footer.setVisible(False)

        if primary_entity.get("image"):
            # there is a thumbnail. Show thumbnail.
            self.ui.details_thumb.setVisible(True)
            
        self.ui.details_thumb.set_shotgun_data(primary_entity)
            

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

        elif thumbnail_type == ActivityStreamDataHandler.THUMBNAIL_ENTITY:
            thumb = utils.create_rectangular_256x144_thumbnail(image)
            self.ui.details_thumb.setPixmap(thumb)
        






class SimpleNewItemWidget(ActivityStreamBaseWidget):
    """
    Similar to the NewItemWidget, but a smaller version of it.
    This is used for 'less important' newly created items such
    as tasks. The visual representation is smaller and without
    a thumbnail, with a smaller user icon.
    """
    
    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`        
        """

        # first, call the base class and let it do its thing.
        ActivityStreamBaseWidget.__init__(self, parent)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_SimpleNewItemWidget() 
        self.ui.setupUi(self)
        
        # make sure that click on hyperlinks bubble up
        self.ui.header_left.linkActivated.connect(self._entity_request_from_url)        
        self.ui.user_thumb.entity_requested.connect(lambda entity_type, entity_id: self.entity_requested.emit(entity_type, entity_id))
        
    ##############################################################################
    # public interface
        
    def set_info(self, data):
        """
        Populate text fields for this widget.
        
        Example of data:
        
            {'created_at': 1437322777.0,
             'created_by': {'id': 38,
                            'image': '',
                            'name': 'Manne Ohrstrom',
                            'status': 'act',
                            'type': 'HumanUser'},
             'id': 116,
             'meta': {'entity_id': 6007, 'entity_type': 'Version', 'type': 'new_entity'},
             'primary_entity': {'description': 'testing testing\n\n1\n\n2\n\n3',
                                'id': 6007,
                                'image': '',
                                'name': 'note_addressing',
                                'sg_uploaded_movie': {'content_type': 'video/quicktime',
                                                      'id': 180,
                                                      'link_type': 'upload',
                                                      'name': 'note_addressing.mov',
                                                      'type': 'Attachment',
                                                      'url': ''},
                                'status': 'rev',
                                'type': 'Version'},
             'read': False,
             'update_type': 'create'}
        
        
        
        :param data: data dictionary with activity stream info. 
        """
        # call base class
        ActivityStreamBaseWidget.set_info(self, data)
        
        # make the user icon clickable
        self.ui.user_thumb.set_shotgun_data(data["created_by"])
        
        # set standard date and header fields
        self._set_timestamp(data, self.ui.date)
        
        primary_entity = data["primary_entity"]
        entity_url = self._generate_entity_url(primary_entity, this_syntax=False)        
        
        header = "%s was created" % entity_url
        
        # add link if there is a link field that is populated
        if "entity" in primary_entity and primary_entity["entity"]:
            link_url = self._generate_entity_url(primary_entity["entity"])
            header += " on %s" % link_url
        
        self.ui.header_left.setText(header)
            

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
        
