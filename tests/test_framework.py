# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from tank_test.tank_test_base import TankTestBase
from tank_test.tank_test_base import setUpModule

import sgtk


class TestFramework(TankTestBase):
    def setUp(self):
        super(TestFramework, self).setUp()
        self.setup_fixtures()

    def test_import_framework(self):
        context = sgtk.Context(self.tk)
        engine = sgtk.platform.start_engine("tk-testengine", self.tk, context)
        fw = engine.apps["tk-testapp"].execute_hook_method(
            "load_framework", "load_widgets_framework"
        )
        fw.import_module("activity_stream")
        engine.destroy()
