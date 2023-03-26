import * as Plot from "@observablehq/plot"
import parse_spec from "./parsing"

export function render(view) {
    let spec = () => view.model.get("spec");
    view.el.appendChild(generate_plot(spec()));
    view.model.on('change:spec', () => _onValueChanged(view, view.el));
}

function generate_plot(spec) {
    let plot = document.createElement("div");
    plot.classList.add("pyobsplot-plot");
    let out
    try {
        out = parse_spec(spec);
        if (spec["pyobsplot-type"] == "function") {
            if (!(out instanceof Element)) {
                out = out.plot()
            }
        } else {
            out = Plot.plot(out)
        }
    } catch (error) {
        out = document.createElement("pre")
        out.classList.add("pyobsplot-error")
        out.textContent = error
    }
    plot.appendChild(out)
    return plot
}

function _onValueChanged(view, el) {
    let plot = el.querySelector(".pyobsplot-plot")
    el.removeChild(plot)
    let spec = () => view.model.get("spec");
    el.appendChild(generate_plot(spec()));
}

