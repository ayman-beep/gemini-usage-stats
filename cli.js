#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Path to your main python script
const pythonScript = path.join(__dirname, 'generate_dashboard.py');

// Heuristic to find python
const pythonBin = process.platform === 'win32' ? 'python' : 'python3';

if (!fs.existsSync(pythonScript)) {
    console.error(`Error: Could not find ${pythonScript}`);
    process.exit(1);
}

console.log('🚀 Launching Gemini Analytics (via npx)...');

const child = spawn(pythonBin, [pythonScript], {
    stdio: 'inherit',
    shell: true
});

child.on('error', (err) => {
    console.error(`Failed to start Python: ${err.message}`);
    console.log('Make sure Python is installed and in your PATH.');
});

child.on('close', (code) => {
    if (code !== 0) {
        console.log(`❌ Dashboard generation failed (exit code ${code})`);
    }
});
