// Makes the downloadable PDF of the lab from the single-page view at /print/.
//
//   npm run pdf
//
// That command builds the site first, then runs this script. The script serves the built site
// locally, opens /print/ in Google Chrome or Microsoft Edge (headless), waits until all images
// are loaded, and prints it to public/<pdf file> with the website address and page numbers in
// the footer. Commit the new PDF so Vercel publishes it.
//
// Needs Node.js 22 or newer and Chrome or Edge. To use another Chromium-based browser,
// set the CHROME_PATH environment variable to its executable.

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { pdf, siteUrl } from '../src/outline.mjs';

const root = fileURLToPath(new URL('..', import.meta.url));
const dist = join(root, 'dist');
const output = join(root, 'public', pdf.href.replace(/^\//, ''));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

// Footer of every page: the website address and the page number.
const footer = `
	<div style="width: 100%; padding: 0 14mm; font-family: sans-serif; font-size: 8px; color: #666;
	            display: flex; justify-content: space-between;">
		<span>MIE1004 Lab · ${siteUrl.replace(/^https?:\/\//, '')}</span>
		<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
	</div>`;

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
const pageUrl = `http://127.0.0.1:${server.address().port}/print/`;

// Start the browser with a throwaway profile, so this works even while the browser is open.
// With --remote-debugging-port=0 the browser picks a free port and writes it to DevToolsActivePort.
const profile = await mkdtemp(join(tmpdir(), 'lab-pdf-'));
const browser = spawn(
	findBrowser(),
	['--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
		`--user-data-dir=${profile}`, '--remote-debugging-port=0', 'about:blank'],
	{ stdio: 'ignore' }
);

try {
	let port;
	for (let i = 0; i < 150 && !port; i++) {
		await sleep(200);
		const portFile = join(profile, 'DevToolsActivePort');
		if (existsSync(portFile)) port = Number((await readFile(portFile, 'utf8')).split('\n')[0]);
	}
	if (!port) throw new Error('The browser did not start.');

	let target;
	for (let i = 0; i < 50 && !target; i++) {
		const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
		target = targets.find((t) => t.type === 'page');
		if (!target) await sleep(200);
	}
	if (!target) throw new Error('The browser has no page to print.');

	// Talk to the page with the Chrome DevTools Protocol.
	const socket = new WebSocket(target.webSocketDebuggerUrl);
	await new Promise((resolve, reject) => {
		socket.onopen = resolve;
		socket.onerror = reject;
	});
	let nextId = 0;
	const pending = new Map();
	socket.onmessage = (event) => {
		const message = JSON.parse(event.data);
		pending.get(message.id)?.(message);
		pending.delete(message.id);
	};
	const send = (method, params = {}) =>
		new Promise((resolve, reject) => {
			const id = ++nextId;
			pending.set(id, (message) => (message.error ? reject(new Error(message.error.message)) : resolve(message.result)));
			socket.send(JSON.stringify({ id, method, params }));
		});
	const evaluate = async (expression) =>
		(await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;

	await send('Page.enable');
	await send('Page.navigate', { url: pageUrl });

	// Wait until the page, its fonts and all its images are loaded.
	const ready = `document.readyState === 'complete'
		&& document.querySelector('.print-doc') !== null
		&& [...document.images].every((img) => img.complete && img.naturalWidth > 0)`;
	let loaded = false;
	for (let i = 0; i < 300 && !loaded; i++) {
		await sleep(200);
		loaded = await evaluate(ready).catch(() => false);
	}
	if (!loaded) throw new Error('The print page did not finish loading.');
	await evaluate('document.fonts.ready.then(() => true)');

	const { data } = await send('Page.printToPDF', {
		printBackground: true,
		preferCSSPageSize: true,
		displayHeaderFooter: true,
		headerTemplate: '<div></div>',
		footerTemplate: footer,
	});
	await writeFile(output, Buffer.from(data, 'base64'));
	console.log(`PDF written to ${output}`);
	socket.close();
} finally {
	browser.kill();
	server.close();
	await sleep(500);
	await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 });
}
