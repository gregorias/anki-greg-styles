"""This package manages the plugin's web assets."""
from .internal import AnkiAssetManager, sync_assets

__all__ = ['sync_assets', 'AnkiAssetManager']
