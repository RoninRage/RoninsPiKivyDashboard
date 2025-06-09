import os
import sys
import shutil
import tarfile
import tempfile
import datetime
import requests
from kivy.app import App


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
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Optional: Backup bestehender Dateien
        if backup:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(current_dir, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            if status_callback:
                status_callback(f"📦 Creating backup at {backup_dir}")
            for item in os.listdir(current_dir):
                if (
                    item.startswith("backup_")
                    or item == "__pycache__"
                    or item == os.path.basename(__file__)
                ):
                    continue
                src = os.path.join(current_dir, item)
                dst = os.path.join(backup_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

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
