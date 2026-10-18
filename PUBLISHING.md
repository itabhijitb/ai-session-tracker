# Publishing Guide

This guide explains how to publish ai-session-tracker to PyPI and GitHub.

## Initial Setup

### 1. GitHub Repository Setup

1. Create a new repository on GitHub: `ai-session-tracker`
2. Initialize the repository with your existing code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/itabhijitb/ai-session-tracker.git
   git push -u origin main
   ```

3. Enable GitHub Actions:
   - Go to repository Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

4. Configure GitHub secrets for PyPI publishing (see below)

### 2. PyPI Setup

1. Create a PyPI account at https://pypi.org/account/register/

2. Enable 2-Factor Authentication (required for publishing)

3. Create an API token:
   - Go to https://pypi.org/manage/account/token/
   - Create a new token
   - Name it "ai-session-tracker" or similar
   - Scope: "Entire account" (recommended) or specific to the project
   - **Save the token securely** - you won't see it again

4. Configure GitHub for Trusted Publishing:
   - Go to your PyPI account settings
   - Navigate to "Publishing" → "Add a new publisher"
   - Select "GitHub" as the publisher
   - Select your GitHub repository: `itabhijitb/ai-session-tracker`
   - Configure the workflow name: `publish.yml`
   - Set the environment name: `pypi`
   - Save the configuration

   This is the **recommended** method as it doesn't require storing tokens in GitHub secrets.

### Alternative: Traditional Publishing with API Token

If you prefer the traditional method (not recommended):

1. Go to your GitHub repository Settings → Secrets and variables → Actions
2. Add a new secret named `PYPI_API_TOKEN`
3. Paste your PyPI API token as the value
4. Update `.github/workflows/publish.yml` to use the token instead of trusted publishing

## Publishing a Release

### 1. Update Version

Edit `pyproject.toml` and update the version:

```toml
[project]
name = "ai-session-tracker"
version = "0.1.0"  # Update this
```

### 2. Update CHANGELOG.md

Add an entry for the new version:

```markdown
## [0.1.0] - 2026-10-18

### Added
- New feature description
```

### 3. Commit and Tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

### 4. Automatic Publishing

When you push a tag that matches `v*.*.*`:
- GitHub Actions will automatically build the package
- It will publish to PyPI using trusted publishing
- It will create a GitHub release with the built artifacts

### 5. Verify

Check PyPI to ensure the package was published:
- Visit https://pypi.org/project/ai-session-tracker/
- Verify the version and files

## Local Testing Before Publishing

### Test Build

```bash
python -m build
twine check dist/*
```

### Test on TestPyPI

1. Create a TestPyPI account: https://test.pypi.org/account/register/

2. Upload to TestPyPI:
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. Install from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ ai-session-tracker
   ```

4. Test the installation:
   ```bash
   ais --help
   ais status
   ```

5. If everything works, proceed with production PyPI publishing

## GitHub Environment Setup

The `publish.yml` workflow uses a GitHub environment named `pypi`:

1. Go to repository Settings → Environments
2. Create a new environment named `pypi`
3. Configure protection rules (optional but recommended):
   - Required reviewers: 1
   - Wait timer: 0 minutes
   - Deployment branches: only `main`

This adds an extra layer of security before publishing.

## Post-Publishing Checklist

- [ ] Verify package on PyPI
- [ ] Test installation from PyPI in a clean environment
- [ ] Update README badges if needed
- [ ] Announce release (Twitter, blog, etc.)
- [ ] Close related GitHub issues
- [ ] Update version to next development version (e.g., 0.2.0-dev)

## Troubleshooting

### Publishing Fails

1. Check the GitHub Actions logs
2. Verify PyPI trusted publishing is configured correctly
3. Ensure the tag format matches `v*.*.*`
4. Check that the version in `pyproject.toml` matches the tag

### Build Fails

1. Run `python -m build` locally to reproduce
2. Check `twine check dist/*` output
3. Verify `pyproject.toml` syntax
4. Ensure all dependencies are properly specified

### Trusted Publishing Issues

1. Verify the publisher is configured in PyPI
2. Check the repository name matches exactly
3. Ensure the workflow name matches
4. Verify the environment name matches

## Maintenance

### Regular Tasks

- Update dependencies regularly ( Dependabot will help)
- Review and merge Dependabot PRs
- Keep CHANGELOG.md updated
- Monitor for security vulnerabilities

### Dependency Updates

When updating dependencies:

1. Test locally first
2. Run all tests
3. Update `pyproject.toml`
4. Commit and push
5. Dependabot will handle most updates automatically

## Support

For issues with publishing:
- Check GitHub Actions logs
- Review PyPI documentation: https://packaging.python.org/
- Open an issue on GitHub
