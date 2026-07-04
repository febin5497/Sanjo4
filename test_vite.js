const { spawn } = require('child_process');
const http = require('http');

const vite = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5175'], {
    cwd: 'D:\\Projects\\frontend\\frontend-vite',
    stdio: ['ignore', 'pipe', 'pipe']
});

let output = '';
vite.stdout.on('data', (data) => { output += data.toString(); });
vite.stderr.on('data', (data) => { output += data.toString(); });

setTimeout(() => {
    http.get('http://localhost:5175/', (res) => {
        let body = '';
        res.on('data', (chunk) => body += chunk);
        res.on('end', () => {
            console.log('HTML status:', res.statusCode);
            console.log('HTML length:', body.length);
            console.log('Title:', body.match(/<title>(.*?)<\/title>/)?.[1] || 'none');
            console.log('Has root div:', body.includes('id="root"'));
            vite.kill();
            process.exit(0);
        });
    }).on('error', (e) => {
        console.log('HTML fetch error:', e.message);
        console.log('Vite output:', output.substring(0, 500));
        vite.kill();
        process.exit(1);
    });
}, 8000);
