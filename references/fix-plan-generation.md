# GTM Fix Plan Generation Reference

Guide for building prioritized remediation plans from test results,
scored against GTM best practices.

## Inputs Required

1. **Test results** — `GTM-TAG-TEST-RESULTS.md` (structured pass/fail data)
2. **Container data** — tags, triggers, variables JSON
3. **Audit report** — `GTM-AUDIT-REPORT.md` (if available, for cross-referencing)
4. **Best practices** — `references/google-tag-best-practices.md`

---

## Issue-to-Fix Mapping

### Severity → Priority

| Severity | SLA | Action |
|----------|-----|--------|
| CRITICAL | Fix immediately | Blocks revenue attribution or creates compliance risk |
| HIGH | Fix this sprint | Incorrect data being sent to platforms |
| MEDIUM | Fix next sprint | Suboptimal config, minor data gaps |
| LOW | Backlog | Cosmetic, nice-to-have improvements |

### Source → Phase

| Fix Location | Phase | Who |
|-------------|-------|-----|
| GTM trigger config | Phase 1: Quick Wins | GTM admin (you, now) |
| GTM tag parameters | Phase 1: Quick Wins | GTM admin (you, now) |
| GTM consent settings | Phase 1: Quick Wins | GTM admin (you, now) |
| GTM tag sequencing | Phase 1: Quick Wins | GTM admin (you, now) |
| GTM variable creation/update | Phase 2: Config Fixes | GTM admin |
| GTM new tag creation | Phase 2: Config Fixes | GTM admin |
| Frontend dataLayer | Phase 3: Dev Team | Frontend developer |
| Backend data | Phase 3: Dev Team | Backend developer |
| Investigation needed | Phase 3: Dev Team | Analyst + developer |
| Re-test and monitor | Phase 4: Validation | GTM admin + tester |

---

## Fix Templates by Issue Type

### Duplicate Tag Firing

**Pattern**: Tag fires 2+ times when it should fire once.

```markdown
### Fix #{n} — {tag_name} firing {count}x

- **Root cause**: Tag has multiple triggers that both fire on the same event.
  Triggers: {trigger_1_name} ({id}) + {trigger_2_name} ({id})
- **Fix**: Open tag {tag_id} in GTM. Remove the redundant trigger.
  Keep: {correct_trigger} (fires at {correct_timing})
  Remove: {redundant_trigger}
- **Best practice**: {cite from google-tag-best-practices.md}
- **Validation**: Preview mode — confirm tag fires exactly once per page load
```

### Missing Consent Settings

**Pattern**: Tag has `consentSettings.consentStatus: "notSet"` but should require consent.

```markdown
### Fix #{n} — {tag_name} missing consent gating

- **Root cause**: Tag {tag_id} has no consent settings configured.
  Current: `consentStatus: notSet` — fires regardless of consent state.
- **Fix**: Open tag {tag_id} → Advanced Settings → Consent Settings.
  {For advertising tags}: Require `ad_storage` = granted
  {For analytics tags}: Require `analytics_storage` = granted
  {For personalization tags}: Require `ad_personalization` = granted
- **Best practice**: §4 Consent Mode v2 — all advertising tags must gate on
  ad_storage; analytics tags on analytics_storage.
- **GDPR risk**: In EEA, this tag currently fires without user consent.
- **Validation**: Preview in EU store — tag should NOT fire until consent granted
```

### Duplicate Events from Frontend

**Pattern**: DataLayer pushes the same event multiple times per user action.

```markdown
### Fix #{n} — Duplicate `{event_name}` dataLayer pushes

- **Root cause**: Frontend code pushes `{event_name}` {count} times per
  {user_action}. This is NOT a GTM issue — it's in the site's JavaScript.
- **Impact**: Inflates {vendor} metrics by {count}x. Affects tags:
  {list affected tag names and IDs}
- **Fix (dev team)**: In the frontend code that pushes `{event_name}` to
  dataLayer, add a guard to prevent duplicate pushes:
  - Option A: Use a flag variable (e.g., `window.__{event}_pushed = true`)
  - Option B: Debounce the push function
  - Option C: Check if the event was already pushed for this page view
- **Validation**: Preview mode — confirm exactly ONE `{event_name}` per action
```

### Missing/Undefined Parameter Values

