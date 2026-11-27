# 📋 Weekly Changelog
**Period**: 2026-11-20 to 2026-11-27

## 📊 Quick Stats
- **Active Repositories**: 19/193
- 📦 **Commits**: 135 | 🔀 **Pull Requests updated**: 98 (59 new, 62 merged) | ❗️ **Issues updated**: 6 (2 new)
## ✅ Added
*New features and additions*

### codejson-schemas
- `identifier` field — a persistent unique ID used to track an asset across renames/migrations. Added to `properties` (right after `name`) and to `required`.
- `downloads` property added to `reuseFrequency.properties`, alongside the existing `forks` and `clones`.
- `feedbackMechanism` (singular)
- `version`, `homepageURL`, `downloadURL`, `disclaimerURL`, `disclaimerText`, `relatedCode`, `reusedCode`, `partners` added as optional fields, taken from original [M-16-21 code.json schema](https://github.com/GSA/code-gov-data/tree/master/schemas)
- `AIUseCaseID` added for assisting with agency collection of their AI Use Case Inventory as part of M-25-21 compliance
- *...and 3 more*

### esmd-ext-fhir-client-python
- **Shared Utilities Package**: Created `esmd_shared` package to eliminate code duplication
- Enhanced `EsmdAuthClient` with token caching, better error handling, and type hints
- Improved `ConfigUtility` with environment variable support and validation
- Advanced `logger` module with file rotation and configurable formatting
- **Comprehensive Documentation**: Complete README.md with installation, usage, and API documentation
- *...and 19 more*

### libyears
- Add an explicit extended SBOM metadata budget for larger local inventories,
- Measure a separate local CycloneDX JSON 1.5 SBOM inventory using supported exact
- Accept explicitly supplied, byte-bound Maven parent/BOM documents through
- Automatically report independent Maven Declared / Observed dependency-age views
- Automatically select qualified current NuGet repository project/lock snapshots
- *...and 10 more*

### mint-app
- [[NOREF] Add Approved ICIP Cypress coverage and TaskCard mutation tests](https://github.com/CMS-Enterprise/mint-app/pull/2676)

## 🪲 Fixed
*Bug fixes and corrections*

### easi-app
- [[NOREF] Fixing TRB assign lead modal submit not firing](https://github.com/CMS-Enterprise/easi-app/pull/3600)

### esmd-ext-fhir-client-python
- **Code Duplication**: Eliminated duplicate files across modules
- **Import Issues**: Fixed circular imports and dependency issues
- **Configuration Loading**: Improved config file discovery and error handling
- **Token Refresh**: Fixed token expiration and refresh logic
- **Package Structure**: Proper Python package hierarchy
- *...and 5 more*

### govcode-index
- [Update Docs and Fix Workflows](https://github.com/GSA-SHARE-IT/govcode-index/pull/15)

### libyears
- Keep every retained unmeasurable Maven Declared occurrence individually visible
- Align ordinary Maven Declared measurements in a module-qualified table with
- Align human-readable dependency tables using the displayed headers and values,

### ztmf
- [fix(misc#415, misc#416): skip fork PRs and publish main's test image in order](https://github.com/CMS-Enterprise/ztmf/pull/652)

### ztmf-ui
- [fix(misc#416): publish ztmf_ui_tag one at a time from main's tip](https://github.com/CMS-Enterprise/ztmf-ui/pull/779)

## 🔧 Changed
*Updates and modifications*

### codejson-schemas
- `$id` updated to `https://gsa-share-it.github.io/code-json-schema.json` (reflecting the repository's move from the `DSACMS` org to `GSA-SHARE-IT`).
- `permissions.usageType`
- enum: M-16-21 exemptions are removed from the schema: `exemptByIPRestriction`, `exemptByAgencySystem`, `exemptByAgencyMission`, `exemptByCIO`, and `exemptByPolicyDate`
- enum: `exemptByDisposableCode`, `exemptByExperimentalCode`, and `exemptByCommercialSoftware` are added, reflecting the SHARE IT Act's exclusions for exploratory/disposable code and commercial/COTS software.
- `identifier` added to `required`.
- *...and 16 more*

### esmd-ext-fhir-client-python
- **Type Hints**: Added comprehensive type annotations throughout shared utilities
- **Error Handling**: Standardized and improved error handling patterns
- **Logging**: Enhanced logging with structured output and rotation
- **Code Structure**: Better separation of concerns and modularity
- **Dependency Security**: Pinned versions to prevent security vulnerabilities
- *...and 7 more*

### fast-facts-2.0
- [Update code.json](https://github.com/DSACMS/fast-facts-2.0/pull/68)

### govcode-index
- [chore: update agency indexes](https://github.com/GSA-SHARE-IT/govcode-index/pull/13)

### libyears
- Keep ordinary directory reports focused on positively relevant ecosystems, with
- Document durable private storage for explicitly supplied approved CA bundles,
- Ordinary NuGet scans can date qualified selected versions against a disclosed
- Measure accepted NuGet project/lock snapshots with explicit package-specific
- Ordinary directory scans automatically attempt bounded NuGet project sources.
- *...and 1 more*

### ztmf
- [chore(ci): bump the github-actions group with 2 updates](https://github.com/CMS-Enterprise/ztmf/pull/653)

## 🗑️ Removed
*Deprecations and removals*

### codejson-schemas
- `categories`, `feedbackMechanisms` (plural, replaced by singular `feedbackMechanism`), `localisation`, `longDescription`, `platforms`, `softwareType` — these agency-extension-style fields were dropped from the generic gov-wide schema.

### ztmf-ui
- [Migrate ScoreDiffModal onto queries and delete its cache](https://github.com/CMS-Enterprise/ztmf-ui/pull/770)

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

### gov-codejson-mcp
- [doc: final README edits](https://github.com/DSACMS/gov-codejson-mcp/pull/27)
- [doc: final-inventory local-client check](https://github.com/DSACMS/gov-codejson-mcp/pull/26)
- [ci: verify Docker build and HTTP health](https://github.com/DSACMS/gov-codejson-mcp/pull/25)

## 🚀 Active Repositories

- **[emmy-app](https://github.com/CMS-Enterprise/emmy-app)**: 24 commits, 31 pulls, 1 issues
- **[gov-codejson-mcp](https://github.com/DSACMS/gov-codejson-mcp)**: 23 commits, 11 pulls
- **[libyears](https://github.com/DSACMS/libyears)**: 27 commits
- **[govcode-index](https://github.com/GSA-SHARE-IT/govcode-index)**: 20 commits, 6 pulls
- **[mint-app](https://github.com/CMS-Enterprise/mint-app)**: 4 commits, 16 pulls
- **[easi-app](https://github.com/CMS-Enterprise/easi-app)**: 6 commits, 12 pulls
- **[indelegible](https://github.com/DSACMS/indelegible)**: 12 commits
- **[ztmf](https://github.com/CMS-Enterprise/ztmf)**: 4 commits, 8 pulls, 1 issues
- **[fast-facts-2.0](https://github.com/DSACMS/fast-facts-2.0)**: 8 commits, 3 pulls, 2 issues
- **[ztmf-ui](https://github.com/CMS-Enterprise/ztmf-ui)**: 3 commits, 6 pulls, 2 issues
- *...and 9 more repositories*

---
*🤖 Generated automatically on 2026-11-27T06:58:46.794413+00:00*