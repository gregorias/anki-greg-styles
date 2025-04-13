"""This module handles Anki models."""
from typing import Callable, Protocol

from anki.collection import ModelManager

StringTransformer = Callable[[str], str]


class ModelModifier(Protocol):
    """The streamlined interface for Anki models (card types)."""

    def modify_templates(self, f: StringTransformer) -> None:
        pass

    def modify_styles(self, f: StringTransformer) -> None:
        pass


class AnkiModelModifier(ModelModifier):

    def __init__(self, model_manager: ModelManager):
        self.model_manager: ModelManager = model_manager

    def modify_templates(self, f: StringTransformer) -> None:
        for model in self.model_manager.all():
            for tmpl in model['tmpls']:
                tmpl['afmt'] = f(tmpl['afmt'])
                tmpl['qfmt'] = f(tmpl['qfmt'])
            self.model_manager.save(model)

    def modify_styles(self, f: StringTransformer) -> None:
        for model in self.model_manager.all():
            model['css'] = f(model['css'])
            self.model_manager.save(model)
