/* Widget rendering */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import { generate_plot } from "pyobsplot"

// Make Plot and d3 available in js()
window.d3 = d3
window.Plot = Plot

// Main render function
function render({ model, el, signal }) {
    // Get spec and theme values and generate plot
    let spec = () => model.get("spec")
    // Add container div
    let plot_div = document.createElement("div")
    plot_div.classList.add("pyobsplot-plot")
    plot_div.classList.add(spec()["theme"])
    let plot = generate_plot(spec(), "widget")

    // Listen to pointer events and update pointer_value
    // and pointer_rowindex traitlets
    plot.addEventListener("input", (event) => {
        let value = plot.value ?? {}
        let rowIndex = value[Symbol.for("rowIndex")] ?? -1
        model.set("pointer_value", value)
        model.set("pointer_rowindex", rowIndex)
        model.save_changes()
    })

    plot_div.appendChild(plot)
    el.appendChild(plot_div)
    // Add spec change callback
    model.on("change:spec", () => _onSpecValueChanged(model, el))
}

// specification value change callback
function _onSpecValueChanged(model, el) {
    // Remove current plot
    let plot = el.querySelector(".pyobsplot-plot")
    plot.replaceChildren()
    // Regenerate it
    let spec = () => model.get("spec")
    plot.appendChild(generate_plot(spec(), "widget"))
}

export default { render }
