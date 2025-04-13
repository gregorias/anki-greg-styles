from typing import List

from gregstyles.assets.model import ModelModifier, StringTransformer

__all__ = 'FakeModelModifier'


class FakeModelModifier(ModelModifier):
    """A fake model modifier for testing purposes."""

    def __init__(self) -> None:
        self.templates: List[str] = []
        self.styles: List[str] = []

    def modify_templates(self, f: StringTransformer) -> None:
        for i, tmpl in enumerate(self.templates):
            self.templates[i] = f(tmpl)

    def modify_styles(self, f: StringTransformer) -> None:
        for i, style in enumerate(self.styles):
            self.styles[i] = f(style)

    def add_template(self, tmpl: str) -> None:
        """Adds a template to the fake modifier."""
        self.templates.append(tmpl)

    def add_style(self, css: str) -> None:
        """Adds a style to the fake modifier."""
        self.styles.append(css)
