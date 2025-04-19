import os
import unittest

from gregstyles.main import addon_path


class MainTestCase(unittest.TestCase):

    def test_addon_path_root_python_package(self):
        self.assertEqual('gregstyles', os.path.basename(addon_path))
