const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
    ...baseConfig,
    timeout: 2400000,
    retries: 0,
};