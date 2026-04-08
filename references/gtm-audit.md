# GTM Container Audit Checklist

<!-- 53 checks across 7 categories -->

## Tag Health (25% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| T01 | All tags have descriptive names | Medium | Flag tags matching "Untitled", "Copy of", "Tag #", or default names | §1 Tag Naming |
| T02 | No stale paused tags (> 90 days) | Low | Check `paused: true` tags; cross-reference with container version dates | — |
| T03 | Tag firing option appropriate | High | `oncePerEvent` for event tags, `oncePerPage` for page-level, `unlimited` only when justified | — |
| T04 | GA4 Config tag exists and fires on All Pages | Critical | At least one `googtag` type tag with `All Pages` trigger | §1 GA4 Configuration — Single Config Call Rule |
| T05 | No duplicate GA4 measurement IDs | Critical | Extract `tagId` parameter from all `googtag`/`gaawc` tags; flag duplicates | §1 GA4 Configuration — Single Instance Rule |
| T06 | Conversion tags use correct event parameters | High | GA4 event tags should have `event_name` parameter; Google Ads tags need `conversionId` + `conversionLabel` | §1 Event Implementation — Critical Parameter Rules |
| T07 | Custom HTML tags reviewed for safety | High | Flag Custom HTML tags using `document.write`, `eval()`, `innerHTML` with user data, or loading unvetted external scripts | §1 Custom HTML Safety, §8 CSP |
| T08 | Tag sequencing configured for dependencies | Medium | Tags that depend on GA4 config should have setup tag sequencing; e.g., event tags fire after config | §1 GA4 Configuration — Single Config Call Rule |
| T09 | No deprecated tag types | Medium | Flag tags using `ua` (Universal Analytics), legacy Floodlight, or discontinued templates | §1 Deprecated Tags — Mandatory Migration |

## Trigger Quality (20% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| R01 | No orphaned triggers | Medium | Triggers whose `triggerId` is not in any tag's `firingTriggerId` or `blockingTriggerId` | — |
| R02 | Conversion triggers are specific | High | Conversion/purchase tags should NOT fire on "All Pages" — need specific event or page triggers | §3 Trigger Configuration — scope triggers to tested pages |
| R03 | Custom event naming consistent | Medium | Extract all custom event trigger names; check for mixed conventions (snake_case vs camelCase vs spaces) | §3 Event Naming Conventions |
| R04 | Click triggers use stable selectors | Medium | CSS selectors using only class names that look auto-generated are fragile; prefer IDs or data attributes | §3 Trigger Configuration — test in preview mode |
| R05 | Trigger groups used for multi-conditions | Low | If a tag needs multiple conditions (page + element + custom event), a trigger group is cleaner | — |
| R06 | No firing/exception trigger overlap | High | A tag should not have the same trigger in both `firingTriggerId` and `blockingTriggerId` | — |
| R07 | Scroll/visibility thresholds reasonable | Low | Scroll triggers at 1% or 100% are likely misconfigured; typical: 25%, 50%, 75%, 90% | — |
| R08 | Timer triggers have stop conditions | Medium | Timer triggers without `limit` or stop conditions can fire indefinitely | — |

## Consent & Privacy (20% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| C01 | Consent Mode v2 default command present | Critical | Look for a tag/trigger that sets `consent('default', {...})` — typically via CMP integration | §4 Consent Mode v2 — Mandatory Setup |
| C02 | Tags have consent settings configured | Critical | Check `consentSettings` field on each tag; "notSet" on advertising tags = FAIL | §4 Tag Behavior When Consent Denied |
| C03 | No tags fire before consent granted | High | Tags with `firingTriggerId` on consent initialization or All Pages without consent checks | §4 Implementation Sequence, §4 Common Pitfalls |
| C04 | Consent initialization trigger exists | High | A trigger type for consent initialization (usually provided by CMP template) | §3 Consent Initialization Trigger, §4 GTM-Specific Consent APIs |
| C05 | Ad tags require ad_storage consent | Critical | Meta Pixel, Google Ads, LinkedIn Insight, TikTok Pixel must have `ad_storage: granted` | §4 Consent Mode v2 Parameters table |
| C06 | Analytics tags have analytics_storage | High | GA4 tags should have `analytics_storage` consent configured | §4 Consent Mode v2 Parameters table |
| C07 | No PII in tags without consent | Critical | Tags sending email, phone, or user IDs must have consent and preferably hash data | §4 URL Passthrough & Ads Data Redaction |

