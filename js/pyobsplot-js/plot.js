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
            // If spec root is a JS function, call plot() on it.
            // This is to handle the specifications with mark function call.
            out = out.plot()
        } else {
            if (spec["debug"]) {
                debug_output(out, renderer)
            }
            out = Plot.plot(out)
        }
    } catch (error) {
        // If an error occured, display it as output
        out = document.createElement("pre")
        out.style.color = "#CC0000"
        out.style.padding = "1em 1.5em"
        out.textContent = "⚠ " + error
    }
    return out
}


// Output plot specification if debug is true
function debug_output(out, renderer) {
    if (renderer == "widget") {
        console.log("--- start pyobsplot debugging output ---")
        console.log(out)
        console.log("--- end pyobsplot debugging output ---")
    }
    if (renderer == "jsdom") {
        console.log("<br>--- start pyobsplot debugging output ---<br>")
        console.log(out)
        console.log("<br>--- end pyobsplot debugging output ---</br>")
    }
}

export { parse_spec, get_fun } from "./parsing.js"