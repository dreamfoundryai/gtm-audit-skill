# GTM On-Page Test Generation Reference

Guide for generating on-page test suites from GTM container data. The output is a
self-contained markdown document designed for execution by Claude in Chrome browser
with GTM Tag Assistant connected.

## Prerequisites (MUST appear in every test brief)

### Mandatory: GTM Tag Assistant Connection

The tester MUST have Google Tag Assistant (tagassistant.google.com) connected to the
target site before starting any tests. Without Tag Assistant, Layer 1 checks (did it fire?)
are impossible.

```
SETUP INSTRUCTIONS (include in every test brief):

1. Open Google Tag Assistant: https://tagassistant.google.com/
2. Click "Add domain" and enter the site URL
3. Select the correct GTM container ID (e.g., GTM-XXXXXXX)
4. Click "Connect" — Tag Assistant opens the site in a new tab with debug mode
5. Verify Tag Assistant shows "Connected" and is logging events
6. Keep Tag Assistant open in a separate tab throughout ALL testing
7. Open Chrome DevTools → Network tab (useful for Layer 3 checks)
8. Open Chrome DevTools → Console tab (useful for Custom HTML tag output)
```

### Additional Setup

- **Fresh session**: Clear cookies/cache or use Incognito before each test run
- **Consent**: Document whether to accept/deny consent and how it affects tag firing
- **Test data**: Provide shipping address, payment method, order cap for purchase tests

---

## Data Sources

Read these JSON files from `/tmp/gtm-audit/` or the project's `backups/` directory:

| File | Contains | Key Fields |
|------|----------|------------|
| `tags.json` | All tags | `tagId`, `name`, `type`, `parameter[]`, `firingTriggerId[]`, `blockingTriggerId[]`, `consentSettings`, `tagFiringOption`, `paused`, `setupTag[]`, `teardownTag[]` |
| `triggers.json` | All triggers | `triggerId`, `name`, `type`, `customEventFilter[]`, `filter[]` |
| `variables.json` | All variables | `variableId`, `name`, `type`, `parameter[]` |
| `built_in_variables.json` | Enabled built-ins | `type`, `name` |
| `metadata.json` | Container info | `containerId`, `containerName`, `publicId` |

---

## Tag Classification Algorithm

### Step 1: Identify trigger type for each tag

Map each tag's `firingTriggerId` to the triggers JSON. Classify triggers:

| Trigger Type | Indicators |
|-------------|------------|
| **All Pages** | `type: "pageview"` with no filters |
| **Consent Init** | `type: "consentInit"` or name contains "Consent Initialization" |
| **Container Loaded** | `type: "domReady"` or similar |
| **Window Loaded** | `type: "windowLoaded"` |
| **Custom Event** | `type: "customEvent"` — extract event name from `customEventFilter[].parameter[].value` |
| **Click** | `type: "linkClick"` or `type: "click"` |
| **Element Visibility** | `type: "elementVisibility"` |
| **Form Submit** | `type: "formSubmission"` |
| **Scroll Depth** | `type: "scrollDepth"` |
| **Timer** | `type: "timer"` |
| **Trigger Group** | `type: "triggerGroup"` |

### Step 2: Classify tags into test groups

| Group | Rule | Test Approach |
|-------|------|---------------|
| **Always-Fire** | Fires on All Pages, Consent Init, Container Loaded, or Window Loaded triggers | Test on homepage load — all should appear in Tag Assistant |
| **Ecommerce Funnel** | Fires on custom events matching GA4 ecommerce event names | Test through user journey steps |
| **Interaction** | Fires on click, scroll, visibility, form, or non-ecommerce custom events | Test with specific user actions |
| **Consent** | Tag type is consent template (`cvt_*` with consent in name) | Test during page init and consent banner interaction |
| **Conditional/Optional** | Fires on narrow URL filters, specific element visibility, or low-priority events | Document as optional tests |
| **Paused** | `paused: true` | Should NOT fire — verify absence |

