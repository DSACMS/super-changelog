# 📋 Weekly Changelog
**Period**: 2026-11-06 to 2026-11-13

## 📊 Quick Stats
- **Active Repositories**: 20/189
- 📦 **Commits**: 207 | 🔀 **Pull Requests**: 143 | ❗️ **Issues**: 5

## ✅ Added
*New features and additions*

### codejson-schemas
- `identifier` field — a persistent unique ID used to track an asset across renames/migrations. Added to `properties` (right after `name`) and to `required`.
- `downloads` property added to `reuseFrequency.properties`, alongside the existing `forks` and `clones`.
- `feedbackMechanism` (singular)
- `version`, `homepageURL`, `downloadURL`, `disclaimerURL`, `disclaimerText`, `relatedCode`, `reusedCode`, `partners` added as optional fields, taken from original [M-16-21 code.json schema](https://github.com/GSA/code-gov-data/tree/master/schemas)
- `AIUseCaseID` added for assisting with agency collection of their AI Use Case Inventory as part of M-25-21 compliance
- *...and 5 more*

### esmd-ext-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### libyears
- Automatically report independent Maven Declared / Observed dependency-age views
- Automatically select qualified current NuGet repository project/lock snapshots
- Accept an explicitly bound resolved NuGet snapshot as a population fallback when
- Accept explicit per-project supplier witnesses with repeatable
- Measure explicitly selected NuGet project snapshots with `--nuget-project`
- *...and 7 more*

### site
- [Add screenshots to forms](https://github.com/GSA-SHARE-IT/site/pull/20)
- [ Search: Add search.gov to GSA SHARE IT Act site](https://github.com/GSA-SHARE-IT/site/pull/18)

### ztmf-ui
- [feat(misc#311): add Help page and sign-in help](https://github.com/CMS-Enterprise/ztmf-ui/pull/769)

## 🪲 Fixed
*Bug fixes and corrections*

### esmd-ext-fhir-client-python
- **Code Duplication**: Eliminated duplicate files across modules
- **Import Issues**: Fixed circular imports and dependency issues
- **Configuration Loading**: Improved config file discovery and error handling
- **Token Refresh**: Fixed token expiration and refresh logic
- **Package Structure**: Proper Python package hierarchy
- *...and 5 more*

### libyears
- Align human-readable dependency tables using the displayed headers and values,

### ospo-guide
- [Resources: Fixes for the Packaging Guides](https://github.com/DSACMS/ospo-guide/pull/153)

## 🔧 Changed
*Updates and modifications*

### codejson-schemas
- `$id` updated to `https://gsa-share-it.github.io/code-json-schema.json` (reflecting the repository's move from the `DSACMS` org to `GSA-SHARE-IT`).
- `permissions.usageType`
- enum: M-16-21 exemptions are removed from the schema: `exemptByIPRestriction`, `exemptByAgencySystem`, `exemptByAgencyMission`, `exemptByCIO`, and `exemptByPolicyDate`
- enum: `exemptByDisposableCode`, `exemptByExperimentalCode`, and `exemptByCommercialSoftware` are added, reflecting the SHARE IT Act's exclusions for exploratory/disposable code and commercial/COTS software.
- `identifier` added to `required`.
- *...and 17 more*

### esmd-ext-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### iv-cbv-payroll
- [FFS-5024: Update JSON for the NSC partially self-attested flow](https://github.com/DSACMS/iv-cbv-payroll/pull/2331)

### libyears
- Ordinary NuGet scans can date qualified selected versions against a disclosed
- Measure accepted NuGet project/lock snapshots with explicit package-specific
- Ordinary directory scans automatically attempt bounded NuGet project sources.
- Upgrade JSON output from schema v2 to schema v3. This is an intentional

### mint-app
- [[MINT-3982] Update UI For Create Model Plan](https://github.com/CMS-Enterprise/mint-app/pull/2661)

### site
- [Sitemap: Update collections so sitemap.xml is correctly generated](https://github.com/GSA-SHARE-IT/site/pull/19)

### super-changelog
- [📋 Changelog Summary: 2026-10-30 to 2026-11-06](https://github.com/DSACMS/super-changelog/pull/184)
- [Weekly Changelog Summary: 2026-07-31 to 2026-08-07](https://github.com/DSACMS/super-changelog/pull/183)

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

- **[libyears](https://github.com/DSACMS/libyears)**: 100 commits
- **[emmy-app](https://github.com/CMS-Enterprise/emmy-app)**: 35 commits, 33 pulls
- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 25 commits, 37 pulls
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 7 commits, 21 pulls
- **[site](https://github.com/GSA-SHARE-IT/site)**: 20 commits, 7 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 6 commits, 10 pulls
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 3 commits, 9 pulls, 1 issues
- **[codejson-schemas](https://github.com/GSA-SHARE-IT/codejson-schemas)**: 4 commits, 4 pulls
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 2 commits, 5 pulls
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 7 pulls, 4 issues
- *...and 10 more repositories*

---
*🤖 Generated automatically on 2026-11-13T05:22:06.353008+00:00*