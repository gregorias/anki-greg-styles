"""This module manages the add-on’s assets."""
import os.path
import pathlib
import re
from typing import Callable, List, Optional, Protocol

from anki.collection import Collection
from anki.media import MediaManager

__all__ = [
    'sync_assets', 'AssetManager', 'AnkiAssetManager', 'read_asset_version'
]

PLUGIN_CLASS_NAME = 'greg-styles'
ASSET_PREFIX = f'_{PLUGIN_CLASS_NAME}-'
ASSET_VERSION_FILE_NAME = f'{ASSET_PREFIX}asset-version.txt'
IMPORT_STATEMENTS = (f'<link rel="stylesheet" href="{ASSET_PREFIX}main.css" ' +
                     f'class="{PLUGIN_CLASS_NAME}">\n')


class AssetManager(Protocol):
    """An object that can install/delete an add-on’s assets."""

    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


class AnkiAssetManager:

    def __init__(self, modify_templates: Callable[[Callable[[str], str]],
                                                  None], col: Collection):
        self.modify_templates = modify_templates
        self.col = col

    def install_assets(self) -> None:
        install_media_assets(self.col)
        configure_cards(self.modify_templates)

    def delete_assets(self) -> None:
        clear_cards(self.modify_templates)
        delete_media_assets(self.col)


def has_newer_version(media: MediaManager) -> bool:
    """Checks if the add-on has a newer asset version than the one in the media.

    Args:
        media: Anki’s media manager.

    Returns:
        bool: True if the add-on has a newer asset version, False otherwise.
    """
    new_version = read_asset_version(plugin_assets_directory() /
                                     ASSET_VERSION_FILE_NAME)
    old_version = read_asset_version(
        anki_media_directory(media) / ASSET_VERSION_FILE_NAME)
    if new_version is None:
        return False
    elif old_version is None or new_version > old_version:
        return True
    else:
        return False


addon_path = os.path.dirname(os.path.dirname(__file__))


def read_asset_version(asset_version: pathlib.Path) -> Optional[int]:
    """Reads the integer representing the asset version from the file."""
    try:
        with open(asset_version, 'r') as f:
            return int(f.read())
    except Exception:
        return None


def plugin_assets_directory() -> pathlib.Path:
    return pathlib.Path(addon_path) / 'assets'


def anki_media_directory(media: MediaManager) -> pathlib.Path:
    return pathlib.Path(media.dir())


def list_my_assets(dir: pathlib.Path) -> List[str]:
    return [f for f in os.listdir(dir) if f.startswith(ASSET_PREFIX)]


def install_media_assets(col: Collection) -> None:
    plugin_assets_dir = plugin_assets_directory()
    my_assets = list_my_assets(plugin_assets_dir)
    for asset in my_assets:
        col.media.add_file(str(plugin_assets_dir / asset))


def delete_media_assets(col: Collection) -> None:
    my_assets = list_my_assets(anki_media_directory(col.media))
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


def sync_assets(has_newer_version: Callable[[], bool],
                asset_manager: AssetManager) -> None:
    """Checks if assets need updating and updates them."""
    if not has_newer_version():
        return None
    asset_manager.delete_assets()
    asset_manager.install_assets()