## Performance & Loading (15% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| P01 | Critical tags have firing priority | Medium | GA4 Config, Consent Init should have higher priority than marketing pixels | — |
| P02 | Custom HTML avoids synchronous script loading | High | Check for `<script src="...">` without `async` or `defer` in Custom HTML tags | §5 Custom Code Performance |
| P03 | No `document.write` in Custom HTML | Critical | `document.write` blocks rendering and is a serious performance issue | §5 Custom Code Performance |
| P04 | Image pixels use Custom Image tag type | Medium | `<img>` pixel tags should use the built-in Custom Image type, not Custom HTML | §5 Custom Code Performance |
| P05 | Tags scoped appropriately (not all pages when unnecessary) | Medium | Marketing event tags firing on All Pages instead of specific conversion pages | §5 Container Size |
| P06 | Container tag count within bounds | Medium | See thresholds table — bloated containers slow page load | §5 Container Size — 70% indicator |
| P07 | No excessive listener tags | Low | Multiple scroll/click/visibility listeners on every page add overhead | — |
| P08 | Sequencing preferred over race conditions | Medium | If Tag B depends on Tag A, use sequencing — don't rely on firing order | — |

## Data Layer & Variables (10% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| V01 | Data layer variables use correct key paths | High | Variable type `v` (data layer) should reference valid, documented dataLayer keys | §6 Data Layer Setup, §6 Item Object Parameters |
| V02 | Custom JS variables are simple | Medium | Custom JavaScript variables with > 20 lines of code should be refactored to data layer | §6 Custom JS Variable Limits |
| V03 | Lookup tables preferred over Custom JS | Low | Repeated conditional logic in Custom JS → should be a Lookup Table or RegEx Table | §5 Container Size — RegEx Table optimization |
| V04 | Constant variables for IDs/keys | Medium | Measurement IDs, API keys in Constant variables (not hardcoded in each tag) | §6 Constant Variables |
| V05 | No unused variables | Low | Variables not referenced by any tag, trigger, or other variable | — |
| V06 | Variable naming consistent | Low | Check for consistent prefix/convention (e.g., "DL - ", "CJS - ", "Const - ") | — |
| V07 | Built-in variables minimal | Low | Only enable built-in variables that are actually used | — |

## Container Organization (10% weight)

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| O01 | Tags organized in folders by vendor/function | Low | Folders exist and group related tags (e.g., "GA4", "Meta", "Google Ads") | — |
| O02 | Naming convention consistent | Medium | Tags follow pattern like "Vendor - Type - Detail" (e.g., "GA4 - Event - purchase") | §9 Template Naming — lowerCamelCase for params |
| O03 | Container version notes meaningful | Low | Recent published versions have descriptive notes (not empty or "update") | — |
| O04 | No stale workspaces | Low | Workspaces with uncommitted changes older than 30 days | — |
| O05 | Container published recently | Medium | Last publish date < 90 days (unless site is stable and unchanging) | §7 Container Strategy |
| O06 | Tag/trigger/variable ratio reasonable | Low | Rough guide: triggers ≈ 0.5-1.5x tags; variables ≈ 0.3-1x tags | — |

## Tag Conflicts & Interference (15% weight)

Active tags that may cause issues with each other. Requires cross-referencing tags,
triggers, parameters, and consent settings to detect interference patterns.

