/* Widget rendering */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import { generate_plot } from "pyobsplot"

// Make Plot and d3 available in js()
window.d3 = d3
window.Plot = Plot


// Main render function
export function render(view) {
    // Get spec value and generate plot
    let spec = () => view.model.get("spec");
    // Add container div
    let plot_div = document.createElement("div");
    plot_div.classList.add("pyobsplot-plot");
    let plot = generate_plot(spec(), "widget")
    plot_div.appendChild(plot);
    view.el.appendChild(plot_div);
    // Add spec change callback
    view.model.on('change:spec', () => _onValueChanged(view, view.el));
}

// specification value change callback
function _onValueChanged(view, el) {
    // Remove current plot
    let plot = el.querySelector(".pyobsplot-plot")
    plot.replaceChildren()
    // Regenerate it
    let spec = () => view.model.get("spec");
    plot.appendChild(generate_plot(spec(), "widget"));
}