### Step 3: Map ecommerce events to funnel steps

Standard GA4 ecommerce funnel mapping:

| Funnel Step | dataLayer Event(s) | User Action |
|-------------|-------------------|-------------|
| Step 0: Consent Init | (consent initialization) | Page begins loading |
| Step 1: Page Load | (page_view, all-pages tags) | Navigate to homepage |
| Step 2: Collection | `view_item_list` | Browse a category page |
| Step 3: Product | `view_item` | Click into a product |
| Step 4: Wishlist | `add_to_wishlist` | Click wishlist button (optional) |
| Step 5: Add to Cart | `add_to_cart` | Click "Add to Cart" |
| Step 6: View Cart | `view_cart` | Navigate to cart page |
| Step 7: Begin Checkout | `begin_checkout` | Click "Checkout" |
| Step 8: Shipping | `add_shipping_info` | Enter shipping details |
| Step 9: Payment | `add_payment_info` | Enter payment details |
| Step 10: Purchase | `purchase` | Complete order |

For each funnel step, list ALL tags that fire on that event (across all vendors).

---

## Tag-Type Test Templates

For each tag, generate checks based on its `type` field. Extract actual parameter values
from the tag's `parameter[]` array.

### `googtag` (Google Tag — GA4 or Ads base config)

```markdown
| # | Tag | ID | What to Check |
|---|-----|----|---------------|
| X | {tag.name} | {tag.tagId} | Tag ID: `{extracted tagId param}`, `send_page_view: {value}` |

Data Validation:
- [ ] Tag ID matches expected value: `{tagId}`
- [ ] `send_page_view` = `{true/false}` (check tag config)
- [ ] Network request sent to google-analytics.com or googleads.g.doubleclick.net
- [ ] Tag fires {once per page / once per event} (tagFiringOption: {value})
```

### `gaawe` (GA4 Event Tag)

```markdown
| # | Tag | ID | Event | What to Check |
|---|-----|----|-------|---------------|
| X | {tag.name} | {tag.tagId} | `{event_name}` | Parameter validation below |

Data Validation — {tag.name} → `{event_name}`:
{For each parameter in tag.parameter where key starts with "eventSettingsVariable" 
 or in the "vtp_eventParameters" map:}
- [ ] `{param_key}` = {expected_value_or_variable} (not undefined/null/empty)
{If ecommerce event:}
- [ ] `items` array populated with correct products
- [ ] `currency` matches page currency
- [ ] `value` matches displayed price/total
```

**Parameter extraction for GA4 event tags**: Look for parameters with key `eventSettingsVariable`
or within the `vtp_eventParameters` map. Each parameter entry has a `key` (the GA4 parameter name)
and `value` (the GTM variable reference like `{{ecommerce.items}}`).

### `awct` (Google Ads Conversion)

```markdown
Data Validation — {tag.name}:
- [ ] `conversionId` = `{extracted value}`
- [ ] `conversionLabel` = `{extracted value}`
- [ ] `conversionValue` = {variable reference} (verify number > 0)
- [ ] `currencyCode` = {variable reference} (verify matches page currency)
{If orderId parameter exists:}
- [ ] `orderId` = {variable reference} (verify matches transaction_id)
{If enhanced conversions enabled:}
- [ ] Enhanced Conversion data populated (check variable: {variable name})
```

### `gclidw` (Conversion Linker)

```markdown
Data Validation:
- [ ] `enableUrlPassthrough` = `{true/false}`
- [ ] Sets `_gcl_*` cookies
- [ ] Fires ONCE per page load (not multiple times)
```

### `baut` (Bing/Microsoft UET)

```markdown
Data Validation:
- [ ] UET Tag ID = `{extracted tagId param}`
- [ ] Event type = `{PAGE_LOAD / VARIABLE_REVENUE / CUSTOM}`
{If conversion tag:}
- [ ] `goalValue` = {variable reference} — verify populated (not undefined)
- [ ] `p_currency` = {variable reference}
{Check for legacy UA dataLayer paths in variables — flag as risk}
```

