# -*- coding: utf-8 -*-
"""The implementation of the greg styles plugin."""

from aqt import gui_hooks, mw  # type: ignore
from aqt.utils import showWarning  # type: ignore

from .assets import AnkiAssetManager, sync_assets


def load_mw_and_sync():
    main_window = mw
    if not main_window:
        # For some reason the main window is not initialized yet. Let's print
        # an error message.
        showWarning(
            "Greg styles plugin tried to initialize, " +
            "but couldn't find the main window.\n" +
            "Please report it to the author at " +
            "https://github.com/gregorias/anki-greg-styles/issues/new.")
        return None
    anki_asset_manager = AnkiAssetManager(modify_templates, main_window.col)
    sync_assets(anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
