---
name: gtm
description: >
  Google Tag Manager container audit and tag configuration analysis.
  Connects to GTM API v2 to pull tags, triggers, variables, and consent
  settings. Evaluates 53 checks across tag health, trigger quality,
  consent/privacy, tag conflicts and interference, performance impact,
  data layer usage, and container organization. Detects misconfigured
  tags, duplicate tracking pixels, competing config tags, consent state
  conflicts, race conditions, orphaned triggers, and naming violations.
  Generates on-page test suites from container data for Chrome browser
  testing, ingests test results, and builds fix plans against best
  practices. Use when user says "GTM", "Tag Manager", "GTM audit",
  "tag audit", "container audit", "GTM analysis", "tag configuration",
  "GTM health", "tag health check", "analyze my tags", "tag conflicts",
  "tags interfering", "test my tags", "GTM test", "tag testing", or
  "test suite".
argument-hint: "audit | connect | test | results | fix | tags | triggers | variables | consent | conflicts | report"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Agent
---

# GTM — Google Tag Manager Container Audit & Analysis

Connects to Google Tag Manager API v2, pulls full container configuration,
and performs a 53-check audit across 7 categories.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/gtm audit` | Full container audit with all 53 checks |
| `/gtm connect` | Set up GTM API authentication and test connection |
| `/gtm tags` | Tag-focused analysis (types, firing, consent, duplicates) |
| `/gtm triggers` | Trigger quality analysis (orphans, overlap, specificity) |
| `/gtm variables` | Variable audit (unused, custom JS risk, data layer) |
| `/gtm consent` | Consent Mode and privacy compliance deep dive |
| `/gtm conflicts` | Tag conflict and interference analysis (duplicates, race conditions, consent mismatches) |
| `/gtm report` | Generate report from previously fetched data |
| `/gtm test` | Generate on-page test suite from container data for Chrome browser testing |
| `/gtm results` | Ingest Chrome test results and parse pass/fail per tag and step |
| `/gtm fix` | Build a fix plan from test results, prioritized by severity and effort |

## Process

### First-Time Setup (`/gtm connect`)

1. Check if GTM API credentials exist at `~/.config/gtm-audit/credentials.json`
2. If not, guide the user through:
   a. Create a Google Cloud project (or use existing)
   b. Enable the Tag Manager API v2
   c. Create OAuth 2.0 credentials (Desktop app type)
   d. Download `credentials.json` and place at `~/.config/gtm-audit/credentials.json`
   e. Grant the OAuth client or service account email access in GTM (Admin > User Management)
3. Run `scripts/fetch_gtm.py --auth-only` to complete OAuth flow and cache token
4. Verify connection by listing accessible accounts

### Full Audit (`/gtm audit`)

1. Run `scripts/fetch_gtm.py` to fetch container data → outputs JSON to `/tmp/gtm-audit/`
2. Read `references/gtm-audit.md` for full 53-check audit checklist
3. Read `references/scoring-system.md` for weighted scoring
4. Read `references/google-tag-best-practices.md` for official Google guidance per check
5. Parse fetched JSON data (tags, triggers, variables, built-in variables)
6. Evaluate all applicable checks as PASS, WARNING, or FAIL — cite Google best practice where relevant
7. Calculate GTM Health Score (0-100)
8. Generate `GTM-AUDIT-REPORT.md` with findings, Google doc citations, and action plan

### On-Page Test Suite (`/gtm test`)

Generates a comprehensive browser testing document from container data. Designed to be
handed to Claude in Chrome (or any browser-based tester) for live on-page validation.

1. **Load container data** — Read tags, triggers, variables from `/tmp/gtm-audit/` or project `backups/` dir
2. Read `references/test-generation.md` for tag-type templates and test structure
3. **Classify every active tag** into test groups:
   - **Always-Fire**: Tags on All Pages / Consent Init / Container Loaded triggers
   - **Ecommerce Funnel**: Tags on ecommerce dataLayer events (view_item_list → purchase)
   - **Interaction**: Click, scroll, visibility, form, custom event tags
   - **Consent**: Consent Default + Update tags
   - **Optional/Conditional**: Newsletter, search, wishlist, etc.
4. **For each tag**, generate test checks using tag-type templates:
   - Layer 1: Did it fire? (Tag Assistant status, correct trigger, fire count)
   - Layer 2: Is data correct? (Parameter validation per tag type with expected values)
   - Layer 3: Page behavior (No duplicates, correct sequencing, no console errors)
5. **Build funnel steps** — Map ecommerce events to a step-by-step user journey
6. **Add behavioral quality checks** — Duplicate detection, race conditions, network validation
7. **Add cross-vendor consistency checks** — Compare values across GA4/Meta/GAds/Bing/etc.
8. **Add gate rules** — Stop-and-document rules at critical funnel steps
9. **Generate known issues list** — From audit findings or tag config anomalies
10. **Output**: Write `GTM-TAG-TEST-BRIEF.md` to project directory

The test brief is self-contained — a tester (human or Claude in Chrome) can execute it
without access to the GTM container or API.

**Splitting**: If the container has >25 active tags, split into multiple test suite files
grouped by vendor/platform (e.g., `TEST-SUITE-1-GOOGLE.md`, `TEST-SUITE-2-META.md`).

### Ingest Test Results (`/gtm results`)

Parses browser test results back into structured findings for fix plan generation.

1. **Read results file** — User provides path or pastes results (expect markdown with PASS/FAIL per step)
2. Read `references/results-parsing.md` for parsing rules
3. **Parse each funnel step** — Extract status (PASS / FAIL / PARTIAL / SKIP) per step
4. **Parse each tag result** — Extract per-tag status, parameter failures, data mismatches
5. **Parse behavioral checks** — B1-B5 status with failure details
6. **Parse cross-vendor consistency** — Identify value mismatches across platforms
7. **Extract new issues** — Issues not in the known issues list from the test brief
8. **Calculate test score**:
   - Tags verified: X/Y active tags
   - Data quality: X% parameters validated correctly
   - Known issues confirmed: X/Y
   - New issues found: count
9. **Output**: Write `GTM-TAG-TEST-RESULTS.md` (structured) to project directory
10. **Store parsed data** for fix plan generation — tag failures, parameter issues, behavioral problems

### Build Fix Plan (`/gtm fix`)

Generates a prioritized remediation plan from test results, scored against GTM best practices.

1. **Load inputs**:
   - Parsed test results (`GTM-TAG-TEST-RESULTS.md`)
   - Container data (tags, triggers, variables JSON)
   - Audit report if available (`GTM-AUDIT-REPORT.md`)
2. Read `references/fix-plan-generation.md` for fix templates and prioritization rules
3. Read `references/google-tag-best-practices.md` for official Google guidance
4. **Classify every issue** by:
   - **Severity**: CRITICAL (data loss/compliance) → HIGH (incorrect data) → MEDIUM (suboptimal) → LOW (cosmetic)
   - **Fix location**: GTM-only (can fix now) vs Frontend/backend (needs dev team) vs Investigation (needs more data)
   - **Effort**: Low (< 30min) → Medium (1-4h) → High (> 4h)
5. **Generate fix phases**:
   - Phase 1: GTM Quick Wins — Fix in GTM UI, no dev needed (duplicate triggers, consent gaps, sequencing)
   - Phase 2: GTM Config Fixes — Variable updates, tag parameter changes, new tags needed
   - Phase 3: Frontend/Backend Fixes — DataLayer issues, missing events, incorrect values (needs dev team)
   - Phase 4: Validation & Monitoring — Re-test instructions, ongoing monitoring setup
6. **For each fix**, include:
   - Root cause analysis
   - Specific steps to implement
   - Google best practice reference (from `references/google-tag-best-practices.md`)
   - Validation criteria (how to confirm the fix works)
7. **Output**: Write `GTM-FIX-PLAN.md` to project directory

### End-to-End Workflow

```
/gtm audit → /gtm test → [Chrome testing] → /gtm results → /gtm fix
     ↓              ↓                              ↓              ↓
 AUDIT-REPORT  TEST-BRIEF.md              TEST-RESULTS.md   FIX-PLAN.md
