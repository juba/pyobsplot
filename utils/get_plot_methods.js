#!/usr/bin/env node

import * as Plot from "@observablehq/plot";

let methods = Object.keys(Plot)
    .map((d) => '"' + d + '"')
    .join(", ");
methods = `PLOT_METHODS = (${methods})`;

process.stdin.write(methods);
