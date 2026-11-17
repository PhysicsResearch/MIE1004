# MIE1004 Lab: Medical Imaging with Python (CT / DICOM)

Instructions and example code for the MIE1004 Data Management Practical.

- **Lab instructions:** on the lab website (link follows once it is published). You download the starting code from the website, and a PDF version of the instructions is available there too.
- **Example code:** in the [`examples/`](examples/) folder of this repository.
- **Solutions of Chapter 3:** each step is a commit on the `lab-code` branch, tagged `step-1` … `step-5`. The website links to them.

## What's in this repository

```
examples/   Python code used in the lab
site/       Source of the lab website (you can ignore this folder)
```

---

## For the instructor: working on the website

The website is an [Astro Starlight](https://starlight.astro.build/) site in `site/`. Pages are Markdown (MDX) files in `site/src/content/docs/`, one file per section. The order of the pages is set in `site/src/outline.mjs`, which is used for both the sidebar and the PDF.

```sh
cd site
npm install      # once
npm run dev      # preview at http://localhost:4321, updates as you edit
npm run pdf      # make the downloadable PDF (needs Chrome or Edge)
```

The PDF is made once, at the end, when the content is final: run `npm run pdf` and commit `site/public/mie1004-lab.pdf`. The "Download as PDF" links only appear on the site once that file exists. If you change a page afterwards, run `npm run pdf` again, because Vercel does not regenerate it.

Pages can show code straight from `examples/`, so the website and the repository never get out of sync:

```mdx
import { Code } from '@astrojs/starlight/components';
import checkSetup from '@examples/check_setup.py?raw';

<Code code={checkSetup} lang="py" title="check_setup.py" />
```

### Vercel settings

- **Root Directory:** `site` (Vercel detects Astro and builds it automatically).
- Leave **Include files outside the Root Directory in the Build Step** enabled, so the site can read `examples/`.