```

The workflow is designed for a feedback loop:
- After fixes are applied, run `/gtm test` again to generate a new test suite
- Re-test in Chrome, ingest results, compare to previous run
- Repeat until all CRITICAL/HIGH issues are resolved

### Data Flow

```
GTM API v2 → fetch_gtm.py → /tmp/gtm-audit/*.json → Analysis → Report
```

Files written by fetch script:
- `/tmp/gtm-audit/accounts.json` — Accessible accounts
- `/tmp/gtm-audit/containers.json` — Containers in selected account
- `/tmp/gtm-audit/tags.json` — All tags with full configuration
- `/tmp/gtm-audit/triggers.json` — All triggers with filters
- `/tmp/gtm-audit/variables.json` — All variables (custom + built-in)
- `/tmp/gtm-audit/metadata.json` — Container metadata, fetch timestamp

## What to Analyze

### 1. Tag Health (20% weight)
- All tags have descriptive names (not "Untitled Tag", "Copy of...")
- No paused tags that should be removed (stale > 90 days)
- Tags have appropriate firing options (once per event vs once per page)
- GA4 Configuration tag exists and fires on All Pages
- No duplicate measurement IDs across GA4 tags
- Conversion tags use event parameters correctly
- Custom HTML tags reviewed for errors and safety
- Tag sequencing configured where dependencies exist (setup/cleanup)
- No deprecated tag types (Classic GA, legacy Floodlight templates)

### 2. Tag Conflicts & Interference (15% weight)
- No duplicate tracking pixels sending to the same destination ID
- No competing GA4 config tags with different measurement IDs on same pages
- No conflicting conversion tags (same conversionId + conversionLabel)
- Same-trigger tags have sequencing (no undefined execution order race conditions)
- No consent state conflicts within same vendor (one tag requires consent, another doesn't)
- No overlapping event tags sending duplicate events to same destination
- Blocking triggers don't completely negate firing triggers (dead tags)
- Custom HTML tags don't write to same global variables or dataLayer keys
- Pixel IDs consistent across base pixel and event tags for same vendor
- Active tags don't duplicate paused tags (shadow copies)
- No server-side + client-side double-fire without deduplication
- Outputs an interference matrix showing tag-to-tag conflict pairs

### 3. Trigger Quality (15% weight)
- No orphaned triggers (not referenced by any tag)
- Triggers are specific (avoid overly broad "All Pages" for conversion tags)
- Custom event triggers use consistent naming (snake_case or camelCase, not mixed)
- Click/form triggers use appropriate selectors (IDs > classes > CSS selectors)
- Trigger groups used for multi-condition requirements
- No conflicting triggers on the same tag (firing + exception overlap)
- Scroll/visibility triggers have reasonable thresholds
- Timer triggers have stop conditions

### 4. Consent & Privacy (20% weight)
- Consent Mode v2 implemented (consent_default + consent_update)
- Tags have consent settings configured (ad_storage, analytics_storage, etc.)
- No tags firing before consent is granted (unless exempt)
- Consent initialization trigger present
- Privacy-sensitive tags (Meta Pixel, Google Ads, etc.) require ad_storage consent
- Analytics tags have analytics_storage consent configured
- Built-in consent overview reviewed (no "Not Set" on advertising tags)

### 5. Performance & Loading (10% weight)
- Tag firing priority configured for critical tags
- Custom HTML tags are not loading large external scripts synchronously
- document.write not used in any Custom HTML tag
- Image pixel tags use the built-in Custom Image tag (not Custom HTML)
- Tags don't fire more often than needed (e.g., scroll listeners on every page)
- Container total tag count reasonable (< 50 for small sites, < 100 for enterprise)
- No tags with "fire on all pages" that should be scoped
- Sequencing used instead of race conditions

### 6. Data Layer & Variables (10% weight)
- Data layer variables reference correct key paths
- Custom JavaScript variables don't contain long/complex logic
- Lookup/RegEx tables used instead of repeated Custom JS
- Constant variables used for IDs/keys (not hardcoded in tags)
- No unused variables (defined but not referenced)
- Variable naming follows consistent convention
- Built-in variables enabled only as needed

### 7. Container Organization (10% weight)
- Folders/tags organized by vendor or function
- Naming convention consistent (e.g., "GA4 - Event - purchase")
- Container has meaningful notes on recent versions
- Workspace management: no stale workspaces with uncommitted changes
- Tag, trigger, variable counts proportional to site complexity
- Container published recently (not > 90 days stale)

## Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| Tag count (small site) | < 30 | 30-50 | > 50 |
| Tag count (enterprise) | < 60 | 60-100 | > 100 |
| Orphaned triggers | 0 | 1-3 | > 3 |
| Unused variables | 0 | 1-5 | > 5 |
| Tags without consent | 0 | 1-3 | > 3 |
| Paused tags (> 90d) | 0 | 1-2 | > 2 |
| Custom HTML tags | < 5 | 5-10 | > 10 |
| Duplicate measurement IDs | 0 | — | ≥ 1 |
| Tag conflict pairs | 0 | 1-2 | > 2 |
| Consent state mismatches | 0 | 1 | > 1 |
| Unsequenced shared triggers | 0 | 1-3 | > 3 |

## Output

### GTM Health Score

```
GTM Health Score: XX/100 (Grade: X)

Tag Health:           XX/100  ████████░░  (20%)
Tag Conflicts:        XX/100  ██████░░░░  (15%)
Trigger Quality:      XX/100  ██████████  (15%)
Consent & Privacy:    XX/100  ███████░░░  (20%)
Performance:          XX/100  █████░░░░░  (10%)
Data Layer & Vars:    XX/100  ████████░░  (10%)
Organization:         XX/100  ██████████  (10%)
```

### Deliverables
- `GTM-AUDIT-REPORT.md` — Full 53-check findings with pass/warning/fail
- **Interference matrix** — Tag-to-tag conflict pairs with severity and type
- Tag inventory matrix (name, type, trigger, consent status, firing option)
- Vendor grouping analysis (all tags grouped by platform/vendor)
- Orphaned trigger/variable list
- Consent gap analysis (tag × consent type matrix)
- Quick Wins sorted by impact
- Recommended tag sequencing diagram (if applicable)

## Reference Files

Load on-demand as needed — do NOT load all at startup.

**Path resolution:** All references at `~/.claude/skills/gtm/references/`.

- `references/gtm-audit.md` — Full 53-check audit checklist with severity ratings
- `references/scoring-system.md` — Weighted scoring algorithm and grading thresholds
- `references/google-tag-best-practices.md` — Official Google documentation best practices mapped to audit checks (21 sources)
- `references/test-generation.md` — Tag-type test templates, funnel step mapping, behavioral checks, and test brief structure
- `references/results-parsing.md` — Results format specification, parsing rules, score calculation, and failure classification
- `references/fix-plan-generation.md` — Fix templates by issue type, prioritization matrix, phase structure, and validation criteria

## Scripts

- `scripts/fetch_gtm.py` — GTM API v2 data fetcher (OAuth 2.0, outputs JSON)
- `scripts/requirements.txt` — Python dependencies

## Dependencies

Python 3.9+ with:
- `google-api-python-client` — GTM API v2 client
- `google-auth-httplib2` — HTTP transport
- `google-auth-oauthlib` — OAuth 2.0 flow
