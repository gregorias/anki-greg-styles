"""The implementation of the greg styles add-on."""
import functools
import os
import pathlib
from typing import Callable, List

from aqt import gui_hooks, mw
from aqt.utils import showWarning

from .assets import AnkiAssetManager, has_newer_version, sync_assets
from .assets.model import AnkiModelModifier

NEW_ISSUES_LINK = "https://github.com/gregorias/anki-greg-styles/issues/new."

# The guard used in templates to clearly mark the add-on's code.
GUARD = 'Anki Greg Styles'
PLUGIN_CLASS_NAME = 'greg-styles'
ASSET_PREFIX = f'_{PLUGIN_CLASS_NAME}-'

# TODO: Add a test checking that every asset is accounted for.
ASSET_VERSION_FILE_NAME = f'{ASSET_PREFIX}asset-version.txt'
EXTERNAL_STYLES: List[str] = []
INTERNAL_STYLES = [f'{ASSET_PREFIX}main.css']

addon_path: pathlib.Path = pathlib.Path(os.path.dirname(__file__))


def plugin_assets() -> pathlib.Path:
    return addon_path / 'asset-files'


def read_internal_styles():
    css_snippets = []
    for style in INTERNAL_STYLES:
        with open(plugin_assets() / style, 'r') as f:
            css_snippets.append(f.read())
    return "\n".join(css_snippets)


def modify_templates(modify: Callable[[str], str]) -> None:
    """Modifies all card templates with modify."""
    if not mw:
        showWarning("Greg styles plugin tried to modify card templates " +
                    "but Anki's main window has not loaded up yet.\n" +
                    f"Please report this to the author at {NEW_ISSUES_LINK}.")
        return None
    for model in mw.col.models.all():
        for tmpl in model['tmpls']:
            tmpl['afmt'] = modify(tmpl['afmt'])
            tmpl['qfmt'] = modify(tmpl['qfmt'])
        mw.col.models.save(model)


def load_mw_and_sync() -> None:
    main_window = mw
    if not main_window:
        showWarning("Greg styles plugin tried to initialize but couldn't " +
                    "find the main window.")
        return None

    anki_model_modifier = AnkiModelModifier(mw.col.models)

    anki_asset_manager = AnkiAssetManager(anki_model_modifier,
                                          main_window.col.media,
                                          external_css=EXTERNAL_STYLES,
                                          internal_css=read_internal_styles(),
                                          guard=GUARD,
                                          plugin_assets=plugin_assets(),
                                          asset_prefix=ASSET_PREFIX)
    sync_assets(
        functools.partial(has_newer_version, mw.col.media, plugin_assets(),
                          ASSET_VERSION_FILE_NAME), anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
