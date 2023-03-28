const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
    ...baseConfig,
    timeout: 60000,
    retries: 0,
};