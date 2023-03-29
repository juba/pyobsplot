# pyobsplot

This is a work in progress, not suitable for use right now.

## TODO

- widget tests if possible
- exception not rethrown in pytest
- see why output is lost when notebooks are closed -> VSCode fault, see https://github.com/microsoft/vscode-jupyter/issues/4404. See how pydeck handles this.


## Bundling

```shell
# Once
npm run bundle
# Watching
npm run watch
```

## Tests

Run Python tests:

```shell
npm run pytest
```

Run JavaScript tests:

```shell
npm run jstest
```

For visual regression tests, first install the requirements:

```shell
cd tests/ui
npm install
```

Start a test jupyter instance with:

```shell
npm run uistart
```

And run tests with:

```shell
# Create / update reference snapshots
npm run uitest:update
# Compare with reference snapshots
npm run uitest
```

## Quarto

For plots to be computed and displayed when compiling from an `ipynb` file, you have to add `--execute` :

```shell
quarto render test.ipynb --execute --to html
```