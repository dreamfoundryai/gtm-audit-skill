# GTM Audit Skill

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill for auditing Google Tag Manager containers. Connects to the GTM API v2, evaluates 53 checks across 7 categories, generates browser test suites, ingests test results, and builds prioritized fix plans.

## What it does

- **Audit**: 53-check container audit across tag health, conflicts, triggers, consent, performance, data layer, and organization
- **Test**: Generates self-contained browser test briefs for live on-page validation
- **Results**: Parses test results into structured findings
- **Fix**: Builds prioritized remediation plans mapped to Google best practices

End-to-end workflow:

```
/gtm audit → /gtm test → [Chrome testing] → /gtm results → /gtm fix
```

## Installation

One command:

```bash
curl -fsSL https://raw.githubusercontent.com/dreamfoundryai/gtm-audit-skill/main/install.sh | bash
```

This will:
1. Clone the skill into `~/.claude/skills/gtm`
2. Create an isolated Python virtualenv at `~/.claude/skills/gtm/.venv`
3. Install all Python dependencies into that venv (no system Python pollution)
4. Verify the install

To update later, just run the same command again — it will pull the latest and reinstall deps.

<details>
<summary>Manual install</summary>

```bash
git clone https://github.com/dreamfoundryai/gtm-audit-skill.git ~/.claude/skills/gtm
bash ~/.claude/skills/gtm/install.sh
```

</details>

## Setup (first time)

The skill needs access to the Google Tag Manager API v2.

1. Create or select a Google Cloud project
2. Enable the **Tag Manager API v2**
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download `credentials.json` and place at `~/.config/gtm-audit/credentials.json`
5. In GTM (Admin → User Management), grant the OAuth account read access to the container
6. Run the OAuth flow:

```bash
python ~/.claude/skills/gtm/scripts/fetch_gtm.py --auth-only
```

Or just ask Claude: `/gtm connect`

## Usage

In Claude Code:

| Command | What it does |
|---------|--------------|
| `/gtm audit` | Full container audit (all 53 checks) |
| `/gtm connect` | Set up GTM API auth |
| `/gtm tags` | Tag-focused analysis |
| `/gtm triggers` | Trigger quality analysis |
| `/gtm variables` | Variable audit |
| `/gtm consent` | Consent Mode and privacy deep dive |
| `/gtm conflicts` | Tag conflict and interference analysis |
| `/gtm test` | Generate on-page browser test suite |
| `/gtm results` | Ingest test results |
| `/gtm fix` | Build prioritized fix plan |
| `/gtm report` | Re-generate report from cached data |

## What gets audited

53 checks across 7 weighted categories:

| Category | Weight |
|----------|--------|
| Tag Health | 20% |
| Tag Conflicts & Interference | 15% |
| Trigger Quality | 15% |
| Consent & Privacy | 20% |
| Performance & Loading | 10% |
| Data Layer & Variables | 10% |
| Container Organization | 10% |

Detects: misconfigured tags, duplicate tracking pixels, competing config tags, consent state conflicts, race conditions, orphaned triggers, naming violations, and more. See [SKILL.md](SKILL.md) for the full check list.

## Structure

```
.
├── SKILL.md                          # Skill manifest + workflow
├── scripts/
│   ├── fetch_gtm.py                  # GTM API v2 data fetcher (OAuth 2.0)
│   └── requirements.txt              # Python dependencies
└── references/
    ├── gtm-audit.md                  # 53-check audit checklist
    ├── scoring-system.md             # Weighted scoring algorithm
    ├── google-tag-best-practices.md  # Official Google guidance (21 sources)
    ├── test-generation.md            # Test brief generation rules
    ├── results-parsing.md            # Results parsing spec
    └── fix-plan-generation.md        # Fix plan templates and prioritization
```

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code)
- Python 3.9+
- Google Tag Manager API v2 access (OAuth 2.0)

## License

MIT — see [LICENSE](LICENSE)
