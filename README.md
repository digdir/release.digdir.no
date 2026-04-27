# Release notes
This repo receives deployment details from Argo CD, which is then used to build https://release.digdir.no/

## Getting started
1. Install [Hugo](https://gohugo.io/getting-started/installing/)
2. Clone the repo
3. Run `git submodule update --init --recursive` to fetch the theme
3. Run `npm install` to install dependencies
4. Run `hugo serve` to start the local server

### Development
Run local server: `hugo serve`

Build site with: `hugo`

## Adding products manually

Create a new product folder:

```bash
mkdir -p content/my-product
```

Then add the file with a title and menu entry:

```yaml
---
title: My Product Name
menu:
  sidebar:
    weight: 10
---
```

The `weight` parameter controls the order in the sidebar (lower numbers appear first). The product display name comes from the `title` field.

## Test releases

To add test releases for a product:

1. Create a `test-releases` folder in your product directory:
   ```bash
   mkdir -p content/my-product/test-releases
   ```

2. Create an empty `_index.md` file in the test-releases folder:
   ```bash
   echo "---
   ---" > content/my-product/test-releases/_index.md
   ```

3. Add your test release files (e.g., `my-test-release.md`) to this folder

The test releases will automatically appear as a "Test" button next to "Produksjon" on the product pages. Produksjon remains the default active tab.
