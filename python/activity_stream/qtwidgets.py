# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Wrapper for the various widgets used from frameworks so that they can be used
easily from with Qt Designer
"""

import sgtk

note_input_widget = sgtk.platform.current_bundle().import_module("note_input_widget")
NoteInputWidget = note_input_widget.NoteInputWidget

playback_label = sgtk.platform.current_bundle().import_module("playback_label")
ShotgunPlaybackLabel = playback_label.ShotgunPlaybackLabel
