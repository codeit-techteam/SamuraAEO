# Samura Consulting Group website, version 8

Static site. No build step. Open `index.html` in a browser or deploy the folder as-is.

## Files
- `index.html`: homepage (all sections, form, country picker, animations)
- `case-studies.html`: case studies page
- `assets/`: logo and leadership photos
- `flags/`: SVG flags used by the phone country picker (from the flag-icons project, MIT licence)
- `robots.txt`, `sitemap.xml`, `llms.txt`: crawler and AI-engine files
- Structured data (Organization, Offers, FAQPage) is inline in `index.html`'s head

## Deploy on Vercel (static)
1. Put these files at the root of the repo (or set the Vercel project's root directory to this folder).
2. Framework preset: Other. No build command. Output directory: `.`
3. Add a `vercel.json` with clean URLs so `/case-studies` works without `.html`:
   { "cleanUrls": true, "trailingSlash": false }
4. Point the domain as before.

Alternatively, drop the markup into the existing Next.js app: the `<style>` block becomes a global CSS file, each `<section>` becomes a component, and the inline `<script>` goes in a `useEffect`.

## Things to wire up before go-live
- Contact form: currently opens a pre-filled WhatsApp chat and shows a thank-you. Add a POST to a serverless function that emails sufia.aram@samuraconsulting.com (Resend or SendGrid) and keep the WhatsApp open.
- Footer subscribe form: currently shows a thank-you only. Add a POST to Brevo (or Mailchimp) list API.
- Fonts load from Google Fonts (Manrope, Source Sans 3). Self-host if preferred.
- Insights cards link to `#` until articles exist. Privacy and Terms links point to `#`.
- Replace `assets/logo.png` with an SVG logo if available for sharper rendering.
