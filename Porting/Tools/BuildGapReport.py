import json
import urllib.request
from pathlib import Path

UA = {"User-Agent": "OpenClaw-Porting"}

SO_REPO = "SO-TS/android_kernel_xiaomi_sm8250"
SO_REF = "android16-aptusitu"
BASE_REPO = "yefxx/xiaomi-umi-linux-kernel"
BASE_REF = "master"


def api(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def list_dir(repo: str, ref: str, path: str):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    data = api(url)
    if isinstance(data, list):
        return data
    return []


def names(repo: str, ref: str, path: str):
    try:
        return [x["name"] for x in list_dir(repo, ref, path)]
    except Exception:
        return []


def main():
    so_cfg = names(SO_REPO, SO_REF, "arch/arm64/configs")
    base_cfg = names(BASE_REPO, BASE_REF, "arch/arm64/configs")

    so_umi_like = sorted(
        [
            x
            for x in so_cfg
            if x.endswith("_defconfig")
            and any(k in x for k in ["umi", "lmi", "cmi", "apollo", "alioth", "thyme"])
        ]
    )
    base_umi_like = sorted(
        [
            x
            for x in base_cfg
            if x.endswith("_defconfig")
            and any(k in x for k in ["umi", "lmi", "cmi", "apollo", "alioth", "thyme"])
        ]
    )

    # SO-TS primarily keeps Qualcomm device trees under dts/vendor/qcom
    so_qcom = names(SO_REPO, SO_REF, "arch/arm64/boot/dts/vendor/qcom")
    base_qcom = names(BASE_REPO, BASE_REF, "arch/arm64/boot/dts/qcom")

    so_umi_dts = sorted(
        [
            x
            for x in so_qcom
            if any(
                k in x
                for k in [
                    "sm8250",
                    "umi",
                    "xiaomi",
                    "kona",
                    "lmi",
                    "cmi",
                    "apollo",
                    "alioth",
                    "thyme",
                ]
            )
        ]
    )
    base_umi_dts = sorted(
        [
            x
            for x in base_qcom
            if any(
                k in x
                for k in [
                    "sm8250",
                    "umi",
                    "xiaomi",
                    "kona",
                    "lmi",
                    "cmi",
                    "apollo",
                    "alioth",
                    "thyme",
                ]
            )
        ]
    )

    so_techpack = names(SO_REPO, SO_REF, "techpack")
    base_techpack = names(BASE_REPO, BASE_REF, "techpack")

    report = []
    report.append("# Gap Report (SO-TS 4.19 -> 5+ Base)\n")
    report.append("## Defconfig\n")
    report.append(f"- SO-TS umi-like defconfigs: {len(so_umi_like)}")
    report.append(f"- 5+ base umi-like defconfigs: {len(base_umi_like)}")
    report.append(
        "- SO-TS list: " + (", ".join(so_umi_like) if so_umi_like else "(none)")
    )
    report.append(
        "- 5+ list: " + (", ".join(base_umi_like) if base_umi_like else "(none)")
    )

    report.append("\n## DTS/QCOM focus\n")
    report.append(f"- SO-TS qcom umi/sm8250/xiaomi related files: {len(so_umi_dts)}")
    report.append(
        f"- 5+ base qcom umi/sm8250/xiaomi related files: {len(base_umi_dts)}"
    )
    report.append(
        "- SO-TS sample: " + (", ".join(so_umi_dts[:20]) if so_umi_dts else "(none)")
    )
    report.append(
        "- 5+ sample: " + (", ".join(base_umi_dts[:20]) if base_umi_dts else "(none)")
    )

    report.append("\n## Techpack\n")
    report.append(f"- SO-TS techpack entries: {len(so_techpack)}")
    report.append(f"- 5+ base techpack entries: {len(base_techpack)}")
    if so_techpack:
        report.append("- SO-TS techpack dirs: " + ", ".join(so_techpack))
    if not base_techpack:
        report.append(
            "- 5+ base has no top-level techpack (expected: mainline-style drivers split)."
        )

    report.append("\n## Migration implication\n")
    report.append(
        "- Need to create/port umi defconfig in 5+ base before feature migration."
    )
    report.append(
        "- DTS migration should start from sm8250-xiaomi-* subset, not full tree copy."
    )
    report.append(
        "- Techpack features require subsystem-by-subsystem adaptation into 5+ driver layout."
    )

    out = Path("Porting/GapReport.md")
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
