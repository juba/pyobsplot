import { expect, galata, test } from '@jupyterlab/galata';

import * as path from 'path';

async function test_notebook(page, notebook) {
    const notebook_file = `${notebook}.ipynb`;
    await page.notebook.openByPath(notebook_file);
    await page.notebook.activate(notebook_file);

    const captures = new Array<Buffer>();
    const cellCount = await page.notebook.getCellCount();

    await page.notebook.runCellByCell({
        onAfterCellRun: async (cellIndex: number) => {
            const cell = await page.notebook.getCellOutput(cellIndex);
            if (cell) {
                captures.push(await cell.screenshot());
            }
        },
    });

    await page.notebook.save();

    for (let i = 0; i < cellCount; i++) {
        const image = `${notebook}-widgets-cell-${i}.png`;
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

    for (let notebook of notebooks) {
        test(`${notebook}.ipynb`, async ({ page }) => {
            await test_notebook(page, notebook);
        });
    }

});