import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import * as arrow from "apache-arrow"


export function render(view) {
    let spec = () => view.model.get("spec");
    view.el.appendChild(generate_plot(spec()));
    view.model.on('change:spec', () => _onValueChanged(view, view.el));
}

function get_fun(mod, method) {
    let fun
    switch (mod) {
        case "Plot":
            fun = Plot[method]
            break;
        case "d3":
            fun = d3[method]
            break;
        case "Math":
            fun = Math[method]
            break;
        default:
            throw new Error(`Invalid module: ${mod}`)
    }
    if (fun === undefined) {
        throw new Error(`${mod}.${method} is not defined`)
    }
    return fun
}

function parse_spec(spec) {
    if (spec === null) {
        return null
    }
    if (Array.isArray(spec)) {
        return spec.map(d => parse_spec(d))
    }
    if (typeof spec === 'string' || spec instanceof String) {
        return spec
    }
    if (Object.entries(spec).length == 0) {
        return spec
    }
    if (spec["pyobsplot-type"] == "DataFrame") {
        return arrow.tableFromIPC(spec["value"])
    }
    if (spec["pyobsplot-type"] == "function") {
        let fun = get_fun(spec["module"], spec["method"])
        return fun.call(null, ...parse_spec(spec["args"]));
    }
    if (spec["pyobsplot-type"] == "function-object") {
        return get_fun(spec["module"], spec["method"])
    }
    if (spec["pyobsplot-type"] == "js") {
        // Use indirect eval to avoid bundling issues
        // See https://esbuild.github.io/content-types/#direct-eval
        let indirect_eval = eval
        return indirect_eval(spec["value"])
    }
    if (spec["pyobsplot-type"] == "datetime") {
        return new Date(spec["value"])
    }
    if (spec["pyobsplot-type"] == "GeoJson") {
        return spec["value"]
    }
    let ret = {}
    for (const [key, value] of Object.entries(spec)) {
        ret[key] = parse_spec(value)
    }
    return ret
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

