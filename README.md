# ipyobsplot


## Bundling

```shell
# Once
./esbuild --format=esm --bundle --outdir=static js/* 
# Watching
./esbuild --format=esm --bundle --outdir=static js/* --watch
```

## TODO

- anonymous functions in specs
- move pandas, polars and others to optional dependencies

## Quarto

For plots to be computed and displayed when compiling from an `ipynb` file, you have to add `--execute` :

```shell
quarto render test.ipynb --execute --to html
```