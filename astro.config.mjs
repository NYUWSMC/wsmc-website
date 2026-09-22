// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Static site for Cloudflare Pages. No adapter required.
// Build command: npm run build · Output directory: dist
export default defineConfig({
  site: 'https://wsmc.pages.dev',
  output: 'static',
  trailingSlash: 'always',
  compressHTML: true,
  integrations: [sitemap()],
  build: {
    inlineStylesheets: 'auto',
  },
});