| ID | Check | Severity | How to Evaluate | Google Ref |
|----|-------|----------|-----------------|------------|
| F01 | No duplicate tracking pixels | Critical | Multiple tags of the same type (e.g., two Meta Pixels, two LinkedIn Insight tags) sending to the SAME pixel/partner ID → double-counting conversions and inflating metrics | §2 Single Instance Rule, §2 Pre-Installation Discovery |
| F02 | No competing GA4 config tags | Critical | Multiple `googtag` tags with different measurement IDs firing on the same pages → conflicting session attribution, split user data across properties | §1 GA4 Configuration — Single Config Call Rule |
| F03 | No conflicting conversion tags | High | Multiple Google Ads conversion tags for the same conversion action (same `conversionId` + `conversionLabel`) → duplicate conversion reporting | §1 Event Implementation — transaction_id deduplication |
| F04 | Same-trigger tag race conditions | High | Multiple tags sharing the same trigger with no sequencing → execution order is undefined. Critical when Tag B reads data that Tag A writes to dataLayer | — |
| F05 | Consent state conflicts | Critical | Two tags of the same vendor where one requires consent and the other doesn't → data leaks on the unguarded tag, or the consented tag never fires while the other does, creating inconsistent tracking | §4 Tag Behavior When Consent Denied |
| F06 | Overlapping event tags | High | Multiple tags listening for the same custom event (e.g., two tags on `purchase` event) sending to the same destination → duplicate events in reporting | — |
| F07 | Blocking trigger negates firing | Medium | A tag's blocking trigger is so broad it prevents the tag from ever firing (e.g., fires on "Page Path contains /checkout" but blocked on "All Pages") — effectively a dead tag | — |
| F08 | Tag overwrite conflicts | High | Custom HTML tags that write to the same global variable or dataLayer key → last-write-wins race condition, unpredictable values downstream | §8 Template Policies — write_globals |
| F09 | Pixel ID mismatches across tags | High | Same vendor (e.g., Meta) with DIFFERENT pixel IDs in base pixel vs event tags → events attributed to wrong pixel, broken funnel tracking | §2 Pre-Installation Discovery |
| F10 | Active tag duplicates paused tag | Medium | An active tag that does the same thing as a paused tag (same type, same destination, similar trigger) → suggests the active tag was meant to replace the paused one, but both may re-activate in a future publish | §2 Container Publishing |
| F11 | Server-side + client-side double-fire | Critical | Same event tracked by both a GTM server container tag AND a client-side tag → double-counted conversions unless deduplication is configured at the destination | §5 Server-Side Tagging Benefits |

### Conflict Detection Logic

For each conflict type, the analysis engine should:

1. **Group tags by vendor/type**: Cluster all GA4 tags, all Meta Pixel tags, all Google Ads tags, etc.
2. **Extract destination IDs**: Pull measurement IDs, pixel IDs, conversion labels from tag parameters
3. **Map shared triggers**: Identify tags that fire on the exact same trigger(s)
4. **Compare consent states**: Within each vendor group, compare `consentSettings` for inconsistencies
5. **Analyze Custom HTML interactions**: Parse Custom HTML tag content for global variable writes, dataLayer pushes, and DOM mutations
6. **Build interference matrix**: Tag × Tag matrix showing potential conflicts with severity

### Interference Matrix Output Format

```
INTERFERENCE MATRIX — Tags with potential conflicts

Tag A                    ↔  Tag B                    | Type              | Severity
─────────────────────────────────────────────────────────────────────────────────────
GA4 - Config - Main      ↔  GA4 - Config - Dev       | Competing config  | CRITICAL
Meta - Base Pixel        ↔  Meta - Event - Purchase   | Pixel ID mismatch | HIGH
GAds - Conv - Purchase   ↔  GAds - Conv - Purchase2   | Duplicate conv    | HIGH
CJS - Set User ID        ↔  CJS - Reset Session       | DataLayer race    | HIGH
GA4 - Event - Purchase   ↔  GA4 - Event - Transaction | Same event, same dest | HIGH
```

## Cross-Reference Checks

These are structural analyses that support both the category checks and conflict detection:

| ID | Check | Description |
|----|-------|-------------|
| X01 | Build tag-trigger map | Map every tag to its firing triggers and blocking triggers |
| X02 | Identify trigger reuse | Triggers used by 5+ tags may be too broad |
| X03 | Variable dependency chain | Variables that reference other variables — check for circular refs |
| X04 | Consent coverage matrix | Matrix of every tag × consent type showing gaps |
| X05 | Vendor tag grouping | Group all tags by vendor/platform for conflict analysis |
| X06 | Destination ID extraction | Extract all measurement IDs, pixel IDs, conversion labels into a lookup table |
| X07 | Shared trigger analysis | For each trigger, list all tags that use it — flag where order matters |
| X08 | DataLayer write map | For Custom HTML tags, identify all `dataLayer.push()` calls and global variable assignments |
