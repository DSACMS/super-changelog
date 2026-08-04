# 📋 Weekly Changelog
**Period**: 2026-07-10 to 2026-07-17

## 📊 Quick Stats
- **Active Repositories**: 24/171
- 📦 **Commits**: 81 | 🔀 **Pull Requests**: 92 | ❗️ **Issues**: 48

## ✅ Added
*New features and additions*

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

### iv-cbv-payroll
- [FFS-4465: Add configurable household setup to launcher](https://github.com/DSACMS/iv-cbv-payroll/pull/1906)

### medicare_monthly_enrollment_dashboard
- [Add All Areas and county enrollment data grids below the state map](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/25)
- [Adding map cards for front-end and wiring up buttons](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/23)
- [Add pie chart card section with dashboard selection buttons](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/22)

### ospo-guide
- [[DRAFT] Outbound: Create new Generative AI Usage policy](https://github.com/DSACMS/ospo-guide/pull/130)

### super-changelog
- Initial release of super-changelog
- Weekly pipeline (`run_weekly.py`) producing full and condensed summary PRs
- Historical reporting with a custom date range
- Org-agnostic design &mdash; works with any public GitHub organization
- JSON data output for downstream dashboards and reporting
- *...and 1 more*

## 🪲 Fixed
*Bug fixes and corrections*

### batcave-workflow-engine
- Viper config key names
- Specified CLI command parameters for custom input and output for easier unit testing in the future

### ztmf
- [fix(model): make users_fismasystems Save idempotent on duplicate assignment (#429)](https://github.com/CMS-Enterprise/ztmf/pull/438)
- [fix(api): return 400 not 500 for malformed list-endpoint query params (#420)](https://github.com/CMS-Enterprise/ztmf/pull/430)

## 🔧 Changed
*Updates and modifications*

### batcave-workflow-engine
- Upgrade omnibus base image to v1.5.1
- Move existing CLI package to v0
- Task Run pattern
- refactored CLI for readability and maintenance
- upgraded to go 1.22.0
- *...and 19 more*

### easi-app
- [[EASI-5043] Modify System Intake Contract Questions](https://github.com/CMS-Enterprise/easi-app/pull/3501)

## 🗑️ Removed
*Deprecations and removals*

### mint-app
- [[MINT-3797] Remove custom date](https://github.com/CMS-Enterprise/mint-app/pull/2402)

## 🚀 Active Repositories

- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 15 commits, 19 pulls, 1 issues
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 9 commits, 21 pulls, 24 issues
- **[medicare_monthly_enrollment_dashboard](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard)**: 18 commits, 7 pulls, 2 issues
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 3 commits, 21 pulls
- **[testing-repository](https://github.com/DSACMS/testing-repository)**: 13 commits
- **[automated-codejson-generator](https://github.com/DSACMS/automated-codejson-generator)**: 6 commits, 6 pulls, 7 issues
- **[code-book](https://github.com/DSACMS/code-book)**: 8 commits, 2 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 2 commits, 7 pulls
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 3 pulls
- **[ospo-guide](https://github.com/DSACMS/ospo-guide)**: 2 pulls, 3 issues
- *...and 14 more repositories*

---
*🤖 Generated automatically on 2026-07-17T02:37:58.022507+00:00*