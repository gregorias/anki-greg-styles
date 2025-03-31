"""The implementation of the greg styles plugin."""
from typing import Callable

from aqt import gui_hooks, mw
from aqt.utils import showWarning

from .assets import AnkiAssetManager, sync_assets

NEW_ISSUES_LINK = "https://github.com/gregorias/anki-greg-styles/issues/new."


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


def load_mw_and_sync():
    main_window = mw
    if not main_window:
        showWarning("Greg styles plugin tried to initialize but couldn't " +
                    "find the main window.")
        return None
    anki_asset_manager = AnkiAssetManager(modify_templates, main_window.col)
    sync_assets(anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
