"""
💾 Backup & Restore — one file with all your Nanban data (memory, to-dos, settings).

Create a backup zip you can download and keep; restore it on the same or another laptop.
Only your personal data is included — no code, no secrets beyond your own settings.
"""

import time
import zipfile
from pathlib import Path

import config

_INCLUDE_SUFFIX = {".json", ".jsonl", ".md", ".txt", ".index", ".npy"}


def make_backup() -> str:
    """Create a backup zip of the data folder and return its path (for download)."""
    bdir = config.DATA_DIR / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = bdir / f"nanban-backup-{stamp}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in config.DATA_DIR.rglob("*"):
            if p.is_file() and "backups" not in p.parts and p.suffix.lower() in _INCLUDE_SUFFIX:
                z.write(p, p.relative_to(config.DATA_DIR).as_posix())
        # also back up any documents the user uploaded for Study mode
        for p in config.DOCUMENTS_DIR.rglob("*"):
            if p.is_file():
                z.write(p, ("documents/" + p.relative_to(config.DOCUMENTS_DIR).as_posix()))
    return str(path)


def restore_backup(file_path) -> str:
    """Extract a backup zip back into the data / documents folders."""
    if not file_path:
        return "Pick a backup .zip first."
    try:
        src = Path(file_path if isinstance(file_path, str) else file_path.name)
        with zipfile.ZipFile(src) as z:
            for member in z.namelist():
                if member.startswith("documents/"):
                    z.extract(member, config.BASE_DIR)          # -> documents/
                else:
                    z.extract(member, config.DATA_DIR)          # -> data/
        return "✅ Restored your memory, to-dos, settings and documents. **Restart Nanban** to load it all."
    except Exception as e:
        return f"⚠️ Restore failed: {e}. Make sure it's a Nanban backup .zip."
