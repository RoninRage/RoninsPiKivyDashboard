import os
import sys
import shutil
import tarfile
import tempfile
import datetime
import requests
from pathlib import Path
from kivy.app import App


def cleanup_old_backups(backup_root: Path, keep: int = 5):
    backups = sorted(
        [d for d in backup_root.glob("backup_*") if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    for old_backup in backups[keep:]:
        try:
            shutil.rmtree(old_backup)
            print(f"[Cleanup] Removed old backup: {old_backup.name}")
        except Exception as e:
            print(f"[Cleanup] Failed to remove {old_backup.name}: {e}")


def download_and_apply_update(url: str, status_callback=None, backup=True):
    try:
        if status_callback:
            status_callback("⬇ Downloading update...")

        temp_dir = tempfile.mkdtemp()
        archive_path = os.path.join(temp_dir, "update.tar.gz")

        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(temp_dir)

        extracted_root = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        current_dir = Path(__file__).parent.resolve()

        # Optional: Backup bestehender Dateien
        if backup:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = current_dir / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            if status_callback:
                status_callback(f"📦 Creating backup at {backup_dir}")
            for item in current_dir.iterdir():
                if (
                    item.name.startswith("backup_")
                    or item.name == "__pycache__"
                    or item.name == Path(__file__).name
                ):
                    continue
                dst = backup_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)

            # 🧹 Cleanup: nur letzte 5 Backups behalten
            cleanup_old_backups(current_dir, keep=5)

        # Kopieren der neuen Dateien
        for item in os.listdir(extracted_root):
            src = os.path.join(extracted_root, item)
            dst = os.path.join(current_dir, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        if status_callback:
            status_callback("✅ Update applied. Restarting...")
        App.get_running_app().stop()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        if status_callback:
            status_callback(f"❌ Update failed: {e}")
