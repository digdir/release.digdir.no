# Release notes
This repo receives deployment details from Argo CD, which is then used to build https://release.digdir.no/

## Getting started
1. Install [Hugo](https://gohugo.io/getting-started/installing/)
2. Clone the repo
3. Run `npm install` to install dependencies

### Development
Run local server: `hugo serve`

Build site with: `hugo`

## Automatic release merging

New release PRs receive the `release-notes-automerge` label. Approval and squash/automerge each get up to five attempts, ten seconds apart, to recover from temporary GitHub errors and concurrent merges. Branch protection remains enforced.

The **Retry release automerge** workflow follows up labelled, open release PRs every 15 minutes (GitHub may delay scheduled runs), and can also be started manually. Only same-repository PRs created by `github-actions[bot]`, targeting `main`, with a `release-notes-` branch are eligible. PRs with active automerge are left to GitHub; persistent failures fail the workflow and retain the label for later follow-up. The label remains on merged PRs as a record of intent.

Existing unlabelled release PRs are not changed. After reviewing them, add `release-notes-automerge` to eligible PRs to opt them into follow-up.

Run the offline regression tests with `python3 .github/scripts/test_release_automerge.py` (requires Python 3 and `jq`).

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