**Pattern**: Tag parameter resolves to undefined, null, or empty string.

```markdown
### Fix #{n} — {tag_name}: `{param_name}` = undefined

- **Root cause**: Variable `{variable_name}` reads from dataLayer path
  `{dataLayer_path}` which is not populated by the frontend at this step.
- **Impact**: {vendor} receives {param_name} = undefined/empty.
  {For conversion value}: Revenue attribution is broken — records $0.
  {For transaction_id}: Deduplication fails — may count duplicate conversions.
  {For items array}: Product-level attribution lost.
- **Fix**:
  {If GTM variable path is wrong}:
    Update variable `{variable_name}` to read from correct path: `{correct_path}`
  {If frontend doesn't push the data}:
    Dev team: Add `{param_name}` to the `{event_name}` dataLayer push
  {If legacy UA path}:
    Create new variable reading GA4 path `{ga4_path}` and update tag to use it
- **Best practice**: {cite relevant section}
- **Validation**: Preview mode → check variable value at `{event_name}` step
```

### Legacy UA DataLayer Variables

**Pattern**: Variable reads from Universal Analytics dataLayer structure that no longer exists.

```markdown
### Fix #{n} — {variable_name} uses legacy UA path

- **Root cause**: Variable reads `{ua_path}` (Universal Analytics format).
  GA4 uses `{ga4_path}` instead. If the site only pushes GA4-format data,
  this variable resolves to `undefined`.
- **Affected tags**: {list tags using this variable}
- **Fix**:
  1. Create new variable `{new_variable_name}` reading from `{ga4_path}`
  2. Update tags {tag_ids} to reference the new variable
  3. Optionally: keep old variable as fallback using Lookup Table
- **Best practice**: §1 Deprecated Tags — migrate from UA to GA4 paths
- **Validation**: Preview mode → verify variable resolves at purchase step
```

### Race Condition / Sequencing Issue

**Pattern**: Dependent tag fires before its setup tag.

```markdown
### Fix #{n} — {dependent_tag} fires before {setup_tag}

- **Root cause**: {dependent_tag} ({dep_id}) fires on the same trigger as
  {setup_tag} ({setup_id}) without sequencing configured.
  Execution order is undefined — sometimes setup fires first, sometimes not.
- **Fix**: Open {dependent_tag} ({dep_id}) → Advanced Settings → Tag Sequencing.
  Set "Setup Tag": {setup_tag} ({setup_id})
  Check "Don't fire {dependent_tag} if {setup_tag} fails"
- **Best practice**: §1 GA4 Configuration — setup tags must fire before dependent tags
- **Validation**: Preview mode → verify {setup_tag} always fires first
```

### Cross-Vendor Value Mismatch

**Pattern**: Different vendors receive different values for the same metric.

```markdown
### Fix #{n} — {metric} mismatch across vendors

- **Discrepancy**:
  | Vendor | Variable | Value |
  |--------|----------|-------|
  {For each vendor: vendor_name | variable_reference | observed_value}

- **Root cause**: {description — usually different variables or rounding}
- **Impact**: Revenue reporting differs across platforms by {amount/percentage}
- **Fix**: Ensure all vendor tags reference the same underlying variable
  for {metric}. Recommended source of truth: `{canonical_variable}`
  Tags to update: {list tag_ids and their current variable references}
- **Validation**: Preview mode → compare values across all vendors at purchase step
```

### Hardcoded Values

**Pattern**: Tag uses hardcoded values where dynamic values are available.

```markdown
### Fix #{n} — {tag_name} hardcodes `{field}` = {hardcoded_value}

- **Root cause**: Custom HTML tag has `{field}: {hardcoded_value}` instead
  of reading from a dataLayer variable.
- **Impact**: {description of impact — e.g., abandoned cart emails show wrong total}
- **Fix**:
  1. Create dataLayer variable `{new_var_name}` reading from `{dataLayer_path}`
  2. In the Custom HTML tag, replace hardcoded `{hardcoded_value}` with
     the GTM variable reference: `{{${new_var_name}}}`
  {If dataLayer doesn't have the value}: Dev team needs to push `{field}`
  in the `{event_name}` dataLayer event.
- **Validation**: Preview mode → verify dynamic value at the relevant step
```

