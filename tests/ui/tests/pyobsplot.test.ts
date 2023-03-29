import { expect, galata, test } from '@jupyterlab/galata';

import * as path from 'path';

test.describe('Visual Regression', () => {

    // test.beforeAll(async ({ request, tmpPath }) => {
    //     const contents = galata.newContentsHelper(request);
    //     await contents.uploadFile(
    //         path.resolve(path.resolve(''), `./tests/ui/tests/notebooks/${notebook}`),
    //         `${tmpPath}/${notebook}`
    //     );
    // });

    test.beforeEach(async ({ page, tmpPath }) => {
        await page.contents.uploadDirectory(
            path.resolve(path.resolve(''), `./tests/ui/tests/notebooks/`),
            '/'
        );
        await page.filebrowser.openDirectory('/');
    });

    // test.afterAll(async ({ request, tmpPath }) => {
    //     const contents = galata.newContentsHelper(request);
    //     await contents.deleteDirectory(tmpPath);
    // });

    test('tests.ipynb outputs', async ({
        page,
        tmpPath,
    }) => {
        const notebook = 'tests.ipynb';
        await page.notebook.openByPath(`${notebook}`);
        await page.notebook.activate(notebook);

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
            const image = `widgets-cell-${i}.png`;
            expect(captures[i]).toMatchSnapshot(image);
        }
    });
});