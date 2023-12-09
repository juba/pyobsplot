/* Tests parsing */

import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import * as assert from "assert";

import { parse_spec, get_fun } from "../parsing.js";

describe("get_fun", function () {
    it("should return correct method", function () {
        assert.equal(get_fun("Plot", "plot"), Plot.plot);
        assert.equal(get_fun("d3", "cumsum"), d3.cumsum);
        assert.equal(get_fun("Math", "random"), Math.random);
    });
    it("should raise exception if incorrect method", function () {
        assert.throws(() => get_fun("Plot", "foobar"), Error);
        assert.throws(() => get_fun("Foobar"), Error);
    });
});

describe("parse_spec", function () {
    it("should return correct results for base elements", function () {
        assert.equal(parse_spec(null), null);
        assert.equal(parse_spec("yo"), "yo");
        assert.equal(parse_spec(45), 45);
        assert.deepStrictEqual(parse_spec([1, ["foo", null]]), [1, ["foo", null]]);
        assert.deepStrictEqual(parse_spec({ x: 1, y: { x2: "foo", y2: null } }), {
            x: 1,
            y: { x2: "foo", y2: null },
        });
    });
    it("should return correct results for typed elements", function () {
        assert.equal(parse_spec({ "pyobsplot-type": "js", value: "1 + 2" }), 3);
        assert.deepStrictEqual(
            parse_spec({
                "pyobsplot-type": "GeoJson",
                value: { "pyobsplot-type": "js", value: 2 },
            }),
            { "pyobsplot-type": "js", value: 2 }
        );
        assert.equal(
            parse_spec({
                "pyobsplot-type": "datetime",
                value: "2023-01-01T14:25:10",
            }).getTime(),
            new Date("2023-01-01T14:25:10").getTime()
        );
        assert.equal(
            parse_spec({
                "pyobsplot-type": "function-object",
                module: "Math",
                method: "random",
            }),
            Math.random
        );
        assert.equal(
            parse_spec({
                "pyobsplot-type": "function",
                module: "Math",
                method: "min",
                args: [1, 2, 3],
            }),
            Math.min(1, 2, 3)
        );
    });
    it("should return correct results for DataFrames", function () {
        // FIXME: add tests
    });
    it("should return correct results for cached elements", function () {
        assert.equal(
            parse_spec({ "pyobsplot-type": "GeoJson-ref", value: 0 }, ["foobar"]),
            "foobar"
        );
    });
});
