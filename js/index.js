import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import * as arrow from "apache-arrow"
//document.body.append(Plot.plot(options));


export function render(view) {
    let spec = () => view.model.get("s");
    view.el.appendChild(generate_plot(spec()));
    view.model.on('change:s', () => _onValueChanged(view, view.el));
}

function parse_spec(spec) {
    if (spec === null) {
        return null
    }
    if (Array.isArray(spec)) {
        return spec.map(d => parse_spec(d))
    }
    if (spec["ipyobsplot-type"] == "DataFrame") {
        return arrow.tableFromIPC(spec["value"])
    }
    if (typeof spec === 'string' || spec instanceof String) {
        return spec
    }
    if (Object.entries(spec).length == 0) {
        return spec
    }
    if (spec["ipyobsplot-type"] == "function") {
        let fun;
        switch (spec["module"]) {
            case "Plot":
                fun = Plot[spec["method"]]
                break;
            case "d3":
                fun = d3[spec["method"]]
                break;
            default:
                console.error("Invalid module : ", spec["module"])
        }
        return fun.call(null, ...parse_spec(spec["args"]));
    }
    let ret = {}
    for (const [key, value] of Object.entries(spec)) {
        ret[key] = parse_spec(value)
    }
    return ret
}

function generate_plot(spec) {
    let plot = document.createElement("div");
    plot.classList.add("ipyobsplot-plot");
    let svg = parse_spec(spec)
    if (!(svg instanceof Element)) {
        svg = svg.plot()
    }
    plot.appendChild(svg)
    return plot
}

function _onValueChanged(view, el) {
    let plot = el.querySelector(".ipyobsplot-plot")
    el.removeChild(plot)
    let spec = () => view.model.get("s");
    el.appendChild(generate_plot(spec()));

}

