# Anki Greg Styles

An Anki plugin that manages my card styles.

## For developers

### Dev environment setup

1. Install the required Python version:

   ```shell
   pyenv install CHECK_PIPFILE
   ```

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

## Release & installation

1. Create a release commit.
    1. Bump up the package version in `gregstyles/manifest.json`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
2. Use the `dev/bin/package` tool to create `gregstyles.ankiaddon`.
3. Install the `ankiaddon` file in Anki.
