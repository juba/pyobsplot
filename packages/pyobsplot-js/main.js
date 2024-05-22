#!/usr/bin/env node

/* jsdom rendering */

import * as Plot from "@observablehq/plot";
import * as d3 from "d3";
import * as http from "node:http";
import { JSDOM } from "jsdom";
import { generate_plot } from "./plot.js";

// Create and initialize jsdom
const jsdom = new JSDOM("");
global.window = jsdom.window;
global.document = jsdom.window.document;
global.navigator = jsdom.window.navigator;
global.Event = jsdom.window.Event;
global.Node = jsdom.window.Node;
global.NodeList = jsdom.window.NodeList;
global.HTMLCollection = jsdom.window.HTMLCollection;
// Make Plot and d3 available in js()
global.d3 = d3;
global.Plot = Plot;

// jsdom plot generator
function jsdom_plot(request) {
    request = JSON.parse(request);
    let el = generate_plot(request["spec"], "jsdom");

    // foreground color
    const bg = { light: "white", dark: "black", current: "transparent" };
    // background color
    const fg = { light: "black", dark: "white", current: "currentColor" };
    const theme = request["theme"];

    for (const svg of el.tagName.toLowerCase() === "svg"
        ? [el]
        : el.querySelectorAll("svg")) {
        svg.setAttributeNS(
            "http://www.w3.org/2000/xmlns/",
            "xmlns",
            "http://www.w3.org/2000/svg"
        );
        svg.setAttributeNS(
            "http://www.w3.org/2000/xmlns/",
            "xmlns:xlink",
            "http://www.w3.org/1999/xlink"
        );
        // theming
        svg.style.color ||= fg[theme];
        svg.style.backgroundColor ||= bg[theme];
    }
    for (const figure of el.tagName.toLowerCase() === "figure"
        ? [el]
        : el.querySelectorAll("figure")) {
        figure.style.padding ||= "0px 5px 5px 5px";
        // theming
        figure.style.color ||= fg[theme];
        figure.style.backgroundColor ||= bg[theme];
        for (const h2 of figure.querySelectorAll("h2")) {
            h2.style.lineHeight = "28px";
            h2.style.fontSize = "20px";
            h2.style.fontWeight = "600";
            h2.style.margin = "0";
        }
        for (const h3 of figure.querySelectorAll("h3")) {
            h3.style.lineHeight = "24px";
            h3.style.fontSize = "16px";
            h3.style.fontWeight = "400";
            h3.style.margin = "0";
        }
        for (const figcaption of figure.querySelectorAll("figcaption")) {
            figcaption.style.lineHeight = "20px";
            figcaption.style.fontSize = "12px";
            figcaption.style.fontWeight = "500";
            figcaption.style.color = "#555555";
        }
    }

    return el.outerHTML;
}

// Request listener for http server
const requestListener = function (req, res) {
    // Send back plain text
    res.setHeader("Content-Type", "text/plain");
    switch (req.url) {
        // plot entry point
        case "/plot":
            let body = "";
            req.on("data", (chunk) => {
                body += chunk.toString();
            });
            req.on("end", () => {
                let output;
                try {
                    output = jsdom_plot(body);
                } catch (error) {
                    res.writeHead(500);
                    res.end(`Server error: ${error.message}.`);
                    return;
                }
                res.writeHead(200);
                res.end(output);
            });
            break;
        // status entry point
        case "/status":
            res.writeHead(200);
            res.end("pyobsplot");
            break;
        // else
        default:
            res.writeHead(404);
            res.end("Resource not found");
    }
};

// let OS find a free port
const port = 0;
const host = "localhost";
// Launch server
const server = http.createServer(requestListener);
server.listen(port, host, () => {
    // send selected port to stdout
    const port = server.address().port;
    process.stdout.write(port + "\n");
});
