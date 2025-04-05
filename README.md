# Anki Greg Styles

Greg Styles is an Anki add-on that manages my card styles.
This add-on works by installing CSS stylesheets and modifying card templates
upon Anki initialization.

## For developers

### Dev environment setup

#### Prerequisites

This project requires the following tools:

- [Commitlint]
- [Lefthook]
- [Just]
- [Markdownlint]
- [Mypy]
- [Ruff]
- [Uv]
- [Yapf]

They are not included in the project’s manifest to minimize the project’s
footprint (specifically, the need to respond to security advisories).

#### Setup

1. Set up a local virtual environment:

   ```shell
   uv venv
   ```

1. Install development dependencies:

    ```shell
    uv pip install --group dev
    ```

1. Install Lefthook:

    ```shell
    lefthook install
    ```

## Release & installation

1. Create a release commit.
    1. Bump up the package version in `gregstyles/manifest.json`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
2. Use the `dev/bin/package` tool to create `gregstyles.ankiaddon`.
3. Install the `ankiaddon` file in Anki.

[Commitlint]: https://github.com/conventional-changelog/commitlint
[Lefthook]: https://github.com/evilmartians/lefthook
[Just]: https://github.com/casey/just
[Markdownlint]: https://github.com/igorshubovych/markdownlint-cli
[Mypy]: https://mypy-lang.org/
[Ruff]: https://github.com/astral-sh/ruff
[Uv]:https://docs.astral.sh/uv/
[Yapf]: https://github.com/google/yapf
