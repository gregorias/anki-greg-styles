# Anki Greg Styles

An Anki plugin that manages my card styles.

## For Developers

### Dev Environment Setup

1. Set up Pipenv:

    ```shell
    pipenv install --dev
    ```

1. Set up npm:

    ```shell
    npm install
    ```

1. Install Lefthook:

    ```shell
    lefthook install
    ```

## Release & Installation

1. Create a release commit.
    1. Bump up the package version in `codehighlighter/manifest.json`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
2. Use the `dev/bin/package` tool to create `codehighlighter.ankiaddon`.
3. [Share the package on Anki.](https://addon-docs.ankiweb.net/#/sharing)
