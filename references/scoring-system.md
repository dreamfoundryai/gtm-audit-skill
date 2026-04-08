# GTM Container Audit Scoring System

## Weighted Scoring Algorithm

```
S_total = Σ(C_pass × W_sev × W_cat) / Σ(C_total × W_sev × W_cat) × 100
```

- `C_pass` = check passed (1) or failed (0); WARNING = 0.5
- `W_sev` = severity multiplier of the individual check
- `W_cat` = category weight
- Result: 0-100 Health Score

## Severity Multipliers

| Severity | Multiplier | Criteria |
|----------|-----------|----------|
| Critical | 5.0 | Data integrity or privacy risk. Remediation urgent. |
| High | 3.0 | Significant configuration issue. Fix within 7 days. |
| Medium | 1.5 | Optimization opportunity. Fix within 30 days. |
| Low | 0.5 | Best practice, minor impact. Nice to have. |

## Scoring Per Check Item

| Result | Points Earned |
|--------|--------------|
| PASS | Full severity × category weight |
| WARNING | 50% of full points |
| FAIL | 0 points |
| N/A | Excluded from total possible |

## Category Weights

| Category | Weight | Rationale |
|----------|--------|-----------|
| Tag Health | 20% | Core functionality — misconfigured tags break tracking |
| Tag Conflicts & Interference | 15% | Active tags causing issues with each other — duplicate tracking, race conditions, consent mismatches |
| Trigger Quality | 15% | Triggers control when tags fire; bad triggers = bad data |
| Consent & Privacy | 20% | Legal compliance; Consent Mode v2 required for EU/EEA |
| Performance & Loading | 10% | Tags directly impact page load speed and Core Web Vitals |
| Data Layer & Variables | 10% | Supporting infrastructure for tag configuration |
| Container Organization | 10% | Maintainability and team collaboration |

## Grading Thresholds

| Grade | Score | Label | Action Required |
|-------|-------|-------|-----------------|
| A | 90-100 | Excellent | Minor optimizations only |
| B | 75-89 | Good | Some improvement opportunities |
| C | 60-74 | Needs Improvement | Notable issues need attention |
| D | 40-59 | Poor | Significant problems present |
| F | <40 | Critical | Urgent intervention required |

## Quick Wins Logic

```
IF severity == "Critical" OR severity == "High"
AND estimated_remediation_time < 15 minutes
THEN flag as "Quick Win"
PRIORITY: Quick Wins sorted by (severity × estimated_impact) DESC
```

Quick Win examples:
- Configure consent settings on ad tags (Critical, 5 min per tag)
- Remove orphaned triggers (Medium, 2 min each)
- Enable built-in Consent Overview (High, 5 min)
- Add tag sequencing for GA4 config → event tags (High, 5 min)
- Switch Custom HTML image pixels to Custom Image type (Medium, 3 min)
- Delete stale paused tags (Low, 2 min each)
- Add folder organization (Low, 10 min)

## Tag Type Risk Weighting

Certain tag types carry higher inherent risk and should be weighted accordingly
in the analysis:

| Tag Type | Risk Level | Reason |
|----------|-----------|--------|
| Custom HTML | High | Arbitrary code execution, XSS risk, performance impact |
| Custom Image | Low | Simple pixel fire, minimal risk |
| GA4 Config (googtag) | Medium | Foundation tag — misconfiguration breaks all GA4 tracking |
| GA4 Event (gaawc) | Medium | Data quality depends on correct parameters |
| Google Ads Conversion | High | Revenue attribution — errors directly impact ROAS reporting |
| Meta Pixel | High | Privacy-sensitive, requires consent, cross-site tracking |
| LinkedIn Insight | Medium | B2B attribution, privacy implications |
| TikTok Pixel | Medium | Privacy-sensitive, requires consent |
| Floodlight | Medium | Legacy — should be evaluated for migration |
| Consent Initialization | Critical | Must fire first; errors break entire consent chain |
