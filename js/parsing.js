/* Plot specification parsing */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import * as arrow from "apache-arrow"

// Main function : recursively parse a JSON specification 
export function parse_spec(spec) {
    // If null, return null
    if (spec === null) {
        return null
    }
    // If Array, recursively parse elements
    if (Array.isArray(spec)) {
        return spec.map(d => parse_spec(d))
    }
    // If a string, returns as is
    if (typeof spec === 'string' || spec instanceof String) {
        return spec
    }
    // If not dict-like, returns as is
    if (Object.entries(spec).length == 0) {
        return spec
    }
    // If DataFrame type, deserialize from Arrow IPC
    if (spec["pyobsplot-type"] == "DataFrame") {
        return arrow.tableFromIPC(spec["value"])
    }
    // If a JS function with arguments type, get function from name and call it
    if (spec["pyobsplot-type"] == "function") {
        let fun = get_fun(spec["module"], spec["method"])
        return fun.call(null, ...parse_spec(spec["args"]));
    }
    // If a JS function object type, get function from name and call it
    if (spec["pyobsplot-type"] == "function-object") {
        return get_fun(spec["module"], spec["method"])
    }
    // If JavaScript code, eval it
    if (spec["pyobsplot-type"] == "js") {
        // Use indirect eval to avoid bundling issues
        // See https://esbuild.github.io/content-types/#direct-eval
        let indirect_eval = eval
        return indirect_eval(spec["value"])
    }
    // If datetime, create a new Date object form iso format
    if (spec["pyobsplot-type"] == "datetime") {
        return new Date(spec["value"])
    }
    // If Geojson, returns as is
    if (spec["pyobsplot-type"] == "GeoJson") {
        return spec["value"]
    }
    // If dict-like with entries, parse entries recursively
    let ret = {}
    for (const [key, value] of Object.entries(spec)) {
        ret[key] = parse_spec(value)
    }
    return ret
}


// Returns JavaScript method object from module and method names
export function get_fun(mod, method) {
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

