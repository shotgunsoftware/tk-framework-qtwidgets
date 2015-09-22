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

import sgtk
import datetime
from ...modules.schema import CachedShotgunSchema

class ActivityStreamBaseWidget(QtGui.QWidget):
    """
    Base class for all activity stream widget types
    """

    # signal that fire when things are clicked
    entity_requested = QtCore.Signal(str, int)
    playback_requested = QtCore.Signal(dict)
    
    def __init__(self, parent):
        """
        Constructor
        
        :param parent: QT parent object
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        self._entity_type = None
        self._entity_id = None
        self._target_entity_type = None
        self._target_entity_id = None
        self._app = sgtk.platform.current_bundle()  
        
    ##############################################################################
    # public interface
        
    def set_host_entity(self, entity_type, entity_id):
        """
        specify the entity in whose stream this 
        widget is appearing.
        """
        self._entity_type = entity_type
        self._entity_id = entity_id    
    
    @property
    def entity_type(self):
        return self._entity_type
    
    @property
    def entity_id(self):
        return self._entity_id
    
    @property
    def activity_id(self):
        return self._activity_id

    def set_info(self, data):
        """
        Populate text fields for this widget
        
        :param data: data dictionary with activity stream info. 
        """
        self._target_entity_type = data["primary_entity"]["type"] 
        self._target_entity_id = data["primary_entity"]["id"]
        self._activity_id = data["id"]
        
    def set_thumbnail(self, data):
        """
        Populate the UI with the given thumbnail
        """
        # each deriving class should implement this
        raise NotImplementedError
    
    ##############################################################################
    # protected methods called by base classes
        
    def mouseDoubleClickEvent(self, event):
        """
        Forward any clicks from this widget
        """
        self.entity_requested.emit(self._target_entity_type, self._target_entity_id)
            
    def _icon_url_for_entity_type(self, entity_type):
        """
        Given an entity type, return a dark 16x16px icon resource url.
        Returns None if no icon exists
        
        :param entity_type: entity type
        :returns: resource url or None
        """
        entity_types_with_icons = ["Asset", 
                                   "ClientUser",
                                   "EventLogEntry",
                                   "Group",
                                   "HumanUser",
                                   "Note",
                                   "Playlist",
                                   "Project",
                                   "Sequence",
                                   "Shot",
                                   "Task",
                                   "Ticket",
                                   "Version",
                                   ]

        if entity_type in entity_types_with_icons:        
            url = ":/tk_multi_infopanel_activity_stream/entity_icons/icon_%s_dark.png" % entity_type
        else:
            url = None
            
        return url            
            
    def _entity_request_from_url(self, url):
        """
        Helper method.
        
        Given a url on the form entity_type:entity_id, 
        emit an entity_requested signal. This is typically
        used by deriving classes to hook up linkActivated
        signals to. 
        """
        try:
            (entity_type, entity_id) = url.split(":")
            entity_id = int(entity_id)
            self.entity_requested.emit(entity_type, entity_id)
        except:
            self._app.log_warning("Could not parse url '%s'" % url)

        
    def _set_timestamp(self, data, label):
        """
        Set a standard time stamp in the given label 
        """
        created_at_unixtime = data["created_at"]
        datetime_obj = datetime.datetime.fromtimestamp(created_at_unixtime)
        
        # standard format 
        full_time_str = datetime_obj.strftime('%a %d %b %Y %H:%M') 
    
        if datetime_obj > datetime.datetime.now():
            # future times are reported precisely
            return (full_time_str, full_time_str) 
        
        # get the delta and components
        delta = datetime.datetime.now() - datetime_obj
    
        # the timedelta structure does not have all units; bigger units are converted
        # into given smaller ones (hours -> seconds, minutes -> seconds, weeks > days, ...)
        # but we need all units:
        delta_weeks        = delta.days // 7
        delta_days         = delta.days
    

        if delta_weeks > 52:
            # more than one year ago - 26 June 2012
            time_str = datetime_obj.strftime('%d %b %Y')
        
        elif delta_days > 5:
            # ~ more than one week ago - 26 June
            time_str = datetime_obj.strftime('%d %b')
    
        elif delta_days > 0:
            # more than one day ago - day of week - e.g. Sunday
            time_str = datetime_obj.strftime('%A')
        
        else:
            # earlier today - display timestamp - 23:22
            time_str = datetime_obj.strftime('%H:%M')
                     
        # set the tooltip to be the full time stamp
        # so that if a user hovers over, they get full
        # details.        
        label.setText(time_str)
        label.setToolTip(full_time_str)
    
    
    def __generate_url(self, entity_type, entity_id, name):
        """
        Generate a standard shotgun url
        """
        str_val = """<a href='%s:%s' 
                        style='text-decoration: none;
                        color: %s'>%s</a>
                  """ % (entity_type, 
                         entity_id,
                         self._app.style_constants["SG_HIGHLIGHT_COLOR"], 
                         name)
        return str_val
    
    def _generate_entity_url(self, entity, this_syntax=True, display_type=True):
        """
        Generate a standard created by url string given activity data.
        
        :param data: activity stream data chunk
        :returns: string with url
        """
        entity_type_display_name = CachedShotgunSchema.get_type_display_name(entity["type"])
        
        if entity["type"] == self._entity_type and entity["id"] == self._entity_id and this_syntax:
            # special case - we are looking at "this" entity
            return "this %s" % entity_type_display_name

        icon = self._icon_url_for_entity_type(entity["type"])

        if display_type:
            name = "%s %s" % (entity_type_display_name, entity["name"])
        else:
            name = entity["name"]

        return self.__generate_url(entity["type"], entity["id"], name)