### `html` (Custom HTML)

```markdown
Data Validation:
- [ ] Tag executes without JavaScript errors in console
- [ ] Expected console.log output appears (if tag uses console.log)
- [ ] External script loads successfully (check Network tab)
{If Meta Pixel:}
- [ ] `fbq('init', '{pixel_id}')` called
- [ ] `fbq('track', '{event}')` called with correct parameters
- [ ] `eventID` present for server-side deduplication
- [ ] Network request to facebook.com/tr succeeds
{If DotDigital WBT:}
- [ ] `dmPt('{method}', ...)` called with correct parameters
- [ ] Console log "GTM DotDigital: {event}" appears
{If other vendor:}
- [ ] Vendor script loads from expected domain
- [ ] Tracking request sent to expected endpoint
```

### `hjtc` (Hotjar)

```markdown
Data Validation:
- [ ] Site ID = `{extracted value}`
- [ ] Hotjar script loads successfully
```

### Consent Template Tags (`cvt_*`)

```markdown
Data Validation — Consent Default:
- [ ] All consent types set correctly for region (ad_storage, analytics_storage, ad_user_data, ad_personalization)
- [ ] `url_passthrough` = {value}
- [ ] `wait_for_update` = {value}ms
- [ ] Fires FIRST in Consent Initialization event

Data Validation — Consent Update:
- [ ] Fires on correct custom event (e.g., `userPrefUpdate`)
- [ ] Updates consent state in Tag Assistant consent tab
```

---

## Behavioral Quality Checks

Include these in EVERY test brief. They are tag-agnostic quality gates.

### B1: Duplicate Event Detection

```markdown
At every funnel step, check Tag Assistant event count:
- [ ] Each user action produces exactly ONE dataLayer event (not 2+)
- [ ] Page load produces exactly ONE Consent Initialization and ONE Container Loaded
- [ ] No tags fire more times than expected (check "Times Fired" in Tag Assistant)
- [ ] Config/base tags fire once per page load, not on every dataLayer event
```

### B2: SPA / Page Navigation Behavior

```markdown
- [ ] Determine if site uses full page reloads or SPA-style navigation
- [ ] If SPA: verify page_view events fire on virtual pageviews
- [ ] If SPA: verify ecommerce tags don't carry stale data from previous page
```

### B3: Race Conditions & Tag Sequencing

Generate these checks by analyzing `setupTag` and `teardownTag` arrays in tag config,
plus trigger dependencies:

```markdown
For each tag with setupTag dependency:
- [ ] `{dependent_tag_name}` ({id}) fires AFTER `{setup_tag_name}` ({setup_id})

Common sequencing rules (auto-detect from container):
- Google Ads Config fires AFTER Conversion Linker
- GA4 Event tags fire AFTER GA4 Config tag
- Meta event tags fire AFTER Meta Pixel Base
- All vendor event tags fire AFTER their respective init/base tags
```

### B4: Console Errors

```markdown
- [ ] No `{vendor_function} is not defined` errors
- [ ] No `Cannot read property of undefined` errors from Custom HTML tags
- [ ] No CORS errors blocking tracking requests
{For each Custom HTML tag that uses console.log:}
- [ ] `{expected_log_message}` appears in console
```

### B5: Network Request Validation

Auto-generate from vendor detection:

| Vendor | Expected Endpoint | Check |
|--------|------------------|-------|
| GA4 | `google-analytics.com/g/collect` | 200 OK |
| Meta | `facebook.com/tr` | 200 OK |
| Google Ads | `googleads.g.doubleclick.net` | 200 OK |
| Bing | `bat.bing.com` | 200 OK |
| {Custom} | {extracted from HTML tag script src} | 200 OK |

---

## Cross-Vendor Consistency Checks

For ecommerce events where multiple vendors receive the same data, generate comparison tables:

