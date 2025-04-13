"""This module manages the add-on’s assets."""
import os.path
import pathlib
import re
from typing import Callable, List, Optional, Protocol

from anki.collection import Collection
from anki.media import MediaManager

from .guard import (
    append_guarded_snippet,
    delete_guarded_snippet,
    guard_css_comments,
    guard_html_comments,
)
from .model import ModelModifier

__all__ = [
    'sync_assets',
    'AssetManager',
    'AnkiAssetManager',
    'ModelModifier',
    'AnkiModelModifier',
    'read_asset_version',
]

# TODO: Move this constants up the stack.
GUARD = 'Anki Greg Styles'
PLUGIN_CLASS_NAME = 'greg-styles'
ASSET_PREFIX = f'_{PLUGIN_CLASS_NAME}-'
ASSET_VERSION_FILE_NAME = f'{ASSET_PREFIX}asset-version.txt'

StringTransformer = Callable[[str], str]


class AssetManager(Protocol):
    """An object that can install/delete an add-on’s assets."""

    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


class AnkiAssetManager:

    def __init__(self, models: ModelModifier, col: Collection,
                 external_css: List[str], internal_css: str):
        self.models = models
        self.col = col
        self.external_css: List[str] = external_css
        self.internal_css: str = internal_css

    def install_assets(self) -> None:
        install_media_assets(self.col)
        configure_cards(self.models,
                        external_css=self.external_css,
                        internal_css=self.internal_css)

    def delete_assets(self) -> None:
        clear_cards(self.models)
        # TODO: Just pass the media manager.
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


# TODO: Test the relative path.
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


def delete_media_assets(media: MediaManager) -> None:
    # TODO: Add a commit check for assets having a specific prefix.
    my_assets = list_my_assets(anki_media_directory(media))
    media.trash_files(my_assets)


def configure_cards(models: ModelModifier, external_css: List[str],
                    internal_css: str) -> None:

    if len(external_css) > 0:
        models.modify_templates(lambda tmpl: append_import_statements(
            external_css, [], GUARD, PLUGIN_CLASS_NAME, tmpl))

    if len(internal_css) > 0:

        def modify_styles(tmpl):
            return append_guarded_snippet(tmpl, internal_css,
                                          guard_css_comments(GUARD))

        models.modify_styles(modify_styles)


def clear_cards(models: ModelModifier) -> None:

    def delete_old_import_statements(tmpl):
        return re.sub(f'^<[^>]*class="{PLUGIN_CLASS_NAME}"[^>]*>[^\n]*\n',
                      "",
                      tmpl,
                      flags=re.MULTILINE)

    models.modify_templates(
        lambda tmpl: delete_import_statements(GUARD, PLUGIN_CLASS_NAME, tmpl))

    # TODO: Delete this backward-compatible clearing of the import statements
    # once the new add-on has been out for a while.
    models.modify_templates(lambda tmpl: delete_old_import_statements(tmpl))

    models.modify_styles(
        lambda tmpl: delete_guarded_snippet(tmpl, guard_css_comments(GUARD)))


# Code related to guarding.


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
    guards = guard_html_comments(guard)
    return append_guarded_snippet(tmpl, IMPORT_STATEMENTS, guards)


def delete_import_statements(guard: str, class_name: str, tmpl: str) -> str:
    """
    Deletes import statements from a card template.

    :param guard str A guard string used for HTML comments wrapping the imports.
    :param class_name str A class name that identifies this add-on.
    :param tmpl str
    :rtype str: A template with deleted import statements.
    """
    return delete_guarded_snippet(tmpl, guard_html_comments(guard))


def sync_assets(has_newer_version: Callable[[], bool],
                asset_manager: AssetManager) -> None:
    """Checks if assets need updating and updates them."""
    if not has_newer_version():
        return None
    asset_manager.delete_assets()
    asset_manager.install_assets()
