// @ts-check
import { defineConfig } from 'astro/config';

// Static site for Cloudflare Pages. No adapter required.
// Build command: npm run build · Output directory: dist
export default defineConfig({
  site: 'https://wsmc.pages.dev',
  output: 'static',
  compressHTML: true,
  build: {
    inlineStylesheets: 'auto',
  },
});
