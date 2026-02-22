# Deploy to Vercel

This project was converted to a static frontend so it can be hosted on Vercel.

Quick steps:

1. Install Vercel CLI (if not already):

```bash
npm i -g vercel
```

2. Login:

```bash
vercel login
```

3. Test locally:

```bash
vercel dev
```

4. Deploy:

```bash
vercel --prod
```

Notes:
- The static site root is `public/` and includes `index.html` and `static/` assets.
- If you want server-side state later, we can add `api/` serverless functions.
