import { defineCollection, reference, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Content model for annual handoff.
 * To add an item: copy any Markdown file in the same folder, edit frontmatter, commit.
 * Schemas stay shallow on purpose — editors work in GitHub’s web UI.
 */

const clients = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/clients' }),
  schema: z.object({
    name: z.string(),
    sector: z.string(),
    year: z.coerce.string().describe('Engagement year or span, e.g. 2025–26'),
    summary: z.string().describe('One sentence a buyer can verify if asked'),
    featured: z.boolean().default(false),
    engagementType: z
      .enum(['paid', 'pro-bono', 'unpaid', 'workshop'])
      .describe('How the engagement was contracted'),
  }),
});

const services = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/services' }),
  schema: z.object({
    title: z.string(),
    summary: z.string().describe('Problem framing — what the buyer is stuck on'),
    detail: z.string().describe('How we approach it, in plain language'),
    order: z.number().int().positive(),
  }),
});

const team = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/team' }),
  schema: ({ image }) =>
    z.object({
      // Names are pending for the current cohort — leave blank/null until confirmed.
      name: z.string().optional(),
      initials: z
        .string()
        .max(3)
        .describe('Shown when name or photo is missing'),
      priorRole: z.string(),
      priorOrg: z.string(),
      classYear: z.string().describe('e.g. MA 2027'),
      projectRole: z.string().describe('e.g. Consultant, Project Lead'),
      photo: image().optional(),
      order: z.number().int().positive().default(99),
      published: z.boolean().default(true),
    }),
});

const cases = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/cases' }),
  schema: z.object({
    title: z.string(),
    client: reference('clients'),
    summary: z.string(),
    duration: z.string(),
    teamSize: z.string().describe('e.g. 2–6 consultants by phase'),
    featured: z.boolean().default(false),
    figures: z
      .array(
        z.object({
          label: z.string(),
          value: z.string(),
        }),
      )
      .default([]),
    phases: z
      .array(
        z.object({
          name: z.string(),
          detail: z.string(),
        }),
      )
      .default([]),
    methods: z
      .array(z.string())
      .describe('Methodological vocabulary — keep the technical terms'),
    // Omit or leave empty until a real outcome exists. UI shows a pending state.
    outcome: z.string().optional(),
    testimonial: z
      .object({
        quote: z.string(),
        attribution: z.string().optional(),
        pending: z.boolean().default(true),
      })
      .optional(),
  }),
});

/** Page-level copy — headlines, CTAs, body. Never hardcode this in components. */
const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    eyebrow: z.string().optional(),
    headline: z.string().optional(),
    lede: z.string().optional(),
    primaryCta: z
      .object({
        label: z.string(),
        href: z.string(),
      })
      .optional(),
    secondaryCta: z
      .object({
        label: z.string(),
        href: z.string(),
      })
      .optional(),
  }),
});

export const collections = { clients, services, team, cases, pages };
