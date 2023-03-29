/* Main widget */

import * as Plot from "@observablehq/plot"
import { parse_spec, unserialize_data } from "./parsing"

// Main render function
export function render(view) {
    // Get spec value and generate plot
    let spec = () => view.model.get("spec");
    view.el.appendChild(generate_plot(spec()));
    // Add spec change callback
    view.model.on('change:spec', () => _onValueChanged(view, view.el));
}

// Generate plot from a specification
function generate_plot(spec) {
    // Add container div
    let plot = document.createElement("div");
    plot.classList.add("pyobsplot-plot");
    let out
    try {
        // Parse specification
        spec["data"] = unserialize_data(spec["data"])
        out = parse_spec(spec["code"], spec["data"]);
        console.log(out)
        if (spec["code"]["pyobsplot-type"] == "function") {
            if (!(out instanceof Element)) {
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
    plot.appendChild(out)
    return plot
}


// specification value change callback
function _onValueChanged(view, el) {
    // Remove current plot
    let plot = el.querySelector(".pyobsplot-plot")
    el.removeChild(plot)
    // Regenerate it
    let spec = () => view.model.get("spec");
    el.appendChild(generate_plot(spec()));
}

