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

    test('syntax.ipynb', async ({ page }) => {
        await test_notebook(page, "syntax");
    });

    test('dates.ipynb', async ({ page }) => {
        await test_notebook(page, "dates");
    });

    test('errors.ipynb', async ({ page }) => {
        await test_notebook(page, "errors");
    });

    test('complex_plots.ipynb', async ({ page }) => {
        await test_notebook(page, "complex_plots");
    });

    test('data_sources.ipynb', async ({ page }) => {
        await test_notebook(page, "data_sources");
    });

    test('transforms.ipynb', async ({ page }) => {
        await test_notebook(page, "transforms");
    });

    test('geo.ipynb', async ({ page }) => {
        await test_notebook(page, "geo");
    });


});