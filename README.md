# Release notes
This repo receives deployment details from Argo CD, which is then used to build https://release.digdir.no/

## Getting started
1. Install [Hugo](https://gohugo.io/getting-started/installing/)
2. Clone the repo
3. Run `npm install` to install dependencies

### Development
Run local server: `hugo serve`

Build site with: `hugo`

## Structure

```
content/
├── prod-releases/             # Aggregate page: all prod releases across all products
├── test-releases/             # Aggregate page: all test releases across all products
└── {product}/
    ├── _index.md              # Product section (title, sidebar entry)
    ├── prod-releases/
    │   ├── _index.md
    │   └── {app}-{sha}.md
    └── test-releases/
        ├── _index.md
        └── {app}-{sha}.md
```

The top-level `prod-releases/` and `test-releases/` are aggregate pages that collect all release notes across every product for that environment, displayed on a single paginated page.

Products and environment folders are created automatically by the workflow on the first incoming event. `kt` is mapped to `test`. Products are sorted alphabetically in the sidebar.

Each `{env}-releases/_index.md` is empty but required — Hugo needs it to register the folder as a section, which enables the environment filter buttons (Test / Produksjon) on the product page.

The default display name is the product slug. To use a better name, update `title` in the product's `_index.md`:

```yaml
---
title: ID-porten
menu:
  sidebar:
---
```


