# 📋 Weekly Changelog
**Period**: 2026-07-03 to 2026-07-10

## 📊 Quick Stats
- **Active Repositories**: 24/168
- 📦 **Commits**: 60 | 🔀 **Pull Requests**: 112 | ❗️ **Issues**: 57

## ✅ Added
*New features and additions*

### Esmd-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### batcave-tf-gatus
- Changelog
- pre-commit

### batcave-workflow-engine
- GitHub action auth support
- settings package for config and metaconfig values
- settings package marshalling / unmarshalling
- Grype Image Scan Task
- Task pattern instead of pipeline pattern for simplicity Note: currently the new experimental is behind a build flag
- *...and 50 more*

### emmy-agent-marketplace
- [Add CMS Hybrid Cloud Splunk plugin](https://github.com/DSACMS/emmy-agent-marketplace/pull/16)

### mint-app
- [[MINT-3788] add mock data](https://github.com/CMS-Enterprise/mint-app/pull/2390)
- [[MINT-3778] Add custom date page](https://github.com/CMS-Enterprise/mint-app/pull/2387)
- [[MINT-3791]/additional ctat date tracking](https://github.com/CMS-Enterprise/mint-app/pull/2385)

### ospo-guide
- [[DRAFT] Outbound: Create new Generative AI Usage policy](https://github.com/DSACMS/ospo-guide/pull/130)
- [DSAC Engineering Handbook: Add LaunchDarkly and edit access request instructions](https://github.com/DSACMS/ospo-guide/pull/128)

### repo-scaffolder
- [Adding AI Usage Section to CONTRIBUTING.md](https://github.com/DSACMS/repo-scaffolder/pull/394)

### super-changelog
- Initial release of super-changelog
- Weekly pipeline (`run_weekly.py`) producing full and condensed summary PRs
- Historical reporting with a custom date range
- Org-agnostic design &mdash; works with any public GitHub organization
- JSON data output for downstream dashboards and reporting
- *...and 1 more*

## 🪲 Fixed
*Bug fixes and corrections*

### Esmd-fhir-client-python
- **Code Duplication**: Eliminated duplicate files across modules
- **Import Issues**: Fixed circular imports and dependency issues
- **Configuration Loading**: Improved config file discovery and error handling
- **Token Refresh**: Fixed token expiration and refresh logic
- **Package Structure**: Proper Python package hierarchy
- *...and 5 more*

### batcave-workflow-engine
- Viper config key names
- Specified CLI command parameters for custom input and output for easier unit testing in the future

### ospo-guide
- [Minor doc fixes](https://github.com/DSACMS/ospo-guide/pull/125)

## 🔧 Changed
*Updates and modifications*

### Esmd-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### batcave-workflow-engine
- Upgrade omnibus base image to v1.5.1
- Move existing CLI package to v0
- Task Run pattern
- refactored CLI for readability and maintenance
- upgraded to go 1.22.0
- *...and 19 more*

### easi-app
- [[NOREF] update syntax to correctly silence the no operation provided message](https://github.com/CMS-Enterprise/easi-app/pull/3516)

### super-changelog
- [📋 Changelog Summary: 2026-06-26 to 2026-07-03](https://github.com/DSACMS/super-changelog/pull/114)
- [Weekly Changelog Summary: 2025-10-24 to 2025-10-31](https://github.com/DSACMS/super-changelog/pull/113)

### ztmf
- [Identifiable system questionnaire updates](https://github.com/CMS-Enterprise/ztmf/pull/407)

## 🔒 Security
*Security improvements*

### Esmd-fhir-client-python
- **Dependency Pinning**: All dependencies are pinned to specific versions
- **Environment Variables**: Sensitive configuration moved to environment variables
- **Token Security**: Improved token handling and storage
- **Input Validation**: Better validation of configuration and input data
- **Token Caching**: Reduced authentication overhead with intelligent caching
- *...and 13 more*

## 🚀 Active Repositories

- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 13 commits, 26 pulls, 24 issues
- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 14 commits, 20 pulls
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 8 commits, 20 pulls, 18 issues
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 4 commits, 19 pulls
- **[ospo-guide](https://github.com/DSACMS/ospo-guide)**: 8 commits, 4 pulls, 1 issues
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 3 commits, 5 pulls, 1 issues
- **[emmy-agent-marketplace](https://github.com/DSACMS/emmy-agent-marketplace)**: 2 commits, 4 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 1 commits, 4 pulls
- **[testing-repository](https://github.com/DSACMS/testing-repository)**: 3 commits, 2 issues
- **[automated-codejson-generator](https://github.com/DSACMS/automated-codejson-generator)**: 3 pulls, 2 issues
- *...and 14 more repositories*

---
*🤖 Generated automatically on 2026-07-10T03:19:37.673070+00:00*