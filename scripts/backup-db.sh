#!/usr/bin/env bash
# Backs up backend/recipe_vault.db + backend/uploads/ to the private
# recipe-vault-backup GitHub repo, since the codespace itself is ephemeral.
#
# Requires a fine-grained GitHub PAT (Contents: Read+Write on
# recipe-vault-backup only) saved at ~/.config/recipe-vault-backup/token.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
DB_FILE="$BACKEND_DIR/recipe_vault.db"
UPLOADS_DIR="$BACKEND_DIR/uploads"

BACKUP_REMOTE="https://github.com/mwernimont/recipe-vault-backup.git"
BACKUP_DIR="$HOME/.recipe-vault-backup-clone"
TOKEN_FILE="$HOME/.config/recipe-vault-backup/token"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "Missing backup token at $TOKEN_FILE" >&2
  exit 1
fi
if [[ ! -f "$DB_FILE" ]]; then
  echo "No DB found at $DB_FILE" >&2
  exit 1
fi

TOKEN="$(<"$TOKEN_FILE")"
AUTH_HEADER="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)"

if [[ ! -d "$BACKUP_DIR/.git" ]]; then
  git -c http.extraHeader="$AUTH_HEADER" clone "$BACKUP_REMOTE" "$BACKUP_DIR"
else
  git -C "$BACKUP_DIR" -c http.extraHeader="$AUTH_HEADER" pull --ff-only
fi

# Consistent snapshot even if the app is running and mid-write.
sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/recipe_vault.db'"

mkdir -p "$BACKUP_DIR/uploads"
rsync -a --delete "$UPLOADS_DIR/" "$BACKUP_DIR/uploads/"

cd "$BACKUP_DIR"
git add -A

if git diff --cached --quiet; then
  echo "No changes since last backup."
  exit 0
fi

git commit -q -m "Backup $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
git -c http.extraHeader="$AUTH_HEADER" push origin HEAD
echo "Backup pushed to recipe-vault-backup."
