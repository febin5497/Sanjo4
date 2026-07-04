const { spawn } = require('child_process');
const http = require('http');

const vite = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5180'], {
    cwd: 'D:\\Projects\\frontend\\frontend-vite',
    stdio: ['ignore', 'pipe', 'pipe']
});

let output = '';
vite.stdout.on('data', (data) => { output += data.toString(); });
vite.stderr.on('data', (data) => { output += data.toString(); });

function fetchUrl(path) {
    return new Promise((resolve, reject) => {
        http.get('http://localhost:5180' + path, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve({ status: res.statusCode, body }));
        }).on('error', reject);
    });
}

setTimeout(async () => {
    try {
        const app = await fetchUrl('/src/App.jsx');
        console.log('App.jsx status:', app.status);
        console.log('App.jsx length:', app.body.length);
        // Check for the 'Cannot access lazy before initialization' error
        if (app.body.includes('ReferenceError') || app.body.includes('Cannot access')) {
            console.log('ERROR DETECTED: Module still has TDZ issue');
        } else if (app.body.includes('import.*lazy.*from.*react') || app.body.match(/import[\s\S]*?lazy[\s\S]*?from[\s\S]*?react/)) {
            console.log('lazy import found in transformed output');
        } else {
            console.log('Checking for lazy...');
            // Check if 'lazy' appears as a function call in the transformed code
            if (app.body.includes('lazy(')) {
                console.log('lazy() call found - transform OK');
            } else {
                console.log('No lazy() call - suspicious');
            }
        }
        console.log('---');
        console.log('First 1000 chars of App.jsx transform:');
        console.log(app.body.substring(0, 1000));
    } catch(e) {
        console.log('Error:', e.message);
        console.log('Vite output:', output.substring(0, 500));
    }
    vite.kill();
    process.exit(0);
}, 8000);
