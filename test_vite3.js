const { spawn } = require('child_process');
const http = require('http');

const vite = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5177'], {
    cwd: 'D:\\Projects\\frontend\\frontend-vite',
    stdio: ['ignore', 'pipe', 'pipe']
});

let output = '';
vite.stdout.on('data', (data) => { output += data.toString(); });
vite.stderr.on('data', (data) => { output += data.toString(); });

function fetchUrl(path) {
    return new Promise((resolve, reject) => {
        http.get('http://localhost:5177' + path, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve({ status: res.statusCode, body }));
        }).on('error', reject);
    });
}

setTimeout(async () => {
    try {
        // Try to fetch the index.css transform
        const css = await fetchUrl('/src/index.css');
        console.log('CSS status:', css.status);
        console.log('CSS body (first 600 chars):');
        console.log(css.body.substring(0, 600));
        console.log('---');
        
        // Try to fetch App.jsx
        const app = await fetchUrl('/src/App.jsx');
        console.log('App.jsx status:', app.status);
        console.log('App.jsx body (first 200 chars):');
        console.log(app.body.substring(0, 200));
        if (app.body.length > 200) {
            console.log('...(truncated, total:', app.body.length, 'chars)');
        }
        
        // Check for error indicators
        if (app.status !== 200 || app.body.includes('Error')) {
            console.log('App.jsx might have issues');
        }
    } catch(e) {
        console.log('Error:', e.message);
        console.log('Vite output:', output.substring(0, 300));
    }
    
    vite.kill();
    process.exit(0);
}, 8000);
