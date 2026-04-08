# GTM Test Results Parsing Reference

Guide for ingesting and parsing on-page test results from Chrome browser testing
back into structured data for fix plan generation.

## Expected Input Formats

Results come from Claude in Chrome (or a human tester) who executed the test brief.
Accept any of these input methods:

1. **Markdown file path** — User provides path to a results file
2. **Pasted text** — User pastes results directly into the conversation
3. **Structured results** — Results already follow the template from the test brief

---

## Parsing Rules

### Status Keywords

| Status | Patterns to Match | Meaning |
|--------|------------------|---------|
| **PASS** | `PASS`, `Passed`, `Succeeded`, `OK`, checkmark | Tag fired correctly with valid data |
| **FAIL** | `FAIL`, `Failed`, `Error`, `CRITICAL`, cross mark | Tag did not fire, or fired with invalid data |
| **PARTIAL** | `PARTIAL PASS`, `Partial`, `Issues Found`, warning | Tag fired but some data checks failed |
| **SKIP** | `SKIP`, `Skipped`, `N/A`, `Not Tested` | Test was not performed (feature unavailable) |
| **BLOCKED** | `BLOCKED`, `Could not test`, `Blocked by` | Test could not be performed due to a blocker |

### Parsing Order

1. **Behavioral checks first** (B1-B5) — these are container-wide quality signals
2. **Funnel steps** (Step 0-10) — sequential pass/fail per step
3. **Per-tag results** — individual tag status within each step
4. **Parameter validation** — specific field pass/fail within each tag
5. **Cross-vendor consistency** — value comparison across platforms
6. **New issues** — anything not in the known issues list

---

## Result Structure

### Per-Step Result

```yaml
step:
  number: 0-10
  name: "Homepage" | "Collection" | "Product" | etc.
  status: PASS | FAIL | PARTIAL | SKIP
  expected_tags: 11
  verified_tags: 11
  data_verified: true | false
  issues: []
  tags:
    - tag_id: 100
      tag_name: "GA4 - Config - Base"
      status: PASS | FAIL
      fire_count: 1  # how many times it fired (1 = correct for most)
      parameter_results:
        - param: "measurement_id"
          expected: "G-XXXXXXX"
          actual: "G-XXXXXXX"
          status: PASS
        - param: "send_page_view"
          expected: "true"
          actual: "true"
          status: PASS
      notes: ""
```

### Behavioral Check Result

```yaml
behavioral:
  B1_duplicates:
    status: PASS | FAIL
    details: "view_item fires 5+ times per page load"
    affected_tags: [110, 154]
    severity: CRITICAL
  B2_spa:
    status: PASS | FAIL | N/A
    details: ""
  B3_race_conditions:
    status: PASS | FAIL
    details: ""
    sequence_violations: []
  B4_console_errors:
    status: PASS | FAIL
    errors: ["fbq is not defined", ...]
  B5_network:
    status: PASS | FAIL | PARTIAL
    blocked_vendors: ["GA4: 503"]
```

### Cross-Vendor Consistency Result

```yaml
consistency:
  event: "purchase"  # or add_to_cart, begin_checkout, etc.
  fields:
    - field: "order_total"
      values:
        GA4: "$55.97"
        Meta: "$55.97"
        GAds: "$55.97"
        Bing: "undefined"
      match: false
      discrepancy: "Bing reports undefined (legacy UA variable)"
```

---

## Issue Classification

Every failure gets classified:

### Severity Levels

| Severity | Criteria | Examples |
|----------|----------|---------|
| **CRITICAL** | Data loss, revenue attribution broken, compliance violation | Purchase tag not firing, conversion value = 0, no consent gating on ad tags |
| **HIGH** | Incorrect data being sent, duplicate events inflating metrics | Duplicate view_item events, wrong currency, stale transaction_id |
| **MEDIUM** | Suboptimal but not breaking, minor data gaps | Missing item_variant, floating-point precision, hardcoded values |
| **LOW** | Cosmetic, nice-to-have, non-breaking | Missing optional parameters, naming inconsistencies |

