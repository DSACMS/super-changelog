# 📋 Weekly Changelog
**Period**: 2026-07-17 to 2026-07-24

## 📊 Quick Stats
- **Active Repositories**: 22/171
- 📦 **Commits**: 123 | 🔀 **Pull Requests**: 156 | ❗️ **Issues**: 71

## ✅ Added
*New features and additions*

### Esmd-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### archival-identifier
- [Action: Add CRITICALITY_SCORE_THRESHOLD parameter](https://github.com/DSACMS/archival-identifier/pull/19)

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

### codejson-action-e2e
- [Add end-to-end testing workflow, fixtures, and sample source](https://github.com/DSACMS/codejson-action-e2e/pull/1)

### medicare_monthly_enrollment_dashboard
- [Add tier histogram and improve map interactions](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/33)

### power-platform-webres
- [[PPE-60] Changes to add new LCID fields](https://github.com/CMS-Enterprise/power-platform-webres/pull/30)

### super-changelog
- Initial release of super-changelog
- Weekly pipeline (`run_weekly.py`) producing full and condensed summary PRs
- Historical reporting with a custom date range
- Org-agnostic design &mdash; works with any public GitHub organization
- JSON data output for downstream dashboards and reporting
- *...and 1 more*

### ztmf
- [adds guard on what systems a user can be assigned based on their opdivs](https://github.com/CMS-Enterprise/ztmf/pull/460)

### ztmf-ui
- [Add System Delegate user role](https://github.com/CMS-Enterprise/ztmf-ui/pull/595)

## 🪲 Fixed
*Bug fixes and corrections*

### Esmd-fhir-client-python
- **Code Duplication**: Eliminated duplicate files across modules
- **Import Issues**: Fixed circular imports and dependency issues
- **Configuration Loading**: Improved config file discovery and error handling
- **Token Refresh**: Fixed token expiration and refresh logic
- **Package Structure**: Proper Python package hierarchy
- *...and 5 more*

### automated-codejson-generator
- [Change that fixes issue 92](https://github.com/DSACMS/automated-codejson-generator/pull/131)
- [change that introduces fix to issue 107](https://github.com/DSACMS/automated-codejson-generator/pull/130)
- [change that introduces fix to issue 93](https://github.com/DSACMS/automated-codejson-generator/pull/129)

### batcave-workflow-engine
- Viper config key names
- Specified CLI command parameters for custom input and output for easier unit testing in the future

### codejson-action-e2e
- [Fix e2e workflow so validation mode actually runs](https://github.com/DSACMS/codejson-action-e2e/pull/8)

### iv-cbv-payroll
- [Fix ruby dependency updater autofix PR by thawing the bundle](https://github.com/DSACMS/iv-cbv-payroll/pull/1925)

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

### fast-facts-2.0
- [Update code.json](https://github.com/DSACMS/fast-facts-2.0/pull/53)

### iv-cbv-payroll
- [Bump the npm_and_yarn group across 1 directory with 2 updates](https://github.com/DSACMS/iv-cbv-payroll/pull/1927)
- [Update versions from NPM/Python to please Snyk](https://github.com/DSACMS/iv-cbv-payroll/pull/1926)

### medicare_monthly_enrollment_dashboard
- [Updated dashboard layout, 60% map, 40% cards](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/32)

### super-changelog
- [📋 Changelog Summary: 2026-07-10 to 2026-07-17](https://github.com/DSACMS/super-changelog/pull/123)
- [Weekly Changelog Summary: 2026-02-20 to 2026-02-27](https://github.com/DSACMS/super-changelog/pull/122)
- [📋 Changelog Summary: 2026-07-03 to 2026-07-10](https://github.com/DSACMS/super-changelog/pull/120)

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

- **[medicare_monthly_enrollment_dashboard](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard)**: 37 commits, 10 pulls
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 14 commits, 32 pulls, 26 issues
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 12 commits, 27 pulls, 22 issues
- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 12 commits, 23 pulls
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 7 commits, 23 pulls
- **[codejson-action-e2e](https://github.com/DSACMS/codejson-action-e2e)**: 8 commits, 8 pulls
- **[automated-codejson-generator](https://github.com/DSACMS/automated-codejson-generator)**: 7 commits, 7 pulls, 7 issues
- **[power-platform-webres](https://github.com/CMS-Enterprise/power-platform-webres)**: 12 commits, 2 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 1 commits, 11 pulls
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 4 commits, 5 pulls, 1 issues
- *...and 12 more repositories*

---
*🤖 Generated automatically on 2026-07-24T02:39:32.312212+00:00*