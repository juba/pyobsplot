#!/usr/bin/env node

import * as Plot from "@observablehq/plot";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

// Get current file path
const __filename = fileURLToPath(import.meta.url);
const parentDir = path.dirname(path.dirname(__filename));

async function replaceLines(filePath, newContent) {
    let content = await fs.readFile(filePath, "utf8");
    const regex =
        /(    # STATIC PLOT METHODS START\n)[\s\S]*?(\n    # STATIC PLOT METHODS END\n)/;
    content = content.replace(regex, `$1${newContent}\n$2`);
    await fs.writeFile(filePath, content, "utf8");
}

function python_method(name) {
    return `
    @staticmethod
    def ${name}(*args, **kwargs) -> dict: # noqa: ARG001, ARG004, RUF100
        return method_to_spec("${name}", *args, **kwargs)`;
}

process.stdin.write("Importing methods...\n");

let methods = Object.keys(Plot)
    .filter((d) => d[0] !== d[0].toUpperCase())
    .filter((d) => d != "plot")
    .map(python_method)
    .join("\n");

process.stdin.write("Inserting methods in plot.py...\n");

replaceLines(parentDir + "/src/pyobsplot/plot.py", methods).catch(console.error);

process.stdin.write("Done.");
