#!/usr/bin/env node

const axios = require('axios');
const chalk = require('chalk');

const API_URL = process.env.API_URL || 'http://localhost:8000';

const log = {
  test: (name) => console.log(chalk.bold.blue(`\n🧪 ${name}`)),
  success: (msg) => console.log(chalk.green('  ✓'), msg),
  error: (msg) => console.log(chalk.red('  ✗'), msg),
  data: (data) => console.log(chalk.gray(JSON.stringify(data, null, 2)))
};

async function testEndpoint(name, method, url, params = {}) {
  log.test(name);
  try {
    const response = await axios({
      method,
      url: `${API_URL}${url}`,
      params,
      timeout: 10000
    });
    log.success(`Status: ${response.status}`);
    log.data(response.data);
    return true;
  } catch (error) {
    log.error(`Failed: ${error.message}`);
    if (error.response) {
      log.error(`Status: ${error.response.status}`);
      log.data(error.response.data);
    }
    return false;
  }
}

async function runTests() {
  console.log(chalk.bold.cyan('\n🧪 Testing Lumair API'));
  console.log(chalk.gray(`API URL: ${API_URL}`));
  console.log(chalk.gray('=' .repeat(50)));

  const tests = [
    ['Health Check', 'GET', '/health'],
    ['Root Endpoint', 'GET', '/'],
    ['Current AQI - Mumbai', 'GET', '/api/aqi/current/Mumbai'],
    ['AQI Prediction - Mumbai', 'GET', '/api/aqi/predict/Mumbai', { hours: '24,48,72' }],
    ['Historical AQI - Mumbai', 'GET', '/api/aqi/historical/Mumbai', { days: 7 }],
    ['Search Locations', 'GET', '/api/locations/search', { q: 'New York' }],
    ['Popular Locations', 'GET', '/api/locations/popular'],
    ['Compare Cities', 'GET', '/api/aqi/compare', { cities: 'Mumbai,Delhi,Beijing' }]
  ];

  let passed = 0;
  let failed = 0;

  for (const [name, method, url, params] of tests) {
    const result = await testEndpoint(name, method, url, params);
    if (result) passed++;
    else failed++;
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log(chalk.bold.cyan('\n' + '='.repeat(50)));
  console.log(chalk.bold(`\n📊 Results: ${chalk.green(passed + ' passed')} ${chalk.red(failed + ' failed')}`));
  console.log(chalk.gray(`\n📖 Full API documentation: ${API_URL}/docs\n`));

  process.exit(failed > 0 ? 1 : 0);
}

runTests();