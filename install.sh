#!/usr/bin/env bash
#
# GTM Audit Skill — installer
#
# Installs the skill into ~/.claude/skills/gtm and sets up an isolated
# Python virtualenv with all dependencies.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dreamfoundryai/gtm-audit-skill/main/install.sh | bash
#
# Or, from a local clone:
#   ./install.sh
#

set -euo pipefail

REPO_URL="https://github.com/dreamfoundryai/gtm-audit-skill.git"
SKILL_DIR="${HOME}/.claude/skills/gtm"
VENV_DIR="${SKILL_DIR}/.venv"

color() { printf "\033[%sm%s\033[0m\n" "$1" "$2"; }
info()  { color "1;34" "==> $1"; }
ok()    { color "1;32" "  ✓ $1"; }
warn()  { color "1;33" "  ! $1"; }
fail()  { color "1;31" "  ✗ $1"; exit 1; }

# 1. Pre-flight
info "Checking prerequisites"
command -v git >/dev/null 2>&1 || fail "git is required but not installed"
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3.9 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done
[ -n "$PYTHON_BIN" ] || fail "Python 3.9+ is required but not found"
ok "Using $($PYTHON_BIN --version) at $(command -v $PYTHON_BIN)"

# 2. Clone or update
mkdir -p "${HOME}/.claude/skills"
if [ -d "$SKILL_DIR/.git" ]; then
  info "Updating existing install at $SKILL_DIR"
  git -C "$SKILL_DIR" pull --ff-only --quiet
  ok "Repo updated"
elif [ -d "$SKILL_DIR" ] && [ "$(ls -A "$SKILL_DIR" 2>/dev/null)" ]; then
  # Local run from inside the repo: skip clone
  if [ -f "$SKILL_DIR/SKILL.md" ] && [ -f "$SKILL_DIR/scripts/fetch_gtm.py" ]; then
    ok "Skill files already in place at $SKILL_DIR"
  else
    fail "$SKILL_DIR exists but is not a valid skill install. Move it aside and re-run."
  fi
else
  info "Cloning skill into $SKILL_DIR"
  git clone --quiet "$REPO_URL" "$SKILL_DIR"
  ok "Cloned"
fi

# 3. Create venv
info "Setting up Python virtualenv at $VENV_DIR"
if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  ok "Virtualenv created"
else
  ok "Virtualenv already exists"
fi

# 4. Install deps
info "Installing Python dependencies"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SKILL_DIR/scripts/requirements.txt"
ok "Dependencies installed"

# 5. Verify
info "Verifying install"
if "$VENV_DIR/bin/python" -c "import googleapiclient, google_auth_oauthlib" 2>/dev/null; then
  ok "Python modules importable"
else
  fail "Dependency verification failed"
fi

if [ -x "$SKILL_DIR/scripts/fetch_gtm.py" ]; then
  ok "fetch_gtm.py executable"
else
  chmod +x "$SKILL_DIR/scripts/fetch_gtm.py" 2>/dev/null || true
fi

cat <<EOF

$(color "1;32" "✓ GTM Audit Skill installed")

Skill location: $SKILL_DIR
Python venv:    $VENV_DIR

Next steps:
  1. In Claude Code, run:  /gtm connect
     (this walks you through Google Tag Manager API setup)

  2. Then:  /gtm audit

For manual auth:
  $VENV_DIR/bin/python $SKILL_DIR/scripts/fetch_gtm.py --auth-only

EOF
