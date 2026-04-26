import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

UA = {"User-Agent": "OpenClaw-Porting"}

TARGETS = {
    "so_ts": {
        "repo": "SO-TS/android_kernel_xiaomi_sm8250",
        "ref": "android16-aptusitu",
    },
    "base_5plus": {"repo": "yefxx/xiaomi-umi-linux-kernel", "ref": "master"},
    # Author-ID sourced references (selected repos under UtsavBalar1231 account).
    "reference_utsav_sm8150": {
        "repo": "UtsavBalar1231/android_kernel_xiaomi_sm8150",
        "ref": "master",
    },
    "reference_utsav_display_drivers": {
        "repo": "UtsavBalar1231/display-drivers",
        "ref": "psyche-r-oss",
    },
    "reference_utsav_camera_kernel": {
        "repo": "UtsavBalar1231/camera-kernel",
        "ref": "main",
    },
}

AUTHOR_IDS = ["UtsavBalar1231", "liyafe1997"]
DISCOVERY_KEYWORDS = ["kernel", "driver", "sm8250", "xiaomi", "camera", "display"]

PATHS = ["arch/arm64/configs", "arch/arm64/boot/dts", "techpack", "drivers"]


def api(url: str) -> Any:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def list_dir_via_git(repo: str, ref: str, path: str) -> list[str]:
    """Fallback when GitHub API is rate-limited/blocked."""
    with tempfile.TemporaryDirectory(prefix="oc-inv-") as td:
        url = f"https://github.com/{repo}.git"
        try:
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    ref,
                    "--filter=blob:none",
                    url,
                    td,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p = Path(td) / path
            if not p.exists() or not p.is_dir():
                return []
            return sorted(x.name for x in p.iterdir())
        except Exception:
            return []


def list_dir(repo: str, ref: str, path: str):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    try:
        data = api(url)
        if isinstance(data, list):
            return [x["name"] for x in data], "api"
        return [], "api"
    except Exception:
        return list_dir_via_git(repo, ref, path), "git-fallback"


def discover_user_repos(
    user: str, keyword_filters: list[str]
) -> tuple[list[dict[str, str]], str]:
    """Best-effort account scan used to document whether a requested user has relevant public repos."""
    url = f"https://api.github.com/users/{urllib.parse.quote(user)}/repos?per_page=100"
    try:
        data = api(url)
        if not isinstance(data, list):
            return [], "api-nonlist"
        out: list[dict[str, str]] = []
        for r in data:
            name = str(r.get("name", ""))
            low = name.lower()
            if any(k in low for k in keyword_filters):
                out.append(
                    {
                        "name": name,
                        "full_name": str(r.get("full_name", "")),
                        "default_branch": str(r.get("default_branch", "")),
                        "html_url": str(r.get("html_url", "")),
                    }
                )
        return out, "api"
    except Exception:
        return [], "api-error"


def main():
    out: dict[str, Any] = {}
    for name, cfg in TARGETS.items():
        out[name] = {"repo": cfg["repo"], "ref": cfg["ref"], "fetch_mode": {}}
        for p in PATHS:
            vals, mode = list_dir(cfg["repo"], cfg["ref"], p)
            out[name][p] = vals
            out[name]["fetch_mode"][p] = mode

    discovery: dict[str, Any] = {"fetch_mode": {}}
    seen_authors: set[str] = set()
    for author in AUTHOR_IDS:
        key = author.strip().lower()
        if not key or key in seen_authors:
            continue
        seen_authors.add(key)
        rows, mode = discover_user_repos(author, DISCOVERY_KEYWORDS)
        discovery[author] = rows
        discovery["fetch_mode"][author] = mode

    out["reference_discovery"] = discovery

    out["meta"] = {
        "generator": "Porting/Tools/FetchInventory.py",
        "cwd": os.getcwd(),
    }

    with open("Porting/Inventory.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote Porting/Inventory.json")


if __name__ == "__main__":
    main()
