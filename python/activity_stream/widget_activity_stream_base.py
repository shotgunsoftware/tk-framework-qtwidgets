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

shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


class ActivityStreamBaseWidget(QtGui.QWidget):
    """
    Base class for all activity stream widget types
    """

    entity_requested = QtCore.Signal(str, int)
    
    playback_requested = QtCore.Signal(dict)
    
    def __init__(self, parent):
        """
        :param parent: QT parent object
        :type parent: :class:`PySide.QtGui.QWidget`
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)
        self._entity_type = None
        self._entity_id = None
        self._target_entity_type = None
        self._target_entity_id = None
        self._bundle = sgtk.platform.current_bundle()

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
        
    def apply_thumbnail(self, data):
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
            self._bundle.log_warning("Could not parse url '%s'" % url)

        
    def _set_timestamp(self, data, label):
        """
        Set a standard time stamp in the given label 
        """
        # it seems some of the activity stream methods return null
        # time stamps in some cases so make sure those are handled
        # gracefully rather than assuming created_at always exists
        created_at_unixtime = data.get("created_at") or 0
        datetime_obj = datetime.datetime.fromtimestamp(created_at_unixtime)
        
        # standard format 
        full_time_str = datetime_obj.strftime('%a %d %b %Y %H:%M') 

        time_now_obj = datetime.datetime.now()
        # The note created time is rounded up to the nearest second by Shotgun,
        # so handle creation time greater than now.
        if datetime_obj > time_now_obj:
            datetime_obj = time_now_obj

        # get the delta and components
        delta = time_now_obj - datetime_obj

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

        time_str = self._pretty_date(datetime_obj)

        # set the tooltip to be the full time stamp
        # so that if a user hovers over, they get full
        # details.        
        label.setText(time_str)
        label.setToolTip(full_time_str)
    

    def _pretty_date(self, time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        from datetime import datetime
        now = datetime.now()
        if type(time) is int:
            diff = now - datetime.fromtimestamp(time)
        elif isinstance(time,datetime):
            diff = now - time
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff / 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff / 7) + " weeks ago"
        if day_diff < 365:
            if day_diff / 30 == 1:
                return "1 month ago" 
            return str(day_diff / 30) + " months ago"
        return str(day_diff / 365) + " years ago"
                     
    def __generate_url(self, entity_type, entity_id, name):
        """
        Generate a standard shotgun url
        """
        utils = self._bundle.import_module("utils")
        return utils.get_hyperlink_html(
            url="%s:%s" % (entity_type, entity_id),
            name=name,
        )
    
    def _generate_entity_url(self, entity, this_syntax=True, display_type=True):
        """
        Generate a standard created by url string given activity data.
        
        :param data: activity stream data chunk
        :returns: string with url
        """
        
        entity_type_display_name = shotgun_globals.get_type_display_name(entity["type"])
        
        if entity["type"] == self._entity_type and entity["id"] == self._entity_id and this_syntax:
            # special case - we are looking at "this" entity
            return "this %s" % entity_type_display_name

        if display_type:
            name = "%s %s" % (entity_type_display_name, entity["name"])
        else:
            name = entity["name"]

        return self.__generate_url(entity["type"], entity["id"], name)
