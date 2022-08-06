# -*- coding: utf-8 -*-
"""This module manages the plugin's web assets."""
import os.path
import pathlib
import re
from typing import Callable, List, Optional, Protocol, Union

from anki.collection import Collection
from aqt import mw  # type: ignore

__all__ = [
    'sync_assets', 'AssetManager', 'AnkiAssetManager', 'read_asset_version'
]

PLUGIN_CLASS_NAME = 'greg-styles'
ASSET_PREFIX = f'_{PLUGIN_CLASS_NAME}-'
ASSET_VERSION_FILE_NAME = f'{ASSET_PREFIX}asset-version.txt'
IMPORT_STATEMENTS = (f'<link rel="stylesheet" href="{ASSET_PREFIX}main.css" ' +
                     f'class="{PLUGIN_CLASS_NAME}">\n')


class AssetManager(Protocol):

    def has_newer_version(self) -> bool:
        return False

    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


class AnkiAssetManager:

    def __init__(self, modify_templates: Callable[[Callable[[str], str]],
                                                  None], col: Collection):
        self.modify_templates = modify_templates
        self.col = col

    def has_newer_version(self) -> bool:
        new_version = read_asset_version(plugin_assets_directory() /
                                         ASSET_VERSION_FILE_NAME)
        old_version = read_asset_version(
            anki_media_directory(self.col) / ASSET_VERSION_FILE_NAME)
        if new_version is None:
            return False
        elif old_version is None or new_version > old_version:
            return True
        else:
            return False

    def install_assets(self) -> None:
        install_media_assets(self.col)
        configure_cards(self.modify_templates)

    def delete_assets(self) -> None:
        clear_cards(self.modify_templates)
        delete_media_assets(self.col)


addon_path = os.path.dirname(os.path.dirname(__file__))


def read_asset_version(asset_version: pathlib.Path) -> Optional[int]:
    """Reads the integer representing the asset version from the file."""
    try:
        with open(asset_version, 'r') as f:
            return int(f.read())
    except:
        return None


def plugin_assets_directory() -> pathlib.Path:
    return pathlib.Path(addon_path) / 'assets'


def anki_media_directory(col: Collection) -> pathlib.Path:
    return pathlib.Path(col.media.dir())


def list_my_assets(dir: pathlib.Path) -> List[str]:
    return [f for f in os.listdir(dir) if f.startswith(ASSET_PREFIX)]


def install_media_assets(col: Collection) -> None:
    plugin_assets_dir = plugin_assets_directory()
    my_assets = list_my_assets(plugin_assets_dir)
    for asset in my_assets:
        col.media.add_file(str(plugin_assets_dir / asset))


def delete_media_assets(col: Collection) -> None:
    my_assets = list_my_assets(anki_media_directory(col))
    col.media.trash_files(my_assets)


def configure_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    def append_import_statements(tmpl):
        return tmpl + '\n' + IMPORT_STATEMENTS

    modify_templates(append_import_statements)


def clear_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    def delete_import_statements(tmpl):
        return re.sub(f'^<[^>]*class="{PLUGIN_CLASS_NAME}"[^>]*>[^\n]*\n',
                      "",
                      tmpl,
                      flags=re.MULTILINE)

    modify_templates(lambda tmpl: delete_import_statements(tmpl).strip())


def sync_assets(asset_manager: AssetManager) -> None:
    """Checks if assets need updating and updates them."""
    if not asset_manager.has_newer_version():
        return None
    asset_manager.delete_assets()
    asset_manager.install_assets()
