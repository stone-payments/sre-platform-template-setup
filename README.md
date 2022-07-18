# SRE Platform Template Setup

This action is useful to setup a template repository. Giving a JSON file, the action will replace its values with the ones defined in the JSON.

For example, if we have an YAML file in the repository:

```yaml
repositoryName: sre-platform-template-setup
```

And we use the JSON file below as a input to the action:

```json
{
    "sre-platform": "repository"
}
```

The action will replace the content of the YAML file to:

```yaml
repositoryName: repository-template-setup
```

## Inputs

### `setup-file`

**Required** The path to the JSON file to be used.

## Example usage

The snippet below is a complete example of an repository being set up by this action. The repository is replaced and the result is committed and pushed to the main branch:

```yaml
on: [push]

jobs:
  setup_repository:
    runs-on: ubuntu-latest
    name: Job to set up the repository
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Setup Repository
        uses: stone-payments/sre-platform-template-setup@main
        with:
          setup-file: path-to/file.json

      - name: Commit files
        run: |
          git config --global --add safe.directory "$GITHUB_WORKSPACE"
          git config --local user.email "sreplatform[bot]@stone.com.br"
          git config --local user.name "SRE-Platform[bot]"
          git add .
          git commit -m "[bot] Initial repository setup"

      - name: Push changes to main
        uses: ad-m/github-push-action@v0.6.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: main
```
