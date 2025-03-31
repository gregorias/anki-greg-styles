# Anki Greg Styles

An Anki plugin that manages my card styles.

## For developers

### Dev environment setup

#### Prerequisites

This project requires the following tools:

- [Commitlint]
- [Lefthook]
- [Just]
- [Markdownlint]
- [Ruff]

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
[Ruff]: https://github.com/astral-sh/ruff
