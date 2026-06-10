#!/bin/bash
#
# One-shot setup for the Local RAG POC on a fresh Mac.
# Installs Homebrew, Python, and the GitHub CLI, clones the repo,
# creates the virtualenv, configures .env, and starts the server.
#
# Usage (from any terminal, no prerequisites):
#   curl -fsSL https://raw.githubusercontent.com/anandptl84/local-rag-poc/main/setup.sh | bash
#
# Safe to re-run: every step skips work that is already done.

set -euo pipefail

REPO_URL="https://github.com/anandptl84/local-rag-poc.git"
PROJECT_DIR="${RAG_HOME:-$HOME/local-rag-poc}"
PYTHON_FORMULA="python@3.12"
PYTHON_BIN="python3.12"

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }

# stdin may be the curl pipe, so interactive prompts must go through /dev/tty
has_tty() { [[ -r /dev/tty && -w /dev/tty ]]; }

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script is for macOS only." >&2
  exit 1
fi

step "Checking for Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  # Apple Silicon installs to /opt/homebrew, Intel to /usr/local
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
fi
if ! command -v brew >/dev/null 2>&1; then
  echo "Installing Homebrew (this also installs the Xcode Command Line Tools)."
  echo "You may be asked for your Mac login password."
  if has_tty; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/tty
  else
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  else
    eval "$(/usr/local/bin/brew shellenv)"
  fi
  # make brew available in future terminal sessions too
  if ! grep -qs 'brew shellenv' "$HOME/.zprofile"; then
    echo "eval \"\$($(command -v brew) shellenv)\"" >> "$HOME/.zprofile"
  fi
fi
echo "Homebrew: $(brew --version | head -1)"

step "Installing Python and the GitHub CLI"
brew list "$PYTHON_FORMULA" >/dev/null 2>&1 || brew install "$PYTHON_FORMULA"
brew list gh >/dev/null 2>&1 || brew install gh
echo "Python: $("$PYTHON_BIN" --version)"

step "Logging in to GitHub"
if gh auth status >/dev/null 2>&1; then
  echo "Already logged in."
elif has_tty; then
  echo "A browser window will open; follow the prompts to log in."
  gh auth login --hostname github.com --git-protocol https </dev/tty >/dev/tty 2>&1
else
  echo "No terminal available for login; skipping. Run 'gh auth login' later to push changes."
fi
gh auth status >/dev/null 2>&1 && gh auth setup-git

step "Getting the code"
if [[ -d "$PROJECT_DIR/.git" ]]; then
  echo "Repo already cloned at $PROJECT_DIR"
else
  git clone "$REPO_URL" "$PROJECT_DIR"
fi
cd "$PROJECT_DIR"

step "Creating the Python virtual environment"
if [[ ! -x venv/bin/python ]]; then
  "$PYTHON_BIN" -m venv venv
fi
./venv/bin/pip install --quiet --upgrade pip
echo "Installing dependencies (first run takes a few minutes)..."
./venv/bin/pip install --quiet -r requirements.txt

step "Configuring .env"
if [[ -f .env ]]; then
  echo ".env already exists; leaving it as is."
else
  GEMINI_KEY=""
  if has_tty; then
    printf 'Paste your GEMINI_API_KEY (Enter to skip and fill in later): ' >/dev/tty
    IFS= read -r GEMINI_KEY </dev/tty
  fi
  cat > .env <<EOF
GEMINI_API_KEY=${GEMINI_KEY:-your_gemini_api_key_here}
GEMINI_MODEL=gemini-2.5-flash
EOF
  if [[ -z "$GEMINI_KEY" ]]; then
    echo "No key entered. The server will start, but queries will fail until you"
    echo "put a real key in $PROJECT_DIR/.env"
  fi
fi

step "Starting the server"
echo "API docs:     http://127.0.0.1:8000/docs"
echo "Health check: http://127.0.0.1:8000/health"
echo "(Press Ctrl+C to stop. Start it again any time with:"
echo "  cd $PROJECT_DIR && ./venv/bin/uvicorn app.main:app --reload)"
echo
echo "Note: the first PDF ingestion downloads the embedding model (~90 MB)."
exec ./venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
