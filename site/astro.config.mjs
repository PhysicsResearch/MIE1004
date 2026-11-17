// @ts-check
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { chapters, pdf } from './src/outline.mjs';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'MIE1004 Medical Imaging Lab',
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{ label: 'Overview', link: '/' },
				...chapters.map((chapter) => ({
					label: chapter.label,
					items: [chapter.intro, ...chapter.sections].map((slug) => ({ slug })),
				})),
				...(pdf.ready
					? [{ label: 'Download as PDF', link: pdf.href, attrs: { download: pdf.filename } }]
					: []),
			],
		}),
	],
	vite: {
		resolve: {
			// Lets pages show the students' example code straight from the repo's examples/ folder:
			//   import code from '@examples/check_setup.py?raw';
			alias: { '@examples': fileURLToPath(new URL('../examples', import.meta.url)) },
		},
	},
});