### Issue Source Classification

| Source | Description | Who Fixes |
|--------|------------|-----------|
| **GTM-trigger** | Wrong trigger config, duplicate triggers | GTM admin |
| **GTM-tag** | Wrong tag parameters, missing consent, wrong sequencing | GTM admin |
| **GTM-variable** | Variable references wrong dataLayer path, missing variable | GTM admin |
| **Frontend** | DataLayer not pushing correct data, missing events, wrong values | Dev team |
| **Backend** | Server not setting correct values, missing transaction data | Dev team |
| **Infrastructure** | Network blocking, CORS issues, CDN problems | DevOps |
| **Investigation** | Root cause unclear, needs more debugging | Analyst |

---

## Score Calculation

### Tag Coverage Score

```
tag_coverage = (verified_tags / total_active_tags) * 100
```

### Data Quality Score

```
data_quality = (passed_parameter_checks / total_parameter_checks) * 100
```

### Funnel Completion Score

```
funnel_score = (passed_steps / total_steps) * 100
```

### Overall Test Score

```
overall = (tag_coverage * 0.3) + (data_quality * 0.4) + (funnel_score * 0.3)
```

| Score | Grade | Interpretation |
|-------|-------|---------------|
| 90-100 | A | Excellent — minor issues only |
| 75-89 | B | Good — some data gaps to address |
| 60-74 | C | Needs work — significant issues found |
| 40-59 | D | Poor — multiple critical failures |
| 0-39 | F | Critical — fundamental problems |

---

## Output Format

Write `GTM-TAG-TEST-RESULTS.md` with this structure:

```markdown
# GTM Tag Testing Report — {container_name} ({container_id})

**Test Date**: {date}
**Container**: {container_id} ({container_name}) — Live version
**Site**: {site_url}
**Tester**: {tester_info}
**Test Product**: {product_used} (if ecommerce)

---

## Test Score Summary

| Metric | Score |
|--------|-------|
| Tag Coverage | X/Y tags verified (XX%) |
| Data Quality | XX% parameters correct |
| Funnel Completion | X/Y steps passed |
| **Overall Score** | **XX/100 (Grade: X)** |

---

## BEHAVIORAL QUALITY CHECKS

**B1 (Duplicate Events)**: {STATUS} — {details}
**B2 (SPA Navigation)**: {STATUS} — {details}
**B3 (Race Conditions)**: {STATUS} — {details}
**B4 (Console Errors)**: {STATUS} — {details}
**B5 (Network Requests)**: {STATUS} — {details}

---

## FUNNEL STEPS

### Step 0 (Consent Init): {STATUS}
{details per tag}

### Step 1 (Homepage): {STATUS} — Tags: X/Y | Data: Verified/Issues
{details per tag}

{... repeat for each step ...}

---

## CROSS-VENDOR CONSISTENCY

### Purchase
{comparison table}

### Add to Cart
{comparison table if applicable}

---

## ISSUE INVENTORY

| # | Severity | Issue | Source | Affected Tags | Step |
|---|----------|-------|--------|---------------|------|
| 1 | CRITICAL | {description} | {source} | {tag_ids} | {step} |
{... all issues sorted by severity ...}

---

## KNOWN ISSUES CONFIRMED

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| K1 | {from test brief} | Confirmed/Not Confirmed | {details} |

---

## NEW ISSUES DISCOVERED

| # | Severity | Issue | Details |
|---|----------|-------|---------|
| N1 | {severity} | {description} | {details} |
```

---

## Handling Incomplete Results

If the tester couldn't complete the full funnel (e.g., stopped at Step 7):

1. Mark remaining steps as `NOT TESTED`
2. Calculate scores only from tested steps
3. Note the stopping point and reason in the report
4. The fix plan should still generate fixes for confirmed issues

If results are unstructured (free-text notes):

1. Extract tag names and IDs mentioned
2. Map observations to the expected tag list
3. Classify mentions as PASS (positive language) or FAIL (negative language)
4. Flag ambiguous results for user clarification
