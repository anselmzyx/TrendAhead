# TrendAhead

**See what's gaining momentum before everyone else does.**

TrendAhead detects topics that are beginning to gain unusual attention online,
before they become obviously mainstream. It measures the *rate of change* of
public attention (not just absolute popularity) and ranks emerging topics with
a 0–100 **TrendAhead Score**.

> Status: early development (Phase 1 — project foundation).

## How to run it locally

1. Open Terminal and go to the project folder:
   ```bash
   cd ~/Desktop/TrendAhead
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
3. Open http://localhost:3000 in your browser.
   ("localhost" means "this computer" — the site runs only on your machine.)
4. Stop the server with `Ctrl+C` in the terminal.

## Tech stack

- [Next.js](https://nextjs.org) 16 (React framework for the website)
- TypeScript (JavaScript with type checking)
- Tailwind CSS (styling)

## Project documentation

- `PROJECT_PLAN.md` — roadmap and current phase
- `DECISIONS.md` — significant technical/product decisions and why
- `ERROR_LOG.md` — meaningful problems we hit and how we fixed them

More sections (architecture, data pipeline, scoring, deployment) will be added
as those parts are built.
