# GitHub Copilot – Instruksjoner for release.digdir.no

Dette er et **Hugo-basert statisk nettsted** for release notes fra Digdirs fellesløsninger.

---

## Design system

**Følg alltid Designsystemet fra Digitaliseringsdirektoratet:** https://designsystemet.no/no

Nøkkelsider:
- Oppsett: https://designsystemet.no/no/fundamentals/code/setup
- CSS-bruk: https://designsystemet.no/no/fundamentals/code/css
- Størrelser: https://designsystemet.no/no/fundamentals/code/sizes
- Farger: https://designsystemet.no/no/fundamentals/code/colors
- Komponenter: https://designsystemet.no/no/components

### CDN-oppsett (i `layouts/partials/layout/head.html`)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@digdir/designsystemet-css@1.13.2/dist/src/index.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@digdir/designsystemet-css@1.13.2/dist/theme/designsystemet.css">
<script type="module" src="https://cdn.jsdelivr.net/npm/@digdir/designsystemet-web@1.13.2/dist/esm/index.js"></script>
```
