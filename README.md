# Personal Homepage (Sphinx + GitHub Pages)

This repository contains a documentation-style personal homepage built with Sphinx and deployed with GitHub Pages.

## Features

- Resume-style homepage and profile sections
- Blog/log pages with automatic sidebar navigation
- Mixed source formats (`.md` + `.rst`)
- Theme support with dark/light mode (`pydata-sphinx-theme`)
- Local build + preview workflow driven by `Makefile`
- Automatic deployment via GitHub Actions (`.github/workflows/build.yml`)

## Build and Run Locally

This project now uses `Makefile` targets as the default build method.

1. Create a virtual environment:

   ```bash
   make venv
   ```

2. Install dependencies:

   ```bash
   make install
   ```

3. Build the site:

   ```bash
   make html
   ```

4. Open `docs/_build/html/index.html` in your browser.

### Optional: serve locally

To build and start a local preview server:

```bash
make serve
```

Then visit `http://127.0.0.1:8000`.

## Common Commands

- `make help` - show all available targets
- `make clean` - remove generated build output
- `make rebuild` - clean and rebuild HTML output

## Editing Content

- Home/resume content: `docs/index.rst`
- Logs index: `docs/logs/index.md`
- Individual logs: `docs/logs/log-*.md` or `docs/logs/log-*.rst`
- Papers section: `docs/papers/`
- Site configuration: `docs/conf.py`

## Deploy to GitHub Pages

1. Push the repository to GitHub.
2. In repository settings, enable **Pages** and set source to **GitHub Actions**.
3. Push to `main` (or `master`) to trigger automatic build and deploy.
