import { expect, galata, test } from '@jupyterlab/galata';

import * as path from 'path';

async function test_notebook(page, notebook, renderer) {
    const notebook_file = `${notebook}.ipynb`;
    await page.notebook.openByPath(notebook_file);
    await page.notebook.activate(notebook_file);

    const captures = new Array<Buffer>();
    const cellCount = await page.notebook.getCellCount();
    // Replace first cell by Obsplot + set_renderer
    await page.notebook.setCell(0, "code", `from pyobsplot import Obsplot, Plot, d3, Math, js; Obsplot.set_renderer('${renderer}'); print('${renderer}')`)

    await page.notebook.runCellByCell({
        onAfterCellRun: async (cellIndex: number) => {
            const cell = await page.notebook.getCellOutput(cellIndex);
            if (cell) {
                captures.push(await cell.screenshot());
            }
        },
    });

    await page.notebook.save();

    for (let i = 0; i < (cellCount); i++) {
        const image = `${renderer}-${notebook}-cell-${i}.png`;
        expect(captures[i]).toMatchSnapshot(image);
    }
}

test.describe('Visual Regression', () => {

    test.beforeEach(async ({ page, tmpPath }) => {
        await page.contents.uploadDirectory(
            path.resolve(path.resolve(''), `./tests/ui/tests/notebooks/`),
            '/'
        );
        await page.filebrowser.openDirectory('/');
    });

    let notebooks = ["syntax", "dates", "errors", "complex_plots", "data_sources", "transforms", "geo"];

    // check all renderers
    for (let renderer of ["widget", "jsdom"]) {
        // check all notebooks
        for (let notebook of notebooks) {
            test(`${renderer} / ${notebook}.ipynb`, async ({ page }) => {
                await test_notebook(page, notebook, renderer);
            });
        }
    }

});