# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


from . import shotgun_field_factory as _sff

get_display_class = _sff.ShotgunFieldFactory.get_display_class
get_label = _sff.ShotgunFieldFactory.get_label
