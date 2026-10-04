"""Create an ignored local .env with random development secrets."""

import secrets
from pathlib import Path

root = Path(__file__).resolve().parent.parent
target = root / ".env"
if target.exists():
    raise SystemExit(".env already exists; leaving it unchanged")
content = (root / ".env.example").read_text()
for placeholder in (
    "replace-with-local-password",
    "replace-with-a-random-secret",
    "replace-with-local-admin-password",
):
    content = content.replace(placeholder, secrets.token_urlsafe(48))
target.write_text(content)
target.chmod(0o600)
print("Created .env with development secrets. ADMIN_PASSWORD is available in that file.")
