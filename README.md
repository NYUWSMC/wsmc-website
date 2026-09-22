# Washington Square Management Consulting — website

Static Astro site for WSMC. Deploys to Cloudflare Pages from a fresh clone with no manual configuration beyond connecting the repo.

## Edit content (no local setup)

All page copy and structured data live in Markdown under `src/content/`. Edit in GitHub’s web UI:

1. Open the file you want to change.
2. Edit the frontmatter (the block between `---` lines) and/or the body.
3. Commit to `main`. Cloudflare Pages rebuilds automatically.

| Folder | What it drives |
|---|---|
| `src/content/pages/` | Home, Services, Our Work, Team, Join Us, Contact copy |
| `src/content/services/` | Five practice areas |
| `src/content/clients/` | Client index (verified engagements only) |
| `src/content/cases/` | Case studies (GEMS is the flagship) |
| `src/content/team/` | Consultant slots — `photo` and `name` are optional |

**Add a client:** duplicate any file in `clients/`, change the filename and frontmatter, commit.

**Add a headshot later:** in a team file, add `photo: ../../assets/team/jane.jpg` (or the path you use) once the image exists. Leave `photo` out until then — the layout is designed for both states.

**Never invent** statistics, testimonials, outcomes, or client names. If an outcome is unknown, omit the `outcome` field; the site shows a visible pending state.

## Local development

```bash
npm install
npm run dev
```

```bash
npm run build    # output → dist/
npm run preview  # smoke-test the static build
```

Requires Node 22.12+.

## Cloudflare Pages

| Setting | Value |
|---|---|
| Build command | `npm run build` |
| Output directory | `dist` |
| Node version | `22` |

No adapter and no environment variables are required for the static site.

## Brand marks

SVG lockups live in `public/brand/`. Prefer inlining `abbreviated.svg` / `mark.svg` (`currentColor`) in components. Fixed colourways (`*-purple.svg`, `*-white.svg`, `*-black.svg`) are for `<img>` and favicons.

## Design tokens

`src/styles/tokens.css` — brand purple `#7850AA`, light/dark themes, type scale. Fonts are self-hosted via `@fontsource` (no render-blocking Google Fonts).
