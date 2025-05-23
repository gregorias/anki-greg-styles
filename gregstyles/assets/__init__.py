"""This module manages an add-on’s assets."""
import os.path
import pathlib
from typing import Callable, List, Optional, Protocol

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
    'read_asset_version',
]


class AssetManager(Protocol):
    """An object that can install/delete an add-on’s assets."""

    # TODO: Use `sync` semantics instead. It’s safer and more inline
    # with intended use.
    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


class AnkiAssetManager:

    def __init__(self, models: ModelModifier, media: MediaManager,
                 external_css: List[str], internal_css: str, guard: str,
                 plugin_assets: pathlib.Path, asset_prefix: str) -> None:
        self.models = models
        self.media = media
        self.external_css: List[str] = external_css
        self.internal_css: str = internal_css
        self.guard: str = guard
        self.plugin_assets = plugin_assets
        self.asset_prefix = asset_prefix

    def install_assets(self) -> None:
        install_media_assets(self.media,
                             plugin_assets=self.plugin_assets,
                             asset_prefix=self.asset_prefix)
        configure_cards(self.models,
                        external_css=self.external_css,
                        internal_css=self.internal_css,
                        guard=self.guard)

    def delete_assets(self) -> None:
        clear_cards(self.models, guard=self.guard)
        delete_media_assets(self.media, asset_prefix=self.asset_prefix)


def has_newer_version(media: MediaManager, plugin_assets: pathlib.Path,
                      asset_version_file_name: str) -> bool:
    """Checks if the add-on has a newer asset version than the one in the media.

    Args:
        media: Anki’s media manager.

    Returns:
        bool: True if the add-on has a newer asset version, False otherwise.
    """
    new_version = read_asset_version(plugin_assets / asset_version_file_name)
    old_version = read_asset_version(
        anki_media_directory(media) / asset_version_file_name)
    if new_version is None:
        return False
    elif old_version is None or new_version > old_version:
        return True
    else:
        return False


def read_asset_version(asset_version: pathlib.Path) -> Optional[int]:
    """Reads the integer representing the asset version from the file."""
    try:
        with open(asset_version, 'r') as f:
            return int(f.read())
    except Exception:
        return None


def anki_media_directory(media: MediaManager) -> pathlib.Path:
    return pathlib.Path(media.dir())


def list_my_assets(dir: pathlib.Path, asset_prefix: str) -> List[str]:
    return [f for f in os.listdir(dir) if f.startswith(asset_prefix)]


def install_media_assets(media: MediaManager, plugin_assets: pathlib.Path,
                         asset_prefix) -> None:
    my_assets = list_my_assets(plugin_assets, asset_prefix)
    for asset in my_assets:
        media.add_file(str(plugin_assets / asset))


def delete_media_assets(media: MediaManager, asset_prefix) -> None:
    my_assets = list_my_assets(anki_media_directory(media), asset_prefix)
    media.trash_files(my_assets)


def configure_cards(models: ModelModifier, external_css: List[str],
                    internal_css: str, guard: str) -> None:

    if len(external_css) > 0:
        models.modify_templates(lambda tmpl: append_import_statements(
            external_css, [], guard, tmpl))

    if len(internal_css) > 0:

        def modify_styles(tmpl):
            return append_guarded_snippet(tmpl, internal_css,
                                          guard_css_comments(guard))

        models.modify_styles(modify_styles)


def clear_cards(models: ModelModifier, guard: str) -> None:
    models.modify_templates(lambda tmpl: delete_import_statements(guard, tmpl))
    models.modify_styles(
        lambda tmpl: delete_guarded_snippet(tmpl, guard_css_comments(guard)))


# Code related to guarding.


def append_import_statements(css_assets: List[str], js_assets: List[str],
                             guard: str, tmpl: str) -> str:
    """
    Appends import statements to a card template.

    :param css_assets List[str]
    :param js_assets List[str]
    :param guard str A guard string used for HTML comments wrapping the imports.
    :param tmpl str The template to modify.
    :rtype str: A template with added import statements.
    """
    IMPORT_STATEMENTS = (''.join([
        f'<link rel="stylesheet" href="{css_asset}">\n'
        for css_asset in css_assets
    ] + [f'<script src="{js_asset}"></script>\n' for js_asset in js_assets]))
    guards = guard_html_comments(guard)
    return append_guarded_snippet(tmpl, IMPORT_STATEMENTS, guards)


def delete_import_statements(guard: str, tmpl: str) -> str:
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
