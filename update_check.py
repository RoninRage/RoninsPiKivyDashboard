import requests
from packaging import version
from pathlib import Path

# === Konfiguration ===
GITHUB_OWNER = "RoninRage"
GITHUB_REPO = "RoninsPiKivyDashboard"
RELEASE_API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)


def get_local_version() -> str:
    version_file = Path(__file__).parent / "version.txt"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.0.0"


def get_latest_version_info() -> tuple[str, str]:
    try:
        response = requests.get(RELEASE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        tag = data.get("tag_name", "").lstrip("v")
        asset_url = ""
        for asset in data.get("assets", []):
            if asset["name"].endswith(".tar.gz"):
                asset_url = asset["browser_download_url"]
                break
        return tag, asset_url
    except requests.RequestException as e:
        print(f"[Update Check] Failed to fetch release info: {e}")
        return "0.0.0", ""


def is_update_available() -> tuple[bool, str, str]:
    local_ver = get_local_version()
    remote_ver, download_url = get_latest_version_info()
    if version.parse(remote_ver) > version.parse(local_ver):
        return True, remote_ver, download_url
    return False, remote_ver, ""


# === Beispielnutzung ===
if __name__ == "__main__":
    available, new_version, url = is_update_available()
    if available:
        print(f"🔔 Update available: v{new_version}")
        print(f"⬇️  Download: {url}")
    else:
        print("✅ Already up to date.")
