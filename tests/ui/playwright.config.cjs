const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
    ...baseConfig,
    reporter: [['html', { outputFolder: 'playwright-report' }]],
    outputDir: 'test-results',
    timeout: 2400000,
    retries: 0,
    fullyParallel: true,
};