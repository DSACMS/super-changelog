# 📋 Weekly Changelog
**Period**: 2026-11-13 to 2026-11-20

## 📊 Quick Stats
- **Active Repositories**: 24/192
- 📦 **Commits**: 240 | 🔀 **Pull Requests updated**: 191 (123 new, 97 merged) | ❗️ **Issues updated**: 22 (3 new)
## ✅ Added
*New features and additions*

### .github
- [Add docs/org-profile](https://github.com/GSA-SHARE-IT/.github/pull/1)

### codejson-schemas
- `identifier` field — a persistent unique ID used to track an asset across renames/migrations. Added to `properties` (right after `name`) and to `required`.
- `downloads` property added to `reuseFrequency.properties`, alongside the existing `forks` and `clones`.
- `feedbackMechanism` (singular)
- `version`, `homepageURL`, `downloadURL`, `disclaimerURL`, `disclaimerText`, `relatedCode`, `reusedCode`, `partners` added as optional fields, taken from original [M-16-21 code.json schema](https://github.com/GSA/code-gov-data/tree/master/schemas)
- `AIUseCaseID` added for assisting with agency collection of their AI Use Case Inventory as part of M-25-21 compliance
- *...and 4 more*

### emmy-app
- [Add seasonal worker guidance accordion (FFS-4969)](https://github.com/CMS-Enterprise/emmy-app/pull/116)

### esmd-ext-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### govcode-index
- [Dataset: Add CMS-specific schema normalization and validation rules](https://github.com/GSA-SHARE-IT/govcode-index/pull/11)

### libyears
- Accept explicitly supplied, byte-bound Maven parent/BOM documents through
- Automatically report independent Maven Declared / Observed dependency-age views
- Automatically select qualified current NuGet repository project/lock snapshots
- Accept an explicitly bound resolved NuGet snapshot as a population fallback when
- Accept explicit per-project supplier witnesses with repeatable
- *...and 8 more*

### mint-app
- [[NOREF] Add Add Final ICIP document type](https://github.com/CMS-Enterprise/mint-app/pull/2670)

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
- Keep every retained unmeasurable Maven Declared occurrence individually visible
- Align ordinary Maven Declared measurements in a module-qualified table with
- Align human-readable dependency tables using the displayed headers and values,

### super-changelog
- [Fix stale merged prs](https://github.com/DSACMS/super-changelog/pull/186)
- [Fix full summary filename mismatch and stale fallback](https://github.com/DSACMS/super-changelog/pull/185)

### ztmf
- [fix(misc#350): narrow the GitHub OIDC deploy role trust per account](https://github.com/CMS-Enterprise/ztmf/pull/651)
- [fix(misc#421): stop the pr-env reaper when an AWS list call fails](https://github.com/CMS-Enterprise/ztmf/pull/648)

### ztmf-ui
- [feat: frostfall v1.6.1 keyboard audit, with the focus fixes it found](https://github.com/CMS-Enterprise/ztmf-ui/pull/776)
- [fix(misc#439): label each radar tooltip row with its own data call](https://github.com/CMS-Enterprise/ztmf-ui/pull/775)

## 🔧 Changed
*Updates and modifications*

### .github
- [Revise README for improved clarity and consistency](https://github.com/GSA-SHARE-IT/.github/pull/2)

### codejson-schemas
- `$id` updated to `https://gsa-share-it.github.io/code-json-schema.json` (reflecting the repository's move from the `DSACMS` org to `GSA-SHARE-IT`).
- `permissions.usageType`
- enum: M-16-21 exemptions are removed from the schema: `exemptByIPRestriction`, `exemptByAgencySystem`, `exemptByAgencyMission`, `exemptByCIO`, and `exemptByPolicyDate`
- enum: `exemptByDisposableCode`, `exemptByExperimentalCode`, and `exemptByCommercialSoftware` are added, reflecting the SHARE IT Act's exclusions for exploratory/disposable code and commercial/COTS software.
- `identifier` added to `required`.
- *...and 16 more*

### emmy-app
- [FFS-5103 Update Education Review page to surface enrollment certification status and self-attested labels](https://github.com/CMS-Enterprise/emmy-app/pull/117)

### esmd-ext-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### libyears
- Keep ordinary directory reports focused on positively relevant ecosystems, with
- Document durable private storage for explicitly supplied approved CA bundles,
- Ordinary NuGet scans can date qualified selected versions against a disclosed
- Measure accepted NuGet project/lock snapshots with explicit package-specific
- Ordinary directory scans automatically attempt bounded NuGet project sources.
- *...and 1 more*

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

## 📚 Documentation
*Documentation updates*

### ztmf
- [Apply artifact/documentation in the documentation request form](https://github.com/CMS-Enterprise/ztmf/pull/649)

### ztmf-ui
- [Apply artifact/documentation in the documentation request form](https://github.com/CMS-Enterprise/ztmf-ui/pull/778)

## 🚀 Active Repositories

- **[emmy-app](https://github.com/CMS-Enterprise/emmy-app)**: 41 commits, 63 pulls, 1 issues
- **[govcode-index](https://github.com/GSA-SHARE-IT/govcode-index)**: 63 commits, 11 pulls
- **[gov-codejson-mcp](https://github.com/DSACMS/gov-codejson-mcp)**: 54 commits, 16 pulls
- **[libyears](https://github.com/DSACMS/libyears)**: 42 commits
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 8 commits, 22 pulls, 10 issues
- **[iv-cbv-payroll](https://github.com/DSACMS/iv-cbv-payroll)**: 2 commits, 26 pulls, 1 issues
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 9 commits, 18 pulls, 10 issues
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 3 commits, 15 pulls
- **[super-changelog](https://github.com/DSACMS/super-changelog)**: 2 commits, 5 pulls
- **[.github](https://github.com/GSA-SHARE-IT/.github)**: 3 commits, 2 pulls
- *...and 14 more repositories*

---
*🤖 Generated automatically on 2026-11-20T05:56:23.843211+00:00*