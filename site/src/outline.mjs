// The order of the lab pages. The sidebar and the PDF are both built from this list,
// so a new page only needs to be added here (and as a file in src/content/docs/).
//
// Each chapter has an intro page (`intro`) followed by its sections.
// Page ids are file paths inside src/content/docs/ without the extension,
// and an `index.mdx` file is just its folder name (e.g. `data/index.mdx` -> 'data').

import { existsSync } from 'node:fs';
import { join } from 'node:path';

export const labTitle = 'MIE1004 Lab Session – Medical Imaging with Python (CT / DICOM)';

// Address of the published website (Vercel). Used for links in the PDF.
export const siteUrl = 'https://mie-1004.vercel.app';

export const chapters = [
	{
		label: '1. Working environment',
		intro: 'environment',
		sections: [
			'environment/python',
			'environment/virtual-environments',
			'environment/fair-data',
			'environment/vs-code',
		],
	},
	{
		label: '2. Getting the data',
		intro: 'data',
		sections: [
			'data/select-patients',
			'data/manifest',
			'data/retrieve',
			'data/licence',
			'data/explore',
		],
	},
	{
		label: '3. Processing the data',
		intro: 'code',
		sections: [
			'code/start',
			'code/more-metadata',
			'code/faster',
			'code/all-patients',
			'code/plot',
			'code/report',
		],
	},
	{
		label: '4. Extra challenge',
		intro: 'extra',
		sections: [],
	},
];

// GitHub repository. The solutions of Chapter 3 are tagged step-0 ... step-5 (branch lab-code).
export const repo = 'https://github.com/PhysicsResearch/MIE1004';

// Side pages: help pages that are not in the sidebar. Each is linked from its parent page
// and printed right after it in the PDF.
export const sidePages = {
	'environment/vs-code': ['environment/conda-in-vs-code'],
};

// The PDF version of the lab. Make it once, at the end, with `npm run pdf` and commit it.
// The "Download as PDF" links only appear once the file exists in public/.
const pdfFile = 'mie1004-lab.pdf';
export const pdf = {
	href: `/${pdfFile}`,
	filename: 'MIE1004-lab-medical-imaging.pdf',
	ready: existsSync(join(process.cwd(), 'public', pdfFile)),
};
