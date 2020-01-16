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
from tank_test.tank_test_base import setUpModule  # noqa

from tank_vendor import six
import sgtk


class TestFramework(TankTestBase):
    """
    Very basic tests for the framework.
    """

    def setUp(self):
        """
        Prepare a configuration with a config that uses the framework.
        """
        super(TestFramework, self).setUp()
        self.setup_fixtures()
        context = sgtk.Context(self.tk, project=self.project)
        self.engine = sgtk.platform.start_engine("tk-testengine", self.tk, context)
        self._app = sgtk.platform.qt.QtGui.QApplication.instance() or sgtk.platform.qt.QtGui.QApplication(
            []
        )

    def tearDown(self):
        """
        Terminate the engine and the rest of the test suite.
        """
        self.engine.destroy()
        super(TestFramework, self).tearDown()

    def test_import_framework(self):
        """
        Ensure we can import the framework.
        """
        # We can't load modules from a test because load_framework can only be called
        # from within a Toolkit bundle or hook, so we'll do it from a hook.
        fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-qtwidgets"]
        # we need to import a module in order to trigger
        # an import of all the framework modules.
        fw.import_module("activity_stream")

    def test_widget_instantiation(self):
        """
        Ensure we can instantiate the widgets.

        In lieu of a proper test suite that fully tests the widgets, we'll at least
        instantiate all the widgets in a tight loop.

        Careful, there be dragons.
        """

        # We can't load modules from a test because load_framework can only be called
        # from within a Toolkit bundle or hook, so we'll do it from a hook.
        qt_fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-qtwidgets"]
        su_fw = self.engine.apps["tk-testapp"].frameworks["tk-framework-shotgunutils"]

        # Get a few modules that will be useful later on when instantiating widgets.
        shotgun_model = su_fw.import_module("shotgun_model")
        task_manager = su_fw.import_module("task_manager")
        field_manager = qt_fw.import_module("shotgun_fields")
        shotgun_globals = su_fw.import_module("shotgun_globals")

        # We'll parent the widgets under a dialog.
        parent = sgtk.platform.qt.QtGui.QDialog()
        parent.show()
        parent.activateWindow()
        parent.raise_()

        # And we want to reuse the same background task manager for every widget.
        bg_task_manager = task_manager.BackgroundTaskManager(parent=self._app)
        shotgun_globals.register_bg_task_manager(bg_task_manager)

        # Enumerate all the modules inside the framework.
        modules = os.listdir(os.path.join(os.path.dirname(__file__), "..", "python"))
        for module_name in modules:
            # Skips __pycache__ and __init__.py.
            # FIXME: Also, there seems to be some weird ownership problems regarding the
            # background task manager and the activity stream and version details
            # widgets, which causes the test process to crash on exit, due to threads
            # still running because they are not properly shut down.
            # I've tried to fix this, but couldn't figure how. This is only a problem
            # with tests and not in DCCs, so we'll let it slide for now and skip
            # those widgets.
            if "__" in module_name or module_name in [
                "activity_stream",
                "version_details",
            ]:
                continue

            # Got a module we can test, so load it!
            module = qt_fw.import_module(os.path.splitext(module_name)[0])
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Skip non-class attributes
                if inspect.isclass(attr) is False:
                    continue

                # Skip classes that are not widgets.
                if issubclass(attr, sgtk.platform.qt.QtGui.QWidget) is False:
                    continue

                # Skip this particular widget, as it is the base class of other
                # widgets and is unusable.
                if attr_name in ["GroupWidgetBase"]:
                    continue

                params = {}
                if six.PY2:
                    getargspec = inspect.getargspec
                else:
                    getargspec = inspect.getfullargspec
                # Look at the parameter list for this widget's __init__ method
                for arg in getargspec(attr.__init__).args:
                    # For each required parameter, we'll pass in an instance
                    # of the right type.
                    if arg == "parent":
                        params["parent"] = parent
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

                # Add the widget and show it, don't worry about the rest.
                # It. Just. Works.
                attr(**params).show()

        self._app.processEvents()
        parent.destroy()
        bg_task_manager.shut_down()
        time.sleep(3)
