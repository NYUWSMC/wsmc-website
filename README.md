# Washington Square Management Consulting — website

Static Astro site for WSMC. Deploys to Cloudflare Pages from a fresh clone with no manual configuration beyond connecting the repo.

## Pages

| Route | Purpose |
|---|---|
| `/` | Identity, audience routing, services preview, selected work |
| `/services/` | Five practice areas as problems we solve |
| `/work/` | Client index |
| `/team/` | Oversight / confidentiality + cohort (photos optional) |
| `/join/` | First-year recruiting, honest time commitment |
| `/contact/` | Email CTA |

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
| `src/content/cases/` | Case studies (add when disclosure is cleared) |
| `src/content/team/` | Consultant slots — `photo` and `name` are optional |

**Add a client:** duplicate any file in `clients/`, change the filename and frontmatter, commit.

**Add a headshot later:** in a team file, add `photo: ./headshots/jane.jpg` once the image exists beside the markdown (or under `src/assets/`). Leave `photo` out until then — monograms fill the same square.

**Enable the contact form:** set `formEndpoint` in `src/content/pages/contact.md` to a Formspree or Worker URL.

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

## Brand & design

- SVG lockups in `public/brand/` (inline via `Logo.astro` with `currentColor`)
- Tokens in `src/styles/tokens.css` — brand purple `#7850AA`, light/dark
- Fonts self-hosted: Source Serif 4, IBM Plex Sans, IBM Plex Mono
