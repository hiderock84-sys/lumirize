# AGENTS.md

## Cursor Cloud specific instructions

This is a zero-dependency static website (HTML/CSS/vanilla JS) for 株式会社ルミライズ (LUMIRIZE Inc.). There is no `package.json`, no build step, no test framework, and no linter configured.

### Running the dev server

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/` in a browser. The site consists of `index.html`, `styles.css`, `script.js`, and image assets served from the repository root.

### Key notes

- **No build required** — files are served as-is.
- **No automated tests or linting** — manual browser testing is the only verification method.
- **Contact form** uses `mailto:` links (no backend). The submit button opens the user's mail client.
- **Google Fonts** are loaded via CDN; the site falls back to system fonts when offline.
- **GitHub Pages** is the production hosting target.
