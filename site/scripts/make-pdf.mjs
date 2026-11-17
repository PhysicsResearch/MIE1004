// Makes the downloadable PDF of the lab from the single-page view at /print/.
//
//   npm run pdf
//
// That command builds the site first, then runs this script, which serves the built site
// locally and prints /print/ to public/<pdf file> with Microsoft Edge or Google Chrome.
// Commit the new PDF so Vercel publishes it. To use another Chromium-based browser,
// set the CHROME_PATH environment variable to its executable.

import { execFile } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { pdf } from '../src/outline.mjs';

const root = fileURLToPath(new URL('..', import.meta.url));
const dist = join(root, 'dist');
const output = join(root, 'public', pdf.href.replace(/^\//, ''));

const contentTypes = {
	'.html': 'text/html; charset=utf-8',
	'.css': 'text/css',
	'.js': 'text/javascript',
	'.json': 'application/json',
	'.svg': 'image/svg+xml',
	'.png': 'image/png',
	'.jpg': 'image/jpeg',
	'.webp': 'image/webp',
	'.woff2': 'font/woff2',
};

function findBrowser() {
	const candidates = [
		process.env.CHROME_PATH,
		'C:/Program Files/Google/Chrome/Application/chrome.exe',
		'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
		'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
		'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
		'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
		'/usr/bin/google-chrome',
		'/usr/bin/chromium',
		'/usr/bin/chromium-browser',
		'/usr/bin/microsoft-edge',
	];
	const browser = candidates.find((path) => path && existsSync(path));
	if (!browser) {
		throw new Error('No Edge or Chrome found. Set CHROME_PATH to a Chromium-based browser.');
	}
	return browser;
}

if (!existsSync(join(dist, 'print', 'index.html'))) {
	throw new Error('dist/print/index.html is missing. Run `npm run pdf` (it builds the site first).');
}

// Minimal static file server for the built site.
const server = createServer(async (request, response) => {
	try {
		const urlPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
		let file = join(dist, normalize(urlPath));
		if (file !== dist && !file.startsWith(dist + sep)) throw new Error('Outside dist');
		if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
		const body = await readFile(file);
		response.writeHead(200, { 'content-type': contentTypes[extname(file)] ?? 'application/octet-stream' });
		response.end(body);
	} catch {
		response.writeHead(404);
		response.end('Not found');
	}
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const { port } = server.address();

// Edge on Windows can return before it has finished printing, so wait until the
// PDF file exists and has stopped growing.
async function waitForPdf(timeoutMs = 60_000) {
	let lastSize = -1;
	for (let waited = 0; waited < timeoutMs; waited += 500) {
		const size = existsSync(output) ? (await stat(output)).size : -1;
		if (size > 0 && size === lastSize) return;
		lastSize = size;
		await new Promise((resolve) => setTimeout(resolve, 500));
	}
	throw new Error(`The browser did not write ${output} within ${timeoutMs / 1000} s.`);
}

await rm(output, { force: true });

// A throwaway browser profile, so this works even while the browser is already open.
const profile = await mkdtemp(join(tmpdir(), 'lab-pdf-'));
try {
	await promisify(execFile)(findBrowser(), [
		'--headless',
		'--disable-gpu',
		'--no-first-run',
		`--user-data-dir=${profile}`,
		'--no-pdf-header-footer',
		'--virtual-time-budget=10000',
		`--print-to-pdf=${output}`,
		`http://127.0.0.1:${port}/print/`,
	]);
	await waitForPdf();
	console.log(`PDF written to ${output}`);
} finally {
	server.close();
	await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 });
}
