import json
import urllib.request

UA = {"User-Agent": "OpenClaw-Porting"}

TARGETS = {
    "so_ts": {
        "repo": "SO-TS/android_kernel_xiaomi_sm8250",
        "ref": "android16-aptusitu",
    },
    "base_5plus": {
        "repo": "yefxx/xiaomi-umi-linux-kernel",
        "ref": "master",
    },
}

PATHS = [
    "arch/arm64/configs",
    "arch/arm64/boot/dts",
    "techpack",
    "drivers",
]


def api(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def list_dir(repo: str, ref: str, path: str):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    try:
        data = api(url)
        if isinstance(data, list):
            return [x["name"] for x in data]
        return []
    except Exception:
        return []


def main():
    out = {}
    for name, cfg in TARGETS.items():
        out[name] = {}
        for p in PATHS:
            out[name][p] = list_dir(cfg["repo"], cfg["ref"], p)

    with open("Porting/Inventory.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote Porting/Inventory.json")


if __name__ == "__main__":
    main()
