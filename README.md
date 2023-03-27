# pyobsplot


## TODO

- move pandas, polars and others to optional dependencies
- widget tests if possible
- exception not rethrown in pytest
- see why output is lost when notebooks are closed -> VSCode fault, see https://github.com/microsoft/vscode-jupyter/issues/4404. See how pydeck handles this.


## Bundling

```shell
# Once
./esbuild --format=esm --bundle --outdir=static js/index.js js/styles.css
# Watching
./esbuild --format=esm --bundle --outdir=static js/index.js js/styles.css --watch
```

## Tests

Run Python tests:

```shell
pdm run pytest
```

Run JavaScript tests:

```shell
npm run test
```

## Quarto

For plots to be computed and displayed when compiling from an `ipynb` file, you have to add `--execute` :

```shell
quarto render test.ipynb --execute --to html
```