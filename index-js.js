#!/usr/bin/env node

const { PythonShell } = require('python-shell');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

// Print banner
console.log('🏠 Zillow MCP Server');
console.log('Access Zillow real estate data via Model Context Protocol');
console.log('-----------------------------------------------------------');

// Check if Python is installed
function checkPythonInstalled() {
  try {
    const pythonVersion = spawn('python', ['--version']);
    return new Promise((resolve) => {
      pythonVersion.on('close', (code) => {
        resolve(code === 0);
      });
    });
  } catch (error) {
    return Promise.resolve(false);
  }
}

// Install required dependencies
async function installDependencies() {
  console.log('🔧 Installing required dependencies...');
  return new Promise((resolve, reject) => {
    const pip = spawn('pip', ['install', 'fastmcp', 'requests', 'python-dotenv', 'backoff']);
    
    pip.stdout.on('data', (data) => {
      console.log(`${data}`);
    });
    
    pip.stderr.on('data', (data) => {
      console.error(`${data}`);
    });
    
    pip.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Dependencies installed successfully.');
        resolve();
      } else {
        console.error('❌ Failed to install dependencies.');
        reject(new Error('Dependency installation failed'));
      }
    });
  });
}

// Check API key and create .env if needed
function setupApiKey() {
  // Check environment variable first
  const apiKey = process.env.ZILLOW_API_KEY;
  
  if (!apiKey) {
    console.warn('⚠️  Warning: ZILLOW_API_KEY environment variable not found.');
    console.log('You can set it with: export ZILLOW_API_KEY=your_key_here');
  } else {
    console.log('✅ ZILLOW_API_KEY environment variable found.');
  }
  
  return Promise.resolve();
}

// Run the MCP server
function runServer() {
  const serverPath = path.join(__dirname, 'zillow_mcp_server.py');
  
  // Check if we have the server file
  if (!fs.existsSync(serverPath)) {
    console.error('❌ Error: zillow_mcp_server.py not found.');
    process.exit(1);
  }
  
  console.log('🚀 Starting Zillow MCP Server...');
  
  // Pass any command line arguments to the Python script
  const options = {
    mode: 'text',
    pythonOptions: ['-u'], // unbuffered output
    args: process.argv.slice(2)
  };
  
  const pyshell = new PythonShell(serverPath, options);
  
  pyshell.on('message', (message) => {
    console.log(message);
  });
  
  pyshell.on('error', (err) => {
    console.error('❌ Error:', err);
  });
  
  pyshell.on('close', (code) => {
    if (code !== 0) {
      console.error(`❌ Server exited with code ${code}`);
    }
  });
  
  // Handle termination signals
  process.on('SIGINT', () => {
    console.log('\n📢 Stopping Zillow MCP Server...');
    pyshell.terminate();
  });
}

// Main function
async function main() {
  try {
    const isPythonInstalled = await checkPythonInstalled();
    
    if (!isPythonInstalled) {
      console.error('❌ Error: Python not found. Please install Python 3.8 or higher.');
      process.exit(1);
    }
    
    await installDependencies();
    await setupApiKey();
    runServer();
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run main
main();