```markdown
| Field | GA4 ({id}) | Meta ({id}) | GAds ({id}) | {Vendor} ({id}) |
|-------|-----------|-----------|-----------|----------------|
| Order total | value: $___ | value: $___ | conversionValue: $___ | {field}: $___ |
| Currency | currency: ___ | currency: ___ | currencyCode: ___ | {field}: ___ |
| Order ID | transaction_id | transaction_id | orderId | {field} |
| Item count | items.length | contents.length | — | {field} |

- [ ] All values match across vendors (or document discrepancies)
```

---

## Gate Rules

Insert gate checkpoints at critical funnel steps:

```markdown
> **GATE RULE**: DO NOT proceed to the next step unless ALL tags listed
> for this step have fired correctly AND all parameter values are verified.
> If any tag fails, STOP and document the failure.
```

Place gates at:
- Step 5 (Add to Cart) — first conversion event
- Step 7 (Begin Checkout) — checkout entry
- Step 9 (Payment Info) — last step before purchase
- Step 10 (Purchase) — only if ALL prior steps pass

---

## Known Issues Section

Auto-generate from audit findings or tag config anomalies:

1. **Consent gaps**: Tags with `consentSettings.consentStatus: "notSet"` that should have consent
2. **Legacy variables**: Variables referencing UA-era dataLayer paths (e.g., `ecommerce.purchase.actionField`)
3. **Hardcoded values**: Custom HTML tags with hardcoded values that should be dynamic
4. **Duplicate triggers**: Tags with multiple triggers that could cause double-firing
5. **Enhanced conversion mismatches**: Different EC variables across same-vendor tags
6. **Fragile selectors**: CSS selectors with auto-generated class names
7. **Missing parameters**: Tag parameters referencing variables that may not populate

---

## Output Structure

The generated test brief should follow this structure:

```markdown
# GTM Tag Testing Brief — {container_name}

**Container ID**: {public_id} (internal API ID: {container_id})
**Test Date**: {today}
**Tester**: Claude (Chrome) + GTM Preview Mode (Tag Assistant)
**Site**: {site_url}

---

## Setup
{Prerequisites, Tag Assistant connection, fresh session, consent instructions}

## Shipping Details (for checkout)
{If ecommerce site — provide test shipping data placeholder}

## GATE RULE
{Global gate rule}

## Testing Methodology
{Three-layer verification: fire → data → behavior}

## Behavioral Quality Checks
{B1-B5 checks}

## Parameter Reference
{Per-tag parameter tables extracted from container data}

## Funnel Test Steps
{Step 0 through Step 10, each with tag table + data validation + behavioral checks}

## Optional Tests
{Interaction tags, conditional tags}

## Complete Tag Checklist
{Master checklist of all active tags with key config to verify}

## Known Issues
{Auto-detected from container analysis}

## Results Template
{Pre-formatted template for recording results}
```

---

## Splitting Strategy

If the container has >25 active tags, split into vendor-grouped test suites:

| Suite | Contains |
|-------|----------|
| Suite 1: Google | GA4, Google Ads, Conversion Linker, Consent tags |
| Suite 2: Meta + Social | Meta Pixel, TikTok, LinkedIn, Pinterest |
| Suite 3: Vendors | Bing, DotDigital, Hotjar, Poptin, custom vendors |

Each suite is self-contained with its own setup, funnel steps, and results template.
Cross-vendor consistency checks appear in Suite 1 (the primary suite).

---

## Consent Testing (Multi-Region)

If the container has consent tags with regional rules, generate TWO test runs:

| Run | Region | Consent Default | Purpose |
|-----|--------|----------------|---------|
| Run A | Non-EEA (e.g., AU) | All granted | Verify all tags fire normally |
| Run B | EEA (e.g., EU) | All denied | Verify consent-gated tags are blocked until consent granted |

Each run is a complete funnel walkthrough. Run B should verify:
- Consent-gated tags do NOT fire before consent
- Tags fire correctly AFTER consent is granted via banner
- Consent state updates correctly in Tag Assistant
