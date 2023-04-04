#!/usr/bin/env node

/* jsdom rendering */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import { JSDOM } from "jsdom"
import { generate_plot } from "./plot.js"

// Create and initialize jsdom
const jsdom = new JSDOM("")
global.window = jsdom.window
global.document = jsdom.window.document
global.navigator = jsdom.window.navigator
global.Event = jsdom.window.Event
global.Node = jsdom.window.Node
global.NodeList = jsdom.window.NodeList
global.HTMLCollection = jsdom.window.HTMLCollection
// Make Plot and d3 available in js()
global.d3 = d3
global.Plot = Plot

function jsdom_plot(spec) {

    spec = JSON.parse(spec)
    let el = generate_plot(spec, "jsdom")

    for (const svg of el.tagName.toLowerCase() === "svg" ? [el] : el.querySelectorAll("svg")) {
        svg.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns", "http://www.w3.org/2000/svg");
        svg.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
        svg.style.color = "black"
    }
    for (const figure of el.tagName.toLowerCase() === "figure" ? [el] : el.querySelectorAll("figure")) {
        figure.style.color = "black"
        figure.style.backgroundColor = "white"
    }

    return el.outerHTML
}


process.stdin.setEncoding('utf8');
let data = ''
process.stdin.on('data', function (chunk) {
    data += chunk;
});
process.stdin.on('end', function () {
    let output = jsdom_plot(data)
    process.stdout.write(output)
});



