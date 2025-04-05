"""This module manages the add-on’s assets."""
import os.path
import pathlib
import re
from typing import Callable, List, Optional, Protocol, Tuple

from anki.collection import Collection
from anki.media import MediaManager

__all__ = [
    'sync_assets', 'AssetManager', 'AnkiAssetManager', 'read_asset_version'
]

GUARD = 'Anki Greg Styles'
PLUGIN_CLASS_NAME = 'greg-styles'
ASSET_PREFIX = f'_{PLUGIN_CLASS_NAME}-'
ASSET_VERSION_FILE_NAME = f'{ASSET_PREFIX}asset-version.txt'


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
        delete_media_assets(self.col.media)


def has_newer_version(media: MediaManager) -> bool:
    """Checks if the add-on has a newer asset version than the one in the media.

    Args:
        media: Anki’s media manager.

    Returns:
        bool: True if the add-on has a newer asset version, False otherwise.
    """
    plugin_asset_version_path = (plugin_assets_directory() /
                                 ASSET_VERSION_FILE_NAME)
    new_version = read_asset_version(plugin_asset_version_path)
    old_version = read_asset_version(
        anki_media_directory(media) / ASSET_VERSION_FILE_NAME)
    if new_version is None:
        return False
    elif old_version is None or new_version > old_version:
        return True
    else:
        return False


addon_path = os.path.dirname(__file__)


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


def delete_media_assets(media: MediaManager) -> None:
    # TODO: Add a commit check for assets having a specific prefix.
    my_assets = list_my_assets(anki_media_directory(media))
    media.trash_files(my_assets)


def configure_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    modify_templates(lambda tmpl: append_import_statements(
        [ASSET_PREFIX + 'main.css'], [], GUARD, PLUGIN_CLASS_NAME, tmpl))


def clear_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    def delete_old_import_statements(tmpl):
        return re.sub(f'^<[^>]*class="{PLUGIN_CLASS_NAME}"[^>]*>[^\n]*\n',
                      "",
                      tmpl,
                      flags=re.MULTILINE)

    modify_templates(
        lambda tmpl: delete_import_statements(GUARD, PLUGIN_CLASS_NAME, tmpl))

    # TODO: Delete this backward-compatible clearing of the import statements
    # once the new add-on has been out for a while.
    modify_templates(lambda tmpl: delete_old_import_statements(tmpl))


def guards(guard: str) -> Tuple[str, str]:
    """
    Creates HTML comments bracketing import statements.

    :param guard str A guard string used for HTML comments wrapping the imports.
    :rtype Tuple[str, str]
    """
    return (f'<!-- {guard} BEGIN -->\n', f'<!-- {guard} END -->\n')


def append_import_statements(css_assets: List[str], js_assets: List[str],
                             guard: str, class_name: str, tmpl: str) -> str:
    """
    Appends import statements to a card template.

    :param css_assets List[str]
    :param js_assets List[str]
    :param guard str A guard string used for HTML comments wrapping the imports.
    :param class_name str A class name that identifies this add-on.
    :param tmpl str The template to modify.
    :rtype str: A template with added import statements.
    """
    IMPORT_STATEMENTS = (''.join([
        f'<link rel="stylesheet" href="{css_asset}" class="{class_name}">\n'
        for css_asset in css_assets
    ] + [
        f'<script src="{js_asset}" class="{class_name}"></script>\n'
        for js_asset in js_assets
    ]))

    GUARD_BEGIN, GUARD_END = guards(guard)

    gap = '\n' if tmpl.endswith('\n') else '\n\n'

    return tmpl + gap + GUARD_BEGIN + IMPORT_STATEMENTS + GUARD_END


def delete_import_statements(guard: str, class_name: str, tmpl: str) -> str:
    """
    Deletes import statements from a card template.

    :param guard str A guard string used for HTML comments wrapping the imports.
    :param class_name str A class name that identifies this add-on.
    :param tmpl str
    :rtype str: A template with deleted import statements.
    """
    GUARD_BEGIN, GUARD_END = guards(guard)
    return re.sub(f'(\n)*{re.escape(GUARD_BEGIN)}.*{re.escape(GUARD_END)}',
                  '\n',
                  tmpl,
                  flags=re.MULTILINE | re.DOTALL)


def sync_assets(has_newer_version: Callable[[], bool],
                asset_manager: AssetManager) -> None:
    """Checks if assets need updating and updates them."""
    if not has_newer_version():
        return None
    asset_manager.delete_assets()
    asset_manager.install_assets()
