#!/bin/sh
# Oneshotted skill: install it for your coding agents and sign in, in one go.
#   curl -fsSL https://oneshotted.io/install.sh | sh
# What it does (nothing else, no sudo):
#   1. downloads the skill (a tagged release of https://github.com/GovarJabbar/oneshotted-skill)
#   2. installs it for the agents the `skills` CLI finds (Claude Code, Codex, Cursor...), or into
#      ~/.claude/skills/oneshotted when Node isn't available (ONESHOTTED_NO_NPX=1 skips the CLI)
#   3. signs you in to Oneshotted in your browser (a free account works), unless you already are
#      or ONESHOTTED_API_KEY is set
# The whole script is one function, run on the last line: a cut-off download runs nothing.
set -eu

main() {
  REPO="GovarJabbar/oneshotted-skill"
  REF="${ONESHOTTED_REF:-v0.1.0}"
  TARBALL="https://codeload.github.com/$REPO/tar.gz/refs/tags/$REF"
  CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
  CONF="$HOME/.config/oneshotted"

  say() { printf '%s\n' "$*"; }
  need() { command -v "$1" >/dev/null 2>&1 || { say "oneshotted: $1 is required. $2"; exit 1; }; }
  need curl ""
  need tar ""
  need python3 "Install Python 3.9+ (https://www.python.org/downloads/) and run this again."
  python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' || { say "oneshotted: Python 3.9 or newer is needed (python3 is $(python3 -V 2>&1))."; exit 1; }

  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  say "Downloading the Oneshotted skill ($REF)..."
  curl -fsSL "$TARBALL" | tar -xz -C "$tmp"
  src=$(find "$tmp" -maxdepth 4 -type d -path '*/skills/oneshotted' | head -n 1)
  [ -n "$src" ] && [ -f "$src/SKILL.md" ] || { say "oneshotted: the download looks incomplete. Try again."; exit 1; }

  # Claude Code's folder first, so the skills CLI detects it instead of installing into every agent it knows.
  mkdir -p "$CLAUDE_DIR/skills"
  how=""
  if [ -z "${ONESHOTTED_NO_NPX:-}" ] && command -v npx >/dev/null 2>&1; then
    say "Installing for your coding agents with the skills CLI (npx skills@1.7.0)..."
    if npx -y skills@1.7.0 add "$REPO#$REF" -g -y </dev/null >"$tmp/npx.log" 2>&1; then
      how="for your coding agents (skills CLI)"
    else
      say "The skills CLI didn't finish (log below); installing for Claude Code directly."
      tail -n 5 "$tmp/npx.log" | sed 's/^/  /'
    fi
  fi
  # Claude Code always has it. Never replace the CLI's own link (npx skills update keeps that one current).
  if [ ! -f "$CLAUDE_DIR/skills/oneshotted/SKILL.md" ]; then
    rm -rf "$CLAUDE_DIR/skills/oneshotted"
    cp -R "$src" "$CLAUDE_DIR/skills/oneshotted"
  fi
  say "Installed ${how:-in $CLAUDE_DIR/skills/oneshotted}."

  lib="$CLAUDE_DIR/skills/oneshotted/scripts/library.py"
  say ""
  if [ -n "${ONESHOTTED_API_KEY:-}" ] || [ -f "$CONF/key" ]; then
    say "Using your Oneshotted API key: no sign-in needed."
  elif [ -f "$CONF/token.json" ]; then
    say "Already signed in to Oneshotted."
  elif [ -n "${SSH_CONNECTION:-}" ] || { [ "$(uname -s)" = Linux ] && [ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && ! grep -qi microsoft /proc/version 2>/dev/null; }; then
    say "No browser here (SSH or headless). Sign in with an API key instead:"
    say "  1. get a free key at https://oneshotted.io/mcp-docs"
    say "  2. export ONESHOTTED_API_KEY=osk_...   (add it to your shell profile)"
  else
    say "Now sign in (opens your browser; a free account works)."
    python3 "$lib" login </dev/null || {
      say "Sign-in didn't finish. The skill is installed; sign in any time with:"
      say "  python3 $lib login"
      say "or use an API key from https://oneshotted.io/mcp-docs"
    }
  fi

  say ""
  say "Done. Ask your agent for a video, e.g.:"
  say "  \"Make a 15-second launch video for my app. It has to grab people in the first second.\""
}

main "$@"
