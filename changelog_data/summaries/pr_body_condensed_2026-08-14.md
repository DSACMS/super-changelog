# 📋 Weekly Changelog
**Period**: 2026-08-07 to 2026-08-14

## 📊 Quick Stats
- **Active Repositories**: 35/175
- 📦 **Commits**: 139 | 🔀 **Pull Requests**: 199 | ❗️ **Issues**: 29

## ✅ Added
*New features and additions*

### Esmd-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### decks
- [Add cif26 demo day deck](https://github.com/DSACMS/decks/pull/20)

### fdsh-utils
- [Add Security Schemes](https://github.com/DSACMS/fdsh-utils/pull/6)

### iv-delivery
- [Metadata: Add code.json](https://github.com/DSACMS/iv-delivery/pull/2)

### iv-doc-uploader
- [LICENSE: Add CC0 1.0 Universal license](https://github.com/DSACMS/iv-doc-uploader/pull/39)

### repo-scaffolder
- [ Add GitHub repository topic prompts and automatic topic assignment`](https://github.com/DSACMS/repo-scaffolder/pull/395)

### year-in-review
- [Fixed redundant API calls and added timeout to get_stats_contributors](https://github.com/DSACMS/year-in-review/pull/4)

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
- [introduced change that fixes issue #91](https://github.com/DSACMS/automated-codejson-generator/pull/128)

### iv-cbv-payroll
- [FFS-4670: Fix Emmy Launcher to be enabled in CMS Cloud non-production environments](https://github.com/DSACMS/iv-cbv-payroll/pull/1977)
- [Fix Solid Queue CMS deploy config](https://github.com/DSACMS/iv-cbv-payroll/pull/1975)

### mint-app
- [[NOREF] Fix incorrect translation path](https://github.com/CMS-Enterprise/mint-app/pull/2455)

### ztmf
- [fix(scores): tag the server-owned fields on FindScoresInput as non-bindable](https://github.com/CMS-Enterprise/ztmf/pull/552)
- [fix: declare CloudFront price class and assert it](https://github.com/CMS-Enterprise/ztmf/pull/551)

### ztmf-ui
- [Fix questionnaire opening a different data call than the row's Data Call column](https://github.com/CMS-Enterprise/ztmf-ui/pull/695)

## 🔧 Changed
*Updates and modifications*

### Esmd-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### automated-codejson-generator
- [docs(contributor): contributors readme action update](https://github.com/DSACMS/automated-codejson-generator/pull/137)

### code-book
- [Update code.json](https://github.com/DSACMS/code-book/pull/4)

### medicare_monthly_enrollment_dashboard
- [Update code.json](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/44)
- [readme contrinbuting community md files updated](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/43)

### repo-scaffolder
- [Update code.json](https://github.com/DSACMS/repo-scaffolder/pull/397)

### year-in-review
- [Updated metrics with a rerun of the full year 08-07-25 to 08-07-2026](https://github.com/DSACMS/year-in-review/pull/5)
- [Dsacms/zion/get contributors update](https://github.com/DSACMS/year-in-review/pull/3)

## 🗑️ Removed
*Deprecations and removals*

### ztmf-ui
- [chore(deps): phase 1 — security floors, react-router unpin, and unreferenced dependency removal](https://github.com/CMS-Enterprise/ztmf-ui/pull/700)
- [chore(deps): phase 0 — version floors, unused dependency removal, and Storybook teardown](https://github.com/CMS-Enterprise/ztmf-ui/pull/696)

## 🔒 Security
*Security improvements*

### Esmd-fhir-client-python
- **Dependency Pinning**: All dependencies are pinned to specific versions
- **Environment Variables**: Sensitive configuration moved to environment variables
- **Token Security**: Improved token handling and storage
- **Input Validation**: Better validation of configuration and input data
- **Token Caching**: Reduced authentication overhead with intelligent caching
- *...and 13 more*

## 📚 Documentation
*Documentation updates*

### fdsh-utils
- [[codex] Document specs project READMEs](https://github.com/DSACMS/fdsh-utils/pull/4)

### iv-cbv-payroll
- [FFS-4555: Send activity documents over HTTP](https://github.com/DSACMS/iv-cbv-payroll/pull/1976)

## 🚀 Active Repositories

- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 28 commits, 34 pulls, 1 issues
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 6 commits, 47 pulls, 4 issues
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 13 commits, 24 pulls
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 6 commits, 29 pulls, 6 issues
- **[fdsh-utils](https://github.com/DSACMS/fdsh-utils)**: 25 commits, 6 pulls
- **[medicare_monthly_enrollment_dashboard](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard)**: 12 commits, 4 pulls
- **[codejson-action-e2e](https://github.com/DSACMS/codejson-action-e2e)**: 10 commits, 5 pulls
- **[repo-scaffolder](https://github.com/DSACMS/repo-scaffolder)**: 2 commits, 10 pulls, 2 issues
- **[year-in-review](https://github.com/DSACMS/year-in-review)**: 8 commits, 3 pulls
- **[automated-codejson-generator](https://github.com/DSACMS/automated-codejson-generator)**: 2 commits, 7 pulls, 3 issues
- *...and 25 more repositories*

---
*🤖 Generated automatically on 2026-08-14T01:54:53.299048+00:00*