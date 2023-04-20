#!/usr/bin/env node

/* jsdom rendering */

import * as Plot from "@observablehq/plot"
import * as d3 from "d3"
import * as http from "node:http"
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

// jsdom plot generator
function jsdom_plot(spec) {

    spec = JSON.parse(spec)
    let el = generate_plot(spec, "jsdom")

    for (const svg of el.tagName.toLowerCase() === "svg" ? [el] : el.querySelectorAll("svg")) {
        svg.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns", "http://www.w3.org/2000/svg");
        svg.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
        if (svg.style.color == "") {
            svg.style.color = "black"
        }
    }
    for (const figure of el.tagName.toLowerCase() === "figure" ? [el] : el.querySelectorAll("figure")) {
        if (figure.style.color == "") {
            figure.style.color = "black"
        }
        if (figure.style.backgroundColor == "") {
            figure.style.backgroundColor = "white"
        }
    }

    return el.outerHTML
}


// Request listener for http server
const requestListener = function (req, res) {
    // Send back plain text
    res.setHeader("Content-Type", "text/plain");
    switch (req.url) {
        // plot entry point
        case "/plot":
            let body = '';
            req.on('data', (chunk) => {
                body += chunk.toString();
            });
            req.on('end', () => {
                let output
                try {
                    output = jsdom_plot(body)
                } catch (error) {
                    res.writeHead(500);
                    res.end(`Server error: ${error.message}.`);
                    return
                }
                res.writeHead(200);
                res.end(output);
            })
            break
        // status entry point
        case "/status":
            res.writeHead(200);
            res.end("pyobsplot");
            break
        // else
        default:
            res.writeHead(404);
            res.end("Resource not found");
    }
}


// let OS find a free port
const port = 0
const host = "localhost"
// Launch server
const server = http.createServer(requestListener);
server.listen(port, host, () => {
    // send selected port to stdout
    const port = server.address().port;
    process.stdout.write(port + "\n");
});

