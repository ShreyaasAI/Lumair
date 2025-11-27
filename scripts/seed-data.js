#!/usr/bin/env node

const { exec } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');

const log = {
  success: (msg) => console.log(chalk.green('✓'), msg),
  error: (msg) => console.log(chalk.red('✗'), msg),
  info: (msg) => console.log(chalk.blue('ℹ'), msg)
};

const execPromise = (command) => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject({ error, stderr });
      } else {
        resolve(stdout);
      }
    });
  });
};

async function seedLocations() {
  const spinner = ora('Adding default monitoring locations...').start();
  try {
    const script = `
from database import SessionLocal
from ml.data_collector import DataCollector

db = SessionLocal()
try:
    collector = DataCollector(db)
    collector.initialize_default_locations()
    print('Locations added successfully')
except Exception as e:
    print(f'Error: {e}')
    raise
finally:
    db.close()
`;
    await execPromise(`docker-compose exec -T backend python -c "${script.replace(/\n/g, '; ')}"`);
    spinner.succeed('Default locations added');
    return true;
  } catch (error) {
    spinner.fail('Failed to add locations');
    log.error(error.stderr || error.error.message);
    return false;
  }
}

async function collectData() {
  const spinner = ora('Collecting AQI data for all locations...').start();
  try {
    const script = `
from database import SessionLocal
from ml.data_collector import DataCollector

db = SessionLocal()
try:
    collector = DataCollector(db)
    count = collector.collect_all_active_locations()
    print(f'Data collected for {count} locations')
except Exception as e:
    print(f'Error: {e}')
    raise
finally:
    db.close()
`;
    const output = await execPromise(`docker-compose exec -T backend python -c "${script.replace(/\n/g, '; ')}"`);
    spinner.succeed('Data collection complete');
    log.info(output.trim());
    return true;
  } catch (error) {
    spinner.fail('Failed to collect data');
    log.error(error.stderr || error.error.message);
    return false;
  }
}

async function main() {
  console.log(chalk.bold.cyan('\n🌱 Seeding Database\n'));

  const locationsAdded = await seedLocations();
  if (!locationsAdded) {
    process.exit(1);
  }

  const dataCollected = await collectData();
  if (!dataCollected) {
    process.exit(1);
  }

  console.log(chalk.bold.green('\n✅ Database seeded successfully!\n'));
}

main();