import tempfile
import unittest
from textwrap import dedent

from gregstyles import assets
from gregstyles.assets import append_import_statements, delete_import_statements


class FakeAssetManager:

    def __init__(self, local_version: int, plugin_version: int):
        self.local_version = local_version
        self.plugin_version = plugin_version

    def install_assets(self) -> None:
        self.local_version = self.plugin_version

    def delete_assets(self) -> None:
        self.local_version = 0


class AssetsTestCase(unittest.TestCase):

    def test_sync_assets_syncs_on_version_mismatch(self):
        manager = FakeAssetManager(local_version=1, plugin_version=2)
        assets.sync_assets(lambda: True, manager)
        self.assertEqual(manager.local_version, 2)

    def test_sync_assets_passes_if_newer_version_present(self):
        manager = FakeAssetManager(local_version=2, plugin_version=1)
        assets.sync_assets(lambda: False, manager)
        self.assertEqual(manager.local_version, 2)

    def test_read_asset_version_returns_none_on_nonexistant_file(self):
        self.assertEqual(assets.read_asset_version("./foo/bar"), None)

    def test_read_asset_version_returns_version(self):
        with tempfile.NamedTemporaryFile() as version_f:
            version_f.writelines([b'42'])
            version_f.flush()
            self.assertEqual(assets.read_asset_version(version_f.name), 42)

    def test_configure_and_clear_do_nothing(self):
        tmpl = """{{FrontSide}}
                    <hr id=answer>
                    {{Back}}

                    {{#Notes}}
                    <div id=notes>
                    <h4>Notes</h4>
                    {{Notes}}\n"""
        old_tmpl = tmpl

        def modify_tmpl(modify):
            nonlocal tmpl
            tmpl = modify(tmpl)

        assets.configure_cards(modify_tmpl)
        assets.clear_cards(modify_tmpl)
        self.assertEqual(old_tmpl, tmpl)

    def test_append_and_clear_import_statements_do_nothing(self):
        tmpl = """{{FrontSide}}
                    <hr id=answer>
                    {{Back}}

                    {{#Notes}}
                    <div id=notes>
                    <h4>Notes</h4>
                    {{Notes}}"""

        GUARD = 'PLUGIN (Addon 123)'
        CLASS_NAME = 'anki-ch'

        new_tmpl = append_import_statements(['c.css'], ['j.js'], GUARD,
                                            CLASS_NAME, tmpl)
        self.assertEqual(delete_import_statements(GUARD, CLASS_NAME, new_tmpl),
                         tmpl + '\n')

    def test_append_import_statements_adds_them_with_a_gap(self):
        self.assertEqual(
            append_import_statements(['c.css'], ['j.js'], 'Anki Greg Styles',
                                     'plugin', '{{Cloze}}'),
            dedent('''\
            {{Cloze}}

            <!-- Anki Greg Styles BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Anki Greg Styles END -->
            '''))

    def test_append_import_statements_adds_them_with_a_gap_and_minds_a_newline_in_template(
            self):
        self.assertEqual(
            append_import_statements(['c.css'], ['j.js'], 'Anki Greg Styles',
                                     'plugin', '{{Cloze}}\n'),
            dedent('''\
            {{Cloze}}

            <!-- Anki Greg Styles BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Anki Greg Styles END -->
            '''))

    def test_delete_import_statements_deletes_new_style_imports(self):
        TMPL = dedent('''\
            {{Cloze}}

            <!-- Anki Greg Styles BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Anki Greg Styles END -->
            ''')
        self.assertEqual(
            delete_import_statements('Anki Greg Styles', 'plugin', TMPL),
            '{{Cloze}}\n')

    def test_delete_import_statements_deletes_too_many_newlines(self):
        TMPL = dedent('''\
            {{Cloze}}


            <!-- Anki Greg Styles BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Anki Greg Styles END -->
            ''')
        self.assertEqual(
            delete_import_statements('Anki Greg Styles', 'plugin', TMPL),
            '{{Cloze}}\n')
