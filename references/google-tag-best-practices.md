# Google Tag Best Practices — Official Documentation Reference

Curated from Google's official developer documentation. Organized by GTM audit category
to support the 53-check audit framework. Each section cites the source URL.

---

## 1. Tag Health

### GA4 Configuration (T04, T05, T08)

**Single Config Call Rule**
> "You should call the `config` command only once per Google tag."
> Every subsequent call should use the `set` command.
— [gtag.js Configure Guide](https://developers.google.com/tag-platform/gtagjs/configure)

**Valid Tag ID Prefixes** (all interchangeable):
- `GT-XXXXXX` — Google tag (current standard)
- `G-XXXXXX` — Google Analytics 4 legacy prefix
- `AW-XXXXXX` — Google Ads legacy prefix
- `DC-XXXXXX` — Google Floodlight legacy prefix

**Critical**: Universal Analytics (`UA-`) tags are NOT compatible with Google tag (`GT-`).

**Google Tag Snippet Placement**
> "The Google tag snippet must appear on the same page, above event commands, or data will not be sent."
— [gtag.js Reference](https://developers.google.com/tag-platform/gtagjs/reference)

**Parameter Scope Precedence** (highest → lowest):
1. Event scope (per-event parameters)
2. Config scope (per-target parameters)
3. Global scope via `set` command

> "Parameter values set in one scope don't modify the values set for the same parameter in a different scope."
— [gtag.js Reference](https://developers.google.com/tag-platform/gtagjs/reference)

### Deprecated Tags (T09)

**Mandatory Migration**: Upgrade from legacy libraries (`analytics.js`, `conversions.js`, `ga.js`) to gtag.js or GTM.
— [Prerequisites Guide](https://developers.google.com/tag-platform/devguides/prerequisites)

> "Don't use legacy tags (ga.js, analytics.js, conversion.js) — upgrade to gtag.js or GTM."
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

### Custom HTML Safety (T07)

**Minimize custom code**:
> "Minimize or eliminate the use of custom HTML tags and custom JavaScript variables. Use built-in tag templates, triggers, and variables instead of custom code whenever possible."
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

> "Avoid placing static JavaScript code in GTM. Static JavaScript is more efficiently served in an external file via CDN with browser caching."
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

**CSP Security**: Custom JavaScript variables require `'unsafe-eval'` in CSP. Google recommends using Custom Templates instead.
— [CSP Guide](https://developers.google.com/tag-platform/security/guides/csp)

### Event Implementation (T06)

**Use Recommended Events**:
> "Implement recommended events using predefined key-value pairs rather than custom events to enable existing and future reporting features."
— [gtag.js Configure Guide](https://developers.google.com/tag-platform/gtagjs/configure)

> "Recommended events are NOT sent automatically; they require additional context and manual setup."
— [GA4 Recommended Events](https://support.google.com/analytics/answer/9267735)

**8 Core Ecommerce Events** (minimum for CMS integrations):
1. `view_item_list` — params: `item_list_id`, `item_list_name`, `items[]`
2. `add_to_cart` — params: `value`, `currency`, `items[]`
3. `begin_checkout` — params: `value`, `currency`, `items[]`
4. `purchase` — params: `value`, `currency`, `items[]`, `transaction_id` (deduplication)
5. `sign_up` — param: `method`
6. `generate_lead` — params: `value`, `currency`
7. `subscribe` — params: `value`, `currency`, `coupon`
8. `book_appointment` — params: `value`, `currency`, `coupon`
— [CMS Integration Guide](https://developers.google.com/tag-platform/devguides/gtag-integration)

**Critical Parameter Rules**:
- `currency`: Required if `value` is set. Must be 3-letter ISO 4217 (e.g., "USD")
- `value`: Sum of `(price * quantity)` for all items. Exclude shipping/tax.
- `transaction_id`: Required for `purchase` and `refund` (prevents duplicates)
- `items[]`: One of `item_id` or `item_name` is required per item
— [GA4 Events Developer Reference](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)

### Tag Naming (T01)

**Account & Container Structure**:
> "Set up one Tag Manager account per organization."
> "Best practice: set up one container per web domain."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

---

## 2. Tag Conflicts & Interference

### Single Instance Rule (F01, F02)

> "Only one instance of gtag.js per page; add multiple IDs to existing instance."
— [CMS Integration Guide](https://developers.google.com/tag-platform/devguides/gtag-integration)

**Config Duplication**:
> "You should call the `config` command only once per Google tag."
— [gtag.js Configure Guide](https://developers.google.com/tag-platform/gtagjs/configure)

### Container Publishing (F10)

> "When someone publishes a container, all changes go live regardless of domain. If you need to apply changes to one domain without affecting others, use a different container for each."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

### Pre-Installation Discovery (F01, F09)

> "Use Google Tag Assistant for automated tag discovery before adding new tags."
> "Manually search source code for existing tags."
> "Check for existing `dataLayer` object and its contents."
— [Prerequisites Guide](https://developers.google.com/tag-platform/devguides/prerequisites)

---

## 3. Trigger Quality

### Trigger Configuration (R02, R04, R06)

> "Test form and link triggers before publishing. These can break if another JavaScript event interrupts the process."
— [Trigger Best Practices](https://support.google.com/tagmanager/answer/7679102)

> "Limit the scope of form and link triggers to tested pages. Use filters to ensure triggers only fire when specified conditions are met."
— [Trigger Best Practices](https://support.google.com/tagmanager/answer/7679102)

> "Test in older web browsers. Older browsers can have problems with tag behavior."
— [Trigger Best Practices](https://support.google.com/tagmanager/answer/7679102)

### Consent Initialization Trigger (R01, C04)

> "Use Consent Initialization triggers for consent functions only. For tags not specifically used to manage consent settings, use the Initialization trigger instead."
— [Trigger Best Practices](https://support.google.com/tagmanager/answer/7679102)

### Event Naming Conventions (R03)

**GA4 Lead Generation Events** (standardized names):
- `generate_lead`, `qualify_lead`, `disqualify_lead`, `working_lead`, `close_convert_lead`, `close_unconvert_lead`
— [GA4 Events Developer Reference](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)

**GA4 Ecommerce Events** (standardized names):
- `add_to_cart`, `begin_checkout`, `purchase`, `refund`, `view_item`, `view_item_list`, `select_item`, `add_to_wishlist`, `remove_from_cart`, `view_cart`, `add_payment_info`, `add_shipping_info`, `select_promotion`, `view_promotion`
— [GA4 Recommended Events](https://support.google.com/analytics/answer/9267735)

---

## 4. Consent & Privacy

### Consent Mode v2 — Mandatory Setup (C01, C02, C03, C05, C06)

**Default consent state requirements**:
- Must be set **before** any measurement data commands (`config` or `event`)
- Must be set on **every page** of the website
- Must include all four consent types: `ad_storage`, `ad_user_data`, `ad_personalization`, `analytics_storage`
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

**Consent Mode v2 Parameters** (required since November 2023):
| Parameter | Values | Description |
|-----------|--------|-------------|
| `ad_storage` | `'granted'` / `'denied'` | Storage for advertising cookies/identifiers |
| `ad_user_data` | `'granted'` / `'denied'` | Sending user data to Google for advertising |
| `ad_personalization` | `'granted'` / `'denied'` | Personalized advertising |
| `analytics_storage` | `'granted'` / `'denied'` | Storage for analytics (visit duration, etc.) |
| `wait_for_update` | positive integer (ms) | Time to wait for CMP consent update |
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

**Additional Consent Types** (optional):
- `functionality_storage` — website/app functionality (e.g., language settings)
- `personalization_storage` — personalization (e.g., video recommendations)
- `security_storage` — security (authentication, fraud prevention)
— [Consent Mode Overview](https://developers.google.com/tag-platform/security/concepts/consent-mode)

### Implementation Sequence (C03, C04) — Critical Order

> "If your consent code is called out of order, consent defaults will not work."
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

**Required order**:
1. Load Google tag with `consent('default', {...})`
2. Load consent solution (CMP) — account for async loading
3. Call `consent('update', {...})` after user indicates consent

**Default setup**:
```javascript
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'analytics_storage': 'denied'
});
```

**Async CMP handling** — use `wait_for_update`:
```javascript
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'wait_for_update': 500  // ms to wait for CMP
});
```

### Regional Configuration (C01)

ISO 3166-2 codes for region-specific defaults:
```javascript
gtag('consent', 'default', {
  'analytics_storage': 'denied',
  'region': ['ES', 'US-AK']
});
```
> "Scope the default consent settings to the regions where you are surfacing consent banners to your visitors" to preserve measurement elsewhere.
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

**Precedence**: More specific region takes effect (US-CA overrides US for California).

### Tag Behavior When Consent Denied (C02, C05, C06)

| Consent Type Denied | Tag Behavior |
|---------------------|-------------|
| `ad_storage` | No ad cookies written/read, requests via different domain, IP truncated, Google Signals paused |
| `analytics_storage` | No analytics cookies, cookieless pings sent for modeling |
| `ad_personalization` | Remarketing and personalized ads disabled |
| `ad_user_data` | `user_id` and enhanced conversions disabled |
| `ad_storage` + `ads_data_redaction: true` | All above + ad-click identifiers redacted |
— [Consent Mode Overview](https://developers.google.com/tag-platform/security/concepts/consent-mode)

### Basic vs Advanced Consent Mode

- **Basic**: Google tags fully blocked until consent. No data before consent. General modeling.
- **Advanced**: Tags load with defaults `denied`. Cookieless pings sent when denied. Advertiser-specific modeling (more detailed).
— [Consent Mode Overview](https://developers.google.com/tag-platform/security/concepts/consent-mode)

### GTM-Specific Consent APIs (C01, C04)

In GTM templates, do NOT use `gtag('consent', ...)`. Use these APIs instead:
- `setDefaultConsentState` — set defaults using "Consent Initialization - All Pages" trigger
- `updateConsentState` — call as early as possible after user consent
- `gtagSet` — for `ads_data_redaction` and `url_passthrough`

> "Don't use `gtag('consent','update',...)` in Tag Manager context — use `updateConsentState` API instead."
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

### Common Consent Pitfalls (C03)

- **Don't** update consent on a transition page — causes missing `session_start` event
- **Don't** call update immediately before page reload — may cancel network requests
- **Don't** use legacy tags (ga.js, analytics.js) — upgrade to gtag.js or GTM
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

### URL Passthrough & Ads Data Redaction

**URL Passthrough** (`url_passthrough: true`):
- Passes `gclid`, `dclid`, `gclsrc`, `_gl`, `wbraid` via URL parameters
- Requirements: consent-aware Google tag, same-domain links, GCLID/DCLID present
- Redirects must pass all URL parameters unchanged
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

**Ads Data Redaction** (`ads_data_redaction: true`):
- When enabled AND `ad_storage` denied: ad-click identifiers redacted, requests via cookieless domain
- No effect when `ad_storage` granted
— [Consent Mode Guide](https://developers.google.com/tag-platform/security/guides/consent)

### CMP Partners

> "Use Google-certified CMP Partners for ePD/GDPR compliance. CMPs auto-update consent mode, implement/upgrade consent banners, manage banner content, pass consent signals to Google."
— [Google Ads Best Practices](https://support.google.com/google-ads/answer/14792290)

---

## 5. Performance & Loading

### Container Size (P06)

> "If the Size indicator value is above 70%, take steps to optimize your container configuration."
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

**Optimization strategies**:
- Combine similar tags using Lookup Table variables for dynamic field values
- Remove unnecessary tags and variables
- Replace long Lookup Tables with RegEx Table variables
- Split large multi-site containers into smaller ones (GTM 360: use zones)
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

### Custom Code Performance (P02, P03, P04)

> "Minimize or eliminate the use of custom HTML tags and custom JavaScript variables."
> "Use built-in tag templates, triggers, and variables instead of custom code whenever possible."
> "Avoid placing static JavaScript code in GTM. Static JavaScript is more efficiently served in an external file via CDN with browser caching."
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

### Server-Side Tagging Benefits (P01, P02)

> "Improved page speed: amount of third-party code loaded in the browser is greatly reduced."
> "Content security policies can be made more restrictive since browser no longer communicates directly with vendor domains."
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

**Production Deployment Requirements**:
- Default Cloud Run deployment is for testing only
- Minimum 3 instances per container for production redundancy
- Strongly recommended: point a subdomain of your website to the tagging server
- Subdomain enables HttpOnly cookies (more durable, not visible to page scripts)
— [Server-Side Tagging Overview](https://developers.google.com/tag-platform/tag-manager/server-side/overview)

**Three performance benefits of SST**:
1. Single data stream to server instead of multiple vendor requests
2. JavaScript library footprint greatly reduced in browser
3. Server can act as CDN with custom cache headers, compression, temporary storage
— [Why & When SST](https://developers.google.com/tag-platform/learn/sst-fundamentals/3-why-and-when-sst)

### Tag Loading Strategy

> "Google Tag Manager should be your first choice for deploying analytics and marketing tags."
> Use gtag.js only when tagging for a single product with few changes over time.
— [Prerequisites Guide](https://developers.google.com/tag-platform/devguides/prerequisites)

**Deployment verification checklist**:
- Compatibility with GA4 destination
- Remarketing functionality and conversion measurement
- Tag firing on all pages including key event pages
- Proper data layer transmission
- Tools: Tag Assistant, Chrome DevTools Network tab (filter "google"), GA4 Realtime report
— [CMS Integration Guide](https://developers.google.com/tag-platform/devguides/gtag-integration)

---

## 6. Data Layer & Variables

### Data Layer Setup (V01, V02, V03)

**Data Layer Recommendation**:
> "For complex tag firing scenarios, implement a data layer to help pass data from your site/app to tags."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

**Custom JS Variable Limits**:
> Custom JavaScript variables with complex logic should be refactored to data layer pushes or replaced with Lookup/RegEx Tables.
— [Container Size & Efficiency](https://support.google.com/tagmanager/answer/2772488)

### Constant Variables (V04)

**Measurement IDs**: Store in Constant variables, not hardcoded in tags. Google's `config` command supports multiple IDs via a single instance.
— [CMS Integration Guide](https://developers.google.com/tag-platform/devguides/gtag-integration)

### Item Object Parameters (V01) — Standardized Schema

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `item_id` | string | Yes* | *One of `item_id` or `item_name` required |
| `item_name` | string | Yes* | *One of `item_id` or `item_name` required |
| `affiliation` | string | No | Supplying company or store location |
| `coupon` | string | No | Event-level and item-level are independent |
| `discount` | number | No | Unit monetary discount |
| `index` | number | No | Position in list |
| `item_brand` | string | No | |
| `item_category` through `item_category5` | string | No | Category hierarchy |
| `item_list_id` / `item_list_name` | string | No | Item-level overrides event-level |
| `item_variant` | string | No | |
| `location_id` | string | No | Google Place ID recommended |
| `price` | number | No | Discounted unit price if discount applies |
| `quantity` | number | No | Defaults to 1 |

Up to 27 custom parameters per items array.
— [GA4 Events Developer Reference](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)

---

## 7. Container Organization

### Account Structure (O01, O02)

> "Set up one Tag Manager account per organization. The organization for which the tags will be managed should create the Tag Manager account."
> "If an agency manages tags on behalf of your company, your company should create the GTM account and add the agency's Google account as a user."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

### Container Strategy (O05, O06)

> "Best practice: set up one container per web domain."
> "If the user experience and tags on a website span more than one domain, set up a single container that serves all the domains involved."
> "Configurations cannot easily be shared across containers without using container export/import, or by using the API."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

### Access Control & Succession (O03, O04)

> "Put a strategy in place for who will manage the account over the long term."
> "Ensure that if someone leaves your organization and their credentials are terminated, the organization will maintain access."
> "Some organizations delegate administrator roles to multiple users; others create a dedicated master Google account for organizational Tag Manager administration."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576)

### Migration Best Practice

> "When upgrading to Tag Manager, best practice is to migrate all tags at once."
> "Remove any existing legacy tag integrations (analytics.js) before creating gtag.js integration."
— [Considerations Before Install](https://support.google.com/tagmanager/answer/6103576), [CMS Integration Guide](https://developers.google.com/tag-platform/devguides/gtag-integration)

---

## 8. Security (Cross-Category)

### Content Security Policy (CSP)

**Recommended approach**: Server-generated nonce.
```
Content-Security-Policy:
  script-src 'nonce-{SERVER-GENERATED-NONCE}';
  img-src www.googletagmanager.com;
  connect-src www.googletagmanager.com www.google.com
```
— [CSP Guide](https://developers.google.com/tag-platform/security/guides/csp)

**Rules**:
- Avoid `'unsafe-inline'` unless no feasible alternative
- Avoid `'unsafe-eval'` — use Custom Templates instead
- Each Google TLD must be specified individually (no wildcard TLDs)
- Test with `report-uri`/`report-to` before enforcement
- Use Tag Assistant to identify blocked resources
— [CSP Guide](https://developers.google.com/tag-platform/security/guides/csp)

**CSP Directives by Product**:

| Product | script-src | img-src | connect-src |
|---------|-----------|---------|-------------|
| GTM Container | `'nonce-{NONCE}'` | `www.googletagmanager.com` | `www.googletagmanager.com www.google.com` |
| GA4 | `https://*.googletagmanager.com` | `https://*.google-analytics.com https://*.googletagmanager.com` | `https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com` |
| GA4 + Signals | (above) | (+ `*.g.doubleclick.net *.google.com`) | (+ `*.g.doubleclick.net pagead2.googlesyndication.com`) |
| Google Ads | `googleadservices.com google.com googletagmanager.com pagead2.googlesyndication.com googleads.g.doubleclick.net` | (extensive) | (extensive) |
— [CSP Guide](https://developers.google.com/tag-platform/security/guides/csp)

### 2-Step Verification

> Admins can require verification before modifying Custom JavaScript variables, Custom HTML tags, or User settings.
— [Security Hub](https://developers.google.com/tag-platform/security)

### Server-Side Tagging Security

- Server container acts as buffer between users and vendors
- Validate, parse, anonymize, or block HTTP requests before forwarding
- Prevents vendors from accessing third-party cookies
- Fingerprint vectors (IP, HTTP headers) can be obfuscated
- Browser cookies set with HttpOnly flag (more durable, not visible to page scripts)
- Data enrichment happens server-side (API secrets, PII never exposed to browser)
— [Why & When SST](https://developers.google.com/tag-platform/learn/sst-fundamentals/3-why-and-when-sst)

### Template Policies

**Custom template policies** control what tags can do:
- `inject_script`: Control script injection via `data.url`
- `send_pixel`: Control pixel sending
- `write_globals`: Control global variable access via `data.key`

Policy function returns `true` (allow), `false` (reject), or throws an exception.
— [Template Policies](https://developers.google.com/tag-platform/tag-manager/templates/policies)

---

## 9. Template Best Practices (Supplementary)

### Naming & Style

- Template name format: "Organization Name" + "Template Name" in Title Case
- Do NOT use "Official" unless authorized
- Parameter naming: lowerCamelCase exclusively (e.g., `userName`, `customerID`)
- Field labels: sentence case, minimal length
- Help text: sentence case, include example input when possible
— [Template Style Guide](https://developers.google.com/tag-platform/tag-manager/templates/style)

### Icon Specifications

- Formats: PNG, JPEG, GIF
- Dimensions: 48px-96px square
- File size: under 50KB
- No official company logos unless authorized
— [Template Style Guide](https://developers.google.com/tag-platform/tag-manager/templates/style)

### Community Gallery Submission

Required files at repo root:
1. `template.tpl` — exported template with `categories` array
2. `metadata.yaml` — homepage URL, docs URL, version SHA + changeNotes
3. `LICENSE` — Apache 2.0, ALL CAPS filename
4. `README.md` — recommended

Categories (1-3): ADVERTISING, ANALYTICS, CONVERSIONS, REMARKETING, TAG_MANAGEMENT, UTILITY, etc.
— [Template Gallery](https://developers.google.com/tag-platform/tag-manager/templates/gallery)

---

## Source Index

| # | Source | URL |
|---|--------|-----|
| 1 | Prerequisites Guide | https://developers.google.com/tag-platform/devguides/prerequisites |
| 2 | gtag.js Reference | https://developers.google.com/tag-platform/gtagjs/reference |
| 3 | gtag.js Configure | https://developers.google.com/tag-platform/gtagjs/configure |
| 4 | CMS Integration Guide | https://developers.google.com/tag-platform/devguides/gtag-integration |
| 5 | CSP Guide | https://developers.google.com/tag-platform/security/guides/csp |
| 6 | Consent Mode Guide | https://developers.google.com/tag-platform/security/guides/consent |
| 7 | Consent Mode Overview | https://developers.google.com/tag-platform/security/concepts/consent-mode |
| 8 | Security Hub | https://developers.google.com/tag-platform/security |
| 9 | Privacy Overview | https://developers.google.com/tag-platform/security/concepts/privacy |
| 10 | GA4 Recommended Events | https://support.google.com/analytics/answer/9267735 |
| 11 | GA4 Events Dev Reference | https://developers.google.com/analytics/devguides/collection/ga4/reference/events |
| 12 | Trigger Best Practices | https://support.google.com/tagmanager/answer/7679102 |
| 13 | Container Size & Efficiency | https://support.google.com/tagmanager/answer/2772488 |
| 14 | Considerations Before Install | https://support.google.com/tagmanager/answer/6103576 |
| 15 | Server-Side Tagging Overview | https://developers.google.com/tag-platform/tag-manager/server-side/overview |
| 16 | SST Introduction | https://developers.google.com/tag-platform/tag-manager/server-side/intro |
| 17 | Why & When SST | https://developers.google.com/tag-platform/learn/sst-fundamentals/3-why-and-when-sst |
| 18 | Template Style Guide | https://developers.google.com/tag-platform/tag-manager/templates/style |
| 19 | Template Policies | https://developers.google.com/tag-platform/tag-manager/templates/policies |
| 20 | Template Gallery | https://developers.google.com/tag-platform/tag-manager/templates/gallery |
| 21 | Google Ads Best Practices | https://support.google.com/google-ads/answer/14792290 |
