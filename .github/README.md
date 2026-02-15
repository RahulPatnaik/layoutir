# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the layoutir project.

## Workflows

### 1. `ci.yml` - Continuous Integration & Deployment

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Git tags starting with `v*` (e.g., `v1.0.1`)

**Jobs:**

#### Lint Job
- Runs Ruff for code quality checks
- Checks Black formatting
- Continues on error (non-blocking)

#### Build Job
- Tests on Python 3.12 and 3.13
- Builds wheel and source distributions
- Validates package with twine
- Tests installation and imports
- Uploads build artifacts

#### Test Job
- Runs smoke tests on Python 3.12 and 3.13
- Verifies all imports work correctly
- Tests CLI functionality

#### Publish to PyPI (on tags)
- **Triggers**: Only on git tags like `v1.0.0`
- **Requires**: `PYPI_API_TOKEN` secret
- Automatically publishes to PyPI when you create a release tag

#### Publish to TestPyPI (on develop)
- **Triggers**: Only on push to `develop` branch
- **Requires**: `TEST_PYPI_API_TOKEN` secret
- Publishes to TestPyPI for testing

### 2. `release.yml` - GitHub Release Publisher

**Triggers:**
- When a GitHub Release is published

**What it does:**
- Verifies tag version matches `pyproject.toml`
- Builds the package
- Publishes to PyPI
- Uploads wheel and source to GitHub Release assets

## Setup Instructions

### 1. Add PyPI API Token to GitHub Secrets

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token (scope: entire account or project)
3. Go to your GitHub repo → Settings → Secrets and variables → Actions
4. Add new secret:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI token (starts with `pypi-`)

### 2. Add TestPyPI Token (Optional)

For testing on TestPyPI before production:

1. Go to https://test.pypi.org/manage/account/token/
2. Create token
3. Add to GitHub secrets:
   - **Name**: `TEST_PYPI_API_TOKEN`
   - **Value**: Your TestPyPI token

### 3. Publishing a New Release

#### Option A: Via Git Tags (Automated)

```bash
# Update version in pyproject.toml
# Then create and push a tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

The CI workflow will automatically:
- Build the package
- Run tests
- Publish to PyPI

#### Option B: Via GitHub Releases (Recommended)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit and push changes
4. Go to GitHub → Releases → Draft a new release
5. Create tag: `v1.0.1`
6. Auto-generate release notes or write custom notes
7. Click "Publish release"

The `release.yml` workflow will:
- Verify version matches
- Build and publish to PyPI
- Attach wheel and source to release

## Workflow Status

You can view workflow runs at:
`https://github.com/RahulPatnaik/layoutir/actions`

## Dependabot Configuration

The `dependabot.yml` file configures automatic dependency updates:
- GitHub Actions updated weekly
- Python dependencies updated weekly
- Creates pull requests automatically

## Badge for README

Add this to your main `README.md`:

```markdown
[![CI/CD](https://github.com/RahulPatnaik/layoutir/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/RahulPatnaik/layoutir/actions)
[![PyPI version](https://badge.fury.io/py/layoutir.svg)](https://pypi.org/project/layoutir/)
[![Python Versions](https://img.shields.io/pypi/pyversions/layoutir.svg)](https://pypi.org/project/layoutir/)
```

## Troubleshooting

### "Secret PYPI_API_TOKEN not found"
- Make sure you've added the token to GitHub repository secrets
- Check the secret name matches exactly: `PYPI_API_TOKEN`

### "Version mismatch"
- The git tag version must match `pyproject.toml`
- Example: Tag `v1.0.1` requires `version = "1.0.1"` in pyproject.toml

### Build fails on import
- Check all dependencies are listed in `pyproject.toml`
- Verify package structure is correct

## Testing Locally

Before pushing, test the workflow steps locally:

```bash
# Lint
ruff check src/
black --check src/

# Build
python -m build

# Validate
python -m twine check dist/*

# Test install
pip install dist/*.whl
layoutir --help
```
