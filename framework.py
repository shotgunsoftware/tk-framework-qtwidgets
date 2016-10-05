# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

class QtWidgetFramework(sgtk.platform.Framework):
    
    ##########################################################################################
    # init and destroy
            
    def init_framework(self):
        self.log_debug("%s: Initializing..." % self)
    
    def destroy_framework(self):
        self.log_debug("%s: Destroying..." % self)

    ##########################################################################################
    # public methods

    def get_hyperlink_html(self, url, name):
        """
        Provides an html string for a hyperlink pointing to the given URL
        and displaying the provided string name.

        :param str url: The URL that the hyperlink navigates to.
        :param str name: The string name to display.

        :return: HTML string.
        """
        # Older versions of core don't have the SG_LINK_COLOR constant, so we'll
        # just fall back on SG_FOREGROUND_COLOR in that case.
        color = self.style_constants.get(
            "SG_LINK_COLOR",
            self.style_constants["SG_FOREGROUND_COLOR"]
        )

        html = "<a href='%s' style='text-decoration: none; color: %s'><b>%s</b></a>" % (
            url,
            color,
            name,
        )

        return html
    
    
