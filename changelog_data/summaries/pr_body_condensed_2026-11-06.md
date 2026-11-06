# 📋 Weekly Changelog
**Period**: 2026-10-30 to 2026-11-06

## 📊 Quick Stats
- **Active Repositories**: 65/188
- 📦 **Commits**: 206 | 🔀 **Pull Requests**: 201 | ❗️ **Issues**: 10

## ✅ Added
*New features and additions*

### codejson-schemas
- `identifier` field — a persistent unique ID used to track an asset across renames/migrations. Added to `properties` (right after `name`) and to `required`.
- `downloads` property added to `reuseFrequency.properties`, alongside the existing `forks` and `clones`.
- `feedbackMechanism` (singular)
- `version`, `homepageURL`, `downloadURL`, `disclaimerURL`, `disclaimerText`, `relatedCode`, `reusedCode`, `partners` added as optional fields, taken from original [M-16-21 code.json schema](https://github.com/GSA/code-gov-data/tree/master/schemas)
- `AIUseCaseID` added for assisting with agency collection of their AI Use Case Inventory as part of M-25-21 compliance
- *...and 3 more*

### dsacms.github.io
- [Add external talk link for Open Source Summit Europe 2026](https://github.com/DSACMS/dsacms.github.io/pull/20)

### esmd-ext-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### fdsh-utils
- [experiment in visualizing data for the new hub endpoint flow](https://github.com/DSACMS/fdsh-utils/pull/32)

### libyears
- Measure explicitly selected declared Ruby groups with repeatable
- Measure direct RubyGems dependencies from a bounded root `Gemfile.lock` snapshot,
- Use root Yarn Classic v1 `yarn.lock` evidence to measure direct npm production
- Scan direct npm production dependencies from the root `package.json`, using
- Scan npm and PyPI dependencies together, with repository-wide and
- *...and 2 more*

### metrics-data
- [Add initial README](https://github.com/DSACMS/metrics-data/pull/1)

### ospo-guide
- [Events: Added new event reports section with California DPT OSS 2026 report](https://github.com/DSACMS/ospo-guide/pull/152)
- [Events: Create a new sub-section for event reports](https://github.com/DSACMS/ospo-guide/pull/150)
- [Events: Create a new section for events](https://github.com/DSACMS/ospo-guide/pull/149)

### site
- [Add the SHARE IT Outbound Checklist to the repository](https://github.com/GSA-SHARE-IT/site/pull/13)
- [Docs: Add styling for required vs optional fields](https://github.com/GSA-SHARE-IT/site/pull/12)

### ztmf
- [Add a demo portfolio to the empire seed](https://github.com/CMS-Enterprise/ztmf/pull/632)

## 🪲 Fixed
*Bug fixes and corrections*

### codejson-schemas
- [Docs: Fix headers + information updates](https://github.com/GSA-SHARE-IT/codejson-schemas/pull/9)

### esmd-ext-fhir-client-python
- **Code Duplication**: Eliminated duplicate files across modules
- **Import Issues**: Fixed circular imports and dependency issues
- **Configuration Loading**: Improved config file discovery and error handling
- **Token Refresh**: Fixed token expiration and refresh logic
- **Package Structure**: Proper Python package hierarchy
- *...and 5 more*

### power-platform-webres
- [Update Dev migration fixture data](https://github.com/CMS-Enterprise/power-platform-webres/pull/55)

### super-changelog
- [fix-wrong-json-push](https://github.com/DSACMS/super-changelog/pull/182)

### ztmf-ui
- [fix(#764): compute the FIPS baseline from the system record so it shows for every OpDiv](https://github.com/CMS-Enterprise/ztmf-ui/pull/767)

## 🔧 Changed
*Updates and modifications*

### codejson-schemas
- `$id` updated to `https://gsa-share-it.github.io/code-json-schema.json` (reflecting the repository's move from the `DSACMS` org to `GSA-SHARE-IT`).
- `permissions.usageType`
- enum: M-16-21 exemptions are removed from the schema: `exemptByIPRestriction`, `exemptByAgencySystem`, `exemptByAgencyMission`, `exemptByCIO`, and `exemptByPolicyDate`
- enum: `exemptByDisposableCode`, `exemptByExperimentalCode`, and `exemptByCommercialSoftware` are added, reflecting the SHARE IT Act's exclusions for exploratory/disposable code and commercial/COTS software.
- `identifier` added to `required`.
- *...and 18 more*

### easi-app
- [build(deps): bump the other group across 1 directory with 17 updates](https://github.com/CMS-Enterprise/easi-app/pull/3588)

### esmd-ext-fhir-client-nodeJs
- [Changes ESMD-10742](https://github.com/CMS-Enterprise/esmd-ext-fhir-client-nodeJs/pull/4)

### esmd-ext-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### libyears
- Upgrade JSON output from schema v2 to schema v3. This is an intentional

### mint-app
- [[MINT-3964] Update ICIP HA Link](https://github.com/CMS-Enterprise/mint-app/pull/2645)

### power-platform-webres
- [Update request action commands and ribbon icons](https://github.com/CMS-Enterprise/power-platform-webres/pull/57)

### super-changelog
- [Update code.json](https://github.com/DSACMS/super-changelog/pull/181)
- [📋 Changelog Summary: 2026-10-23 to 2026-10-30](https://github.com/DSACMS/super-changelog/pull/180)

## 🗑️ Removed
*Deprecations and removals*

### codejson-schemas
- `categories`, `feedbackMechanisms` (plural, replaced by singular `feedbackMechanism`), `localisation`, `longDescription`, `platforms`, `softwareType` — these agency-extension-style fields were dropped from the generic gov-wide schema.

## 🔒 Security
*Security improvements*

### esmd-ext-fhir-client-python
- **Dependency Pinning**: All dependencies are pinned to specific versions
- **Environment Variables**: Sensitive configuration moved to environment variables
- **Token Security**: Improved token handling and storage
- **Input Validation**: Better validation of configuration and input data
- **Token Caching**: Reduced authentication overhead with intelligent caching
- *...and 13 more*

### libyears
- Prevent pathological backtracking when classifying npm registry versions,

## 🚀 Active Repositories

- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 32 commits, 48 pulls, 1 issues
- **[libyears](https://github.com/DSACMS/libyears)**: 63 commits
- **[emmy-app](https://github.com/CMS-Enterprise/emmy-app)**: 23 commits, 17 pulls
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 10 commits, 16 pulls, 4 issues
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 7 commits, 18 pulls
- **[codejson-schemas](https://github.com/GSA-SHARE-IT/codejson-schemas)**: 14 commits, 7 pulls
- **[site](https://github.com/GSA-SHARE-IT/site)**: 13 commits, 6 pulls
- **[ospo-guide](https://github.com/DSACMS/ospo-guide)**: 12 commits, 6 pulls, 1 issues
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 4 commits, 8 pulls, 3 issues
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 2 commits, 9 pulls
- *...and 55 more repositories*

---
*🤖 Generated automatically on 2026-11-06T05:24:15.457811+00:00*