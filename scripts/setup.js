#!/usr/bin/env node

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const prompts = require('prompts');
const chalk = require('chalk');
const ora = require('ora');

const log = {
  info: (msg) => console.log(chalk.blue('ℹ'), msg),
  success: (msg) => console.log(chalk.green('✓'), msg),
  error: (msg) => console.log(chalk.red('✗'), msg),
  warn: (msg) => console.log(chalk.yellow('⚠'), msg),
  title: (msg) => console.log(chalk.bold.cyan(`\n${msg}\n${'='.repeat(msg.length)}`))
};

const execPromise = (command, options = {}) => {
  return new Promise((resolve, reject) => {
    exec(command, options, (error, stdout, stderr) => {
      if (error) {
        reject({ error, stderr });
      } else {
        resolve(stdout);
      }
    });
  });
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function checkDocker() {
  const spinner = ora('Checking Docker installation...').start();
  try {
    await execPromise('docker --version');
    await execPromise('docker-compose --version');
    spinner.succeed('Docker and Docker Compose are installed');
    return true;
  } catch (error) {
    spinner.fail('Docker or Docker Compose not found');
    log.error('Please install Docker Desktop: https://www.docker.com/products/docker-desktop');
    return false;
  }
}

async function setupEnvironment() {
  log.title('🌍 Lumair Setup');
  
  const envPath = path.join(process.cwd(), '.env');
  const envExamplePath = path.join(process.cwd(), '.env.example');

  if (fs.existsSync(envPath)) {
    const { overwrite } = await prompts({
      type: 'confirm',
      name: 'overwrite',
      message: '.env file already exists. Overwrite?',
      initial: false
    });

    if (!overwrite) {
      log.info('Using existing .env file');
      return true;
    }
  }

  log.info('Creating .env file...');

  const questions = [
    {
      type: 'text',
      name: 'OPENWEATHER_API_KEY',
      message: 'Enter your OpenWeatherMap API key:',
      validate: value => value.length > 0 || 'API key is required'
    },
    {
      type: 'text',
      name: 'WAQI_API_KEY',
      message: 'Enter your WAQI API key:',
      validate: value => value.length > 0 || 'API key is required'
    },
    {
      type: 'text',
      name: 'DATABASE_URL',
      message: 'Database URL:',
      initial: 'postgresql://lumair:lumair_password@postgres:5432/lumair'
    },
    {
      type: 'text',
      name: 'SECRET_KEY',
      message: 'Secret key (for JWT):',
      initial: () => require('crypto').randomBytes(32).toString('hex')
    }
  ];

  const answers = await prompts(questions);

  if (!answers.OPENWEATHER_API_KEY || !answers.WAQI_API_KEY) {
    log.error('Setup cancelled - API keys are required');
    log.info('Get API keys:');
    log.info('  OpenWeatherMap: https://openweathermap.org/api');
    log.info('  WAQI: https://aqicn.org/data-platform/token/');
    return false;
  }

  // Create .env file
  const envContent = `# Database
DATABASE_URL=${answers.DATABASE_URL}

# API Keys
OPENWEATHER_API_KEY=${answers.OPENWEATHER_API_KEY}
WAQI_API_KEY=${answers.WAQI_API_KEY}

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT Secret
SECRET_KEY=${answers.SECRET_KEY}

# Data Collection
DATA_REFRESH_INTERVAL=3600

# Frontend
VITE_API_URL=http://localhost:8000
`;

  fs.writeFileSync(envPath, envContent);
  log.success('.env file created');
  return true;
}

async function startServices() {
  const spinner = ora('Starting Docker containers...').start();
  try {
    await execPromise('docker-compose up -d');
    spinner.succeed('Docker containers started');
    return true;
  } catch (error) {
    spinner.fail('Failed to start Docker containers');
    log.error(error.stderr || error.error.message);
    return false;
  }
}

async function waitForDatabase() {
  const spinner = ora('Waiting for database to be ready...').start();
  let attempts = 0;
  const maxAttempts = 30;

  while (attempts < maxAttempts) {
    try {
      await execPromise('docker-compose exec -T postgres pg_isready -U lumair');
      spinner.succeed('Database is ready');
      return true;
    } catch (error) {
      attempts++;
      await sleep(2000);
    }
  }

  spinner.fail('Database failed to start');
  return false;
}

async function initializeDatabase() {
  const spinner = ora('Initializing database...').start();
  try {
    await execPromise('docker-compose exec -T backend python -c "from database import init_db; init_db()"');
    spinner.succeed('Database initialized');
    return true;
  } catch (error) {
    spinner.fail('Failed to initialize database');
    log.error(error.stderr || error.error.message);
    return false;
  }
}

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
    print('Default locations added')
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

async function collectInitialData() {
  const spinner = ora('Collecting initial AQI data (this may take 1-2 minutes)...').start();
  try {
    const script = `
from database import SessionLocal
from ml.data_collector import DataCollector

db = SessionLocal()
try:
    collector = DataCollector(db)
    count = collector.collect_all_active_locations()
    print(f'Collected data for {count} locations')
except Exception as e:
    print(f'Error: {e}')
    raise
finally:
    db.close()
`;
    await execPromise(`docker-compose exec -T backend python -c "${script.replace(/\n/g, '; ')}"`);
    spinner.succeed('Initial data collection complete');
    return true;
  } catch (error) {
    spinner.fail('Failed to collect initial data');
    log.warn('You can retry later with: pnpm ml:collect');
    return true; // Non-critical, continue
  }
}

async function displaySummary() {
  console.log('\n');
  log.title('✅ Setup Complete!');
  
  console.log(chalk.bold('\n📡 Services Running:'));
  console.log('  Frontend: ' + chalk.cyan('http://localhost:5173'));
  console.log('  Backend:  ' + chalk.cyan('http://localhost:8000'));
  console.log('  API Docs: ' + chalk.cyan('http://localhost:8000/docs'));

  console.log(chalk.bold('\n📝 Next Steps:'));
  console.log('  1. Open ' + chalk.cyan('http://localhost:5173') + ' in your browser');
  console.log('  2. Search for a city to see current AQI');
  console.log('  3. Wait 24+ hours for data collection');
  console.log('  4. Train ML model: ' + chalk.yellow('pnpm ml:train'));

  console.log(chalk.bold('\n🛠️  Useful Commands:'));
  console.log('  ' + chalk.yellow('pnpm start') + '       - Start services');
  console.log('  ' + chalk.yellow('pnpm stop') + '        - Stop services');
  console.log('  ' + chalk.yellow('pnpm logs') + '        - View logs');
  console.log('  ' + chalk.yellow('pnpm test:api') + '    - Test API endpoints');
  console.log('  ' + chalk.yellow('pnpm ml:train') + '    - Train ML model');
  console.log('  ' + chalk.yellow('pnpm ml:collect') + '  - Collect data manually');

  console.log('\n');
}

async function main() {
  try {
    // Check Docker
    const hasDocker = await checkDocker();
    if (!hasDocker) {
      process.exit(1);
    }

    // Setup environment
    const envSetup = await setupEnvironment();
    if (!envSetup) {
      process.exit(1);
    }

    // Start services
    const servicesStarted = await startServices();
    if (!servicesStarted) {
      process.exit(1);
    }

    // Wait for database
    const dbReady = await waitForDatabase();
    if (!dbReady) {
      process.exit(1);
    }

    // Initialize database
    const dbInitialized = await initializeDatabase();
    if (!dbInitialized) {
      process.exit(1);
    }

    // Seed locations
    await seedLocations();

    // Collect initial data
    await collectInitialData();

    // Display summary
    await displaySummary();

  } catch (error) {
    log.error('Setup failed:');
    console.error(error);
    process.exit(1);
  }
}

main();