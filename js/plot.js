/* Plot generation function */

import * as Plot from "@observablehq/plot"
import { parse_spec, unserialize_data } from "./parsing.js"

// Generate plot from a specification
export function generate_plot(spec, renderer) {
    // Add container div
    let out
    try {
        // Parse specification
        spec["data"] = unserialize_data(spec["data"], renderer)
        out = parse_spec(spec["code"], spec["data"]);
        if (spec["code"]["pyobsplot-type"] == "function") {
            if (!(out instanceof Node)) {
                // If spec root is a JS function and the result is not
                // an Element, call plot() on it.
                // This is to handle the specifications with mark function call.
                out = out.plot()
            }
        } else {
            out = Plot.plot(out)
        }
    } catch (error) {
        // If an error occured, display it as output
        out = document.createElement("pre")
        out.classList.add("pyobsplot-error")
        out.textContent = error
    }
    return out
}
