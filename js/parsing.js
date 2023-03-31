/* Plot specification parsing */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import * as arrow from "apache-arrow"

// Make Plot and d3 available in js()
window.d3 = d3
window.Plot = Plot

export function unserialize_data(data) {
    let result = Array()
    for (let d of data) {
        if (d["pyobsplot-type"] == "DataFrame") {
            result.push(arrow.tableFromIPC(d["value"]))
        } else {
            result.push(d)
        }
    }
    return result
}


// Main function : recursively parse a JSON specification 
export function parse_spec(code, data) {
    // If null, return null
    if (code === null) {
        return null
    }
    // If Array, recursively parse elements
    if (Array.isArray(code)) {
        return code.map(d => parse_spec(d, data))
    }
    // If a string, returns as is
    if (typeof code === 'string' || code instanceof String) {
        return code
    }
    // If not dict-like, returns as is
    if (Object.entries(code).length == 0) {
        return code
    }
    // If DataFrame type, deserialize Arrow IPC
    if (code["pyobsplot-type"] == "DataFrame") {
        return arrow.tableFromIPC(code["value"])
    }
    // If DataFrame-ref type, deserialize Arrow IPC from cache
    if (code["pyobsplot-type"] == "DataFrame-ref") {
        return data[code["value"]]
    }
    // If a JS function with arguments type, get function from name and call it
    if (code["pyobsplot-type"] == "function") {
        let fun = get_fun(code["module"], code["method"])
        return fun.call(null, ...parse_spec(code["args"], data));
    }
    // If a JS function object type, get function from name and call it
    if (code["pyobsplot-type"] == "function-object") {
        return get_fun(code["module"], code["method"])
    }
    // If JavaScript code, eval it
    if (code["pyobsplot-type"] == "js") {
        // Use indirect eval to avoid bundling issues
        // See https://esbuild.github.io/content-types/#direct-eval
        let indirect_eval = eval
        return indirect_eval(code["value"])
    }
    // If datetime, create a new Date object form iso format
    if (code["pyobsplot-type"] == "datetime") {
        return new Date(code["value"])
    }
    // If Geojson, returns as is
    if (code["pyobsplot-type"] == "GeoJson") {
        return code["value"]
    }
    // If GeoJson-ref, returns as is from cache
    if (code["pyobsplot-type"] == "GeoJson-ref") {
        return data[code["value"]]
    }

    // If dict-like with entries, parse entries recursively
    let ret = {}
    for (const [key, value] of Object.entries(code)) {
        ret[key] = parse_spec(value, data)
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

