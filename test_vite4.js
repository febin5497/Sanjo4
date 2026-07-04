const { spawn } = require('child_process');
const http = require('http');

const vite = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5178'], {
    cwd: 'D:\\Projects\\frontend\\frontend-vite',
    stdio: ['ignore', 'pipe', 'pipe']
});

function fetchUrl(path) {
    return new Promise((resolve, reject) => {
        http.get('http://localhost:5178' + path, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => resolve({ status: res.statusCode, body }));
        }).on('error', reject);
    });
}

setTimeout(async () => {
    try {
        const css = await fetchUrl('/src/index.css');
        console.log('CSS status:', css.status);
        console.log('CSS length:', css.body.length);
        // Check for tailwind tokens
        if (css.body.includes('tailwind') || css.body.includes('@apply') || css.body.includes('ml-')) {
            console.log('Has tailwind-like content');
        }
        if (css.body.includes('import.meta.hot')) {
            console.log('Has HMR client (correct)');
        }
        // Check for error
        if (css.body.includes('Error') || css.body.includes(' error') || css.status !== 200) {
            console.log('CSS might have errors');
        } else {
            console.log('CSS looks OK');
        }
    } catch(e) {
        console.log('Error:', e.message);
    }
    vite.kill();
    process.exit(0);
}, 8000);
