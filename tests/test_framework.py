# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import time
import os
import inspect

from tank_test.tank_test_base import TankTestBase
from tank_test.tank_test_base import setUpModule

import sgtk


class TestFramework(TankTestBase):
    def setUp(self):
        super(TestFramework, self).setUp()
        self.setup_fixtures()
        context = sgtk.Context(self.tk, project=self.project)
        self.engine = sgtk.platform.start_engine("tk-testengine", self.tk, context)
        self._app = sgtk.platform.qt.QtGui.QApplication.instance() or sgtk.platform.qt.QtGui.QApplication(
            []
        )

    def tearDown(self):
        self.engine.destroy()
        super(TestFramework, self).tearDown()

    def test_import_framework(self):
        fw = self.engine.apps["tk-testapp"].execute_hook_method(
            "load_framework",
            "load_widgets_framework",
            name="tk-framework-qtwidgets_v2.x.x",
        )
        # we need to import a module in order to trigger
        # an import of all the framework modules.
        fw.import_module("activity_stream")

    def test_widget_instantiation(self):
        modules = os.listdir(os.path.join(os.path.dirname(__file__), "..", "python"))
        qt_fw = self.engine.apps["tk-testapp"].execute_hook_method(
            "load_framework",
            "load_widgets_framework",
            name="tk-framework-qtwidgets_v2.x.x",
        )
        su_fw = self.engine.apps["tk-testapp"].execute_hook_method(
            "load_framework",
            "load_widgets_framework",
            name="tk-framework-shotgunutils_v5.x.x",
        )
        shotgun_model = su_fw.import_module("shotgun_model")
        task_manager = su_fw.import_module("task_manager")
        field_manager = qt_fw.import_module("shotgun_fields")
        shotgun_globals = su_fw.import_module("shotgun_globals")

        parent = sgtk.platform.qt.QtGui.QDialog()
        bg_task_manager = task_manager.BackgroundTaskManager(parent=self._app)
        shotgun_globals.register_bg_task_manager(bg_task_manager)
        for module_name in modules:
            # Skips __pycache__ and __init__.py.
            # FIXME: There seems to be some weird ownership problems regarding the
            # background task manager and the activity stream and version details
            # widgets, which causes the test process to crash on exit, so we're
            # skipping those two.
            if "__" in module_name or module_name in [
                "activity_stream",
                "version_details",
            ]:
                continue

            module = qt_fw.import_module(os.path.splitext(module_name)[0])
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "focusInEvent") is False:
                    continue
                if attr_name in ["GroupWidgetBase"]:
                    continue

                params = {}
                for arg in inspect.getargspec(attr.__init__).args:
                    if arg == "parent":
                        continue
                    elif arg == "sg_model":
                        params["sg_model"] = shotgun_model.ShotgunModel(
                            parent=self._app, bg_task_manager=bg_task_manager
                        )
                    elif arg == "bg_task_manager":
                        params["bg_task_manager"] = bg_task_manager
                    elif arg == "fields_manager":
                        params["fields_manager"] = field_manager.ShotgunFieldManager(
                            parent=parent, bg_task_manager=bg_task_manager
                        )
                    elif arg == "sg_entity_type":
                        params["sg_entity_type"] = "Asset"

                attr(parent=parent, **params).destroy()

        parent.destroy()
        bg_task_manager.shut_down()
        time.sleep(3)