### Enhanced Conversion Variable Mismatch

**Pattern**: Same vendor's tags use different enhanced conversion variables.

```markdown
### Fix #{n} — Google Ads enhanced conversion variable inconsistency

- **Current state**:
  - {tag_1_name} ({id}) uses: `{variable_1}`
  - {tag_2_name} ({id}) uses: `{variable_2}`
- **Fix**: Consolidate to a single approach:
  - **Option A (AUTO)**: Set all tags to use automatic enhanced conversions
    (reads from page). Simplest if user data is in standard HTML fields.
  - **Option B (MANUAL)**: Create one consistent `Enhanced Conversion Data`
    variable and reference it from ALL Google Ads conversion tags.
- **Best practice**: Google recommends consistent EC setup across all conversion tags
- **Validation**: Google Ads → Diagnostics → Enhanced Conversions after deploy
```

---

## Phase Structure Template

```markdown
## Phase 1: GTM-Side Quick Wins

*Can fix now in GTM UI, no dev team needed.*

{Fixes sorted by severity within this phase. Each fix includes:
 - Root cause
 - Step-by-step fix instructions
 - Validation criteria}

## Phase 2: GTM Config Fixes

*Medium effort, GTM only. Variable updates, new tags, parameter changes.*

{Fixes requiring new variables or significant tag changes}

## Phase 3: Frontend/Backend Fixes

*Requires dev team involvement. DataLayer issues, missing events, incorrect values.*

{Fixes grouped by affected system (frontend vs backend).
 For each, include:
 - What the dev team needs to change
 - DataLayer specification (event name, expected fields, data types)
 - Example of correct dataLayer push}

## Phase 4: Validation & Monitoring

*After fixes are applied, re-test and set up monitoring.*

1. Run `/gtm test` to generate new test suite
2. Execute test suite in Chrome with Tag Assistant
3. Run `/gtm results` to ingest new results
4. Compare to previous test run — all CRITICAL/HIGH issues should be resolved
5. Set up ongoing monitoring:
   - GA4 DebugView for event validation
   - Google Ads conversion diagnostics
   - Meta Events Manager test events
   - Weekly Tag Assistant spot-checks
```

---

## Output Format

Write `GTM-FIX-PLAN.md` with this structure:

```markdown
# GTM Fix Plan — {container_name} ({container_id})

**Created**: {date}
**Source**: [GTM-TAG-TEST-RESULTS.md](GTM-TAG-TEST-RESULTS.md)
**Container**: {container_id} ({container_name}) — Live version
**Site**: {site_url}

---

## Issue Inventory

| # | Severity | Issue | Fix Location | Effort |
|---|----------|-------|-------------|--------|
{All issues from test results, sorted by severity}

---

## Phase 1: GTM-Side Quick Wins
{fixes}

## Phase 2: GTM Config Fixes
{fixes}

## Phase 3: Frontend/Backend Fixes
{fixes}

## Phase 4: Validation & Monitoring
{re-test plan}

---

## Implementation Order

Recommended execution sequence (respects dependencies):

1. {fix_n} — {reason it goes first, e.g., "unblocks other fixes"}
2. {fix_n} — {reason}
...

## Risk Assessment

| Fix | Risk if NOT fixed | Risk of fixing incorrectly |
|-----|------------------|--------------------------|
{For each CRITICAL/HIGH fix}
```

---

## Google Best Practice Cross-References

When generating fixes, cite the relevant section from `google-tag-best-practices.md`:

| Issue Category | Best Practice Section |
|---------------|---------------------|
| Duplicate measurement IDs | §1 GA4 Configuration — Single Instance Rule |
| Missing consent settings | §4 Consent Mode v2 — Mandatory Setup |
| Tag sequencing | §1 GA4 Configuration — Single Config Call Rule |
| Custom HTML safety | §1 Custom HTML Safety, §8 CSP |
| Deprecated tag types | §1 Deprecated Tags — Mandatory Migration |
| Event naming | §3 Event Naming Conventions |
| Trigger specificity | §3 Trigger Configuration |
| Consent initialization | §4 Implementation Sequence |
| Performance (doc.write) | §1 Custom HTML Safety |

Always include the specific best practice quote or recommendation in the fix description,
so the user (or dev team) understands WHY the fix is recommended, not just what to do.
