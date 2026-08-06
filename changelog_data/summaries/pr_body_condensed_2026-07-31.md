# 📋 Weekly Changelog
**Period**: 2026-07-24 to 2026-07-31

## 📊 Quick Stats
- **Active Repositories**: 23/172
- 📦 **Commits**: 79 | 🔀 **Pull Requests**: 195 | ❗️ **Issues**: 133

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
- [FFS-4495: Add one more URL to Accenture iframe](https://github.com/DSACMS/iv-cbv-payroll/pull/1943)
- [FFS-4496: Add logging to JsonTransmitter and HttpPdfTransmitter](https://github.com/DSACMS/iv-cbv-payroll/pull/1940)

### medicare_monthly_enrollment_dashboard
- [Added accessible design to visuals, added mobile bar graph and grid to trend card](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard/pull/40)

### mint-app
- [[MINT-3804] Part 1 - Add CTAT feature flag](https://github.com/CMS-Enterprise/mint-app/pull/2427)

### ospo-guide
- [Adding repodiving.md to inbound section of OSPO-guide](https://github.com/DSACMS/ospo-guide/pull/134)

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
- [fix(auth): scope the session cookie to the issuing host](https://github.com/CMS-Enterprise/ztmf/pull/497)
- [fix(infra): route alarm notifications to the shared ISPG inbox](https://github.com/CMS-Enterprise/ztmf/pull/496)

### ztmf-ui
- [fix(auth): sync logout across tabs and stop the sign-in redirect loop (#606)](https://github.com/CMS-Enterprise/ztmf-ui/pull/645)

## 🔧 Changed
*Updates and modifications*

### batcave-workflow-engine
- Upgrade omnibus base image to v1.5.1
- Move existing CLI package to v0
- Task Run pattern
- refactored CLI for readability and maintenance
- upgraded to go 1.22.0
- *...and 19 more*

### mint-app
- [Build(deps): bump the other group with 6 updates](https://github.com/CMS-Enterprise/mint-app/pull/2425)

### repodive-tools
- [Updating repodive-tools README.md and CONTRIBUTING.md to match the OSPO guides improved docs!](https://github.com/DSACMS/repodive-tools/pull/23)

### super-changelog
- [removed logic to only append repos with activity to changelog](https://github.com/DSACMS/super-changelog/pull/126)
- [Weekly Changelog Summary: 2026-05-28 to 2026-06-04](https://github.com/DSACMS/super-changelog/pull/124)

## 🗑️ Removed
*Deprecations and removals*

### easi-app
- [remove unused script](https://github.com/CMS-Enterprise/easi-app/pull/3530)
- [removed references to cedar proxy](https://github.com/CMS-Enterprise/easi-app/pull/3527)

## 🚀 Active Repositories

- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 89 pulls, 77 issues
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 9 commits, 31 pulls, 34 issues
- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 14 commits, 18 pulls
- **[medicare_monthly_enrollment_dashboard](https://github.com/DSACMS/medicare_monthly_enrollment_dashboard)**: 21 commits, 8 pulls
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 5 commits, 21 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 9 commits, 11 pulls
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 2 commits, 6 pulls, 1 issues
- **[code-book](https://github.com/DSACMS/code-book)**: 7 commits
- **[ospo-guide](https://github.com/DSACMS/ospo-guide)**: 5 commits, 1 pulls, 3 issues
- **[automated-codejson-generator](https://github.com/DSACMS/automated-codejson-generator)**: 5 pulls, 5 issues
- *...and 13 more repositories*

---
*🤖 Generated automatically on 2026-07-31T14:57:02.885134+00:00*