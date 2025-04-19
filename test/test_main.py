import os
import unittest
from typing import List

from gregstyles import main
from gregstyles.main import addon_path


def get_files_in_assets() -> List[str]:
    return [f for f in os.listdir('assets')]


class MainTestCase(unittest.TestCase):

    def test_addon_path_root_python_package(self):
        self.assertEqual('gregstyles', os.path.basename(addon_path))

    def test_all_files_in_main_and_assets_are_in_sync(self) -> None:
        files_in_assets: List[str] = get_files_in_assets()

        files_in_main: List[str] = [
            main.ASSET_VERSION_FILE_NAME
        ] + main.EXTERNAL_STYLES + main.INTERNAL_STYLES

        self.assertListEqual(list(sorted(files_in_assets)),
                             list(sorted(files_in_main)))

    def test_all_assets_have_consistent_compatible_prefix(self) -> None:
        for file in get_files_in_assets():
            self.assertTrue(file.startswith('_greg-styles-'),
                            f"Asset {file} does not start with _greg_styles-")
