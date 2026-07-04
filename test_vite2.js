const { spawn } = require('child_process');
const http = require('http');

const vite = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5176'], {
    cwd: 'D:\\Projects\\frontend\\frontend-vite',
    stdio: ['ignore', 'pipe', 'pipe']
});

let output = '';
vite.stdout.on('data', (data) => { output += data.toString(); });
vite.stderr.on('data', (data) => { output += data.toString(); });

function fetchUrl(path) {
    return new Promise((resolve, reject) => {
        http.get('http://localhost:5176' + path, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve({ status: res.statusCode, body }));
        }).on('error', reject);
    });
}

setTimeout(async () => {
    try {
        const main = await fetchUrl('/src/main.jsx');
        console.log('main.jsx status:', main.status);
        console.log('main.jsx body (first 800 chars):');
        console.log(main.body.substring(0, 800));
        console.log('---');
        
        // Check for error words
        if (main.body.includes('error') || main.body.includes('Error')) {
            console.log('Possible error detected in main.jsx');
        }
    } catch(e) {
        console.log('Error:', e.message);
    }
    
    vite.kill();
    process.exit(0);
}, 8000);
