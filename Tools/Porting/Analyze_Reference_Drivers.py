import json
from pathlib import Path
from typing import Iterable

INVENTORY = Path("Porting/Inventory.json")
OUT = Path("Porting/Reference-Drivers-Analysis.md")


def as_set(obj: dict, key: str) -> set[str]:
    val = obj.get(key, [])
    if isinstance(val, list):
        return {str(x) for x in val}
    return set()


def fmt_list(items: Iterable[str], limit: int = 30) -> str:
    arr = sorted(items)
    if not arr:
        return "(none)"
    cut = arr[:limit]
    suffix = "" if len(arr) <= limit else f" ... (+{len(arr)-limit} more)"
    return ", ".join(cut) + suffix


def main() -> int:
    if not INVENTORY.exists():
        print("inventory missing; run Tools/Porting/Fetch_Inventory.py first")
        return 1

    data = json.loads(INVENTORY.read_text(encoding="utf-8"))

    so = data.get("so_ts", {})
    base = data.get("base_5plus", {})
    r1 = data.get("reference_utsav_sm8150", {})
    r2 = data.get("reference_utsav_display_drivers", {})
    r3 = data.get("reference_utsav_camera_kernel", {})

    so_drv = as_set(so, "drivers")
    base_drv = as_set(base, "drivers")
    ref_drv = as_set(r1, "drivers") | as_set(r2, "drivers") | as_set(r3, "drivers")

    # Driver directories present in references but absent in current 5+ base.
    ref_missing_in_base = ref_drv - base_drv

    # UMI-relevant candidate focus buckets.
    focus = {
        x
        for x in ref_missing_in_base
        if any(k in x for k in ["xiaomi", "camera", "video", "display", "touch", "sensor", "soc", "gpu", "thermal"])
    }

    strawing_hits = data.get("reference_discovery", {}).get("Strawing", [])

    lines: list[str] = []
    lines.append("# Reference Driver Analysis (Author IDs: UtsavBalar1231 / Strawing)")
    lines.append("")
    lines.append("This report compares additional reference repositories against the current 5+ base driver layout.")
    lines.append("")
    lines.append("## Sources")
    lines.append(f"- so_ts drivers: {len(so_drv)}")
    lines.append(f"- base_5plus drivers: {len(base_drv)}")
    lines.append(f"- utsav combined reference drivers: {len(ref_drv)}")
    lines.append("")
    lines.append("## Driver Delta")
    lines.append(f"- reference-only (missing in base): {len(ref_missing_in_base)}")
    lines.append(f"- sample: {fmt_list(ref_missing_in_base)}")
    lines.append("")
    lines.append("## UMI Integration Focus (prioritized buckets)")
    lines.append(f"- focus count: {len(focus)}")
    lines.append(f"- focus buckets: {fmt_list(focus)}")
    lines.append("")
    lines.append("## Strawing Discovery")
    if isinstance(strawing_hits, list) and len(strawing_hits) > 0:
        lines.append(f"- matched public repos: {len(strawing_hits)}")
        for i in strawing_hits[:20]:
            lines.append(f"  - {i.get('full_name', '')} ({i.get('default_branch', '')})")
    else:
        lines.append("- matched public repos: 0 (no public kernel/driver repos detected at scan time)")
    lines.append("")
    lines.append("## Actionable Integration Plan")
    lines.append("1. Keep source of truth as `so_ts` + `base_5plus`; treat extra references as donor-only for driver ideas.")
    lines.append("2. Prioritize buckets in this order: `xiaomi` -> `camera/video` -> `thermal/power` -> other subsystems.")
    lines.append("3. For each borrowed driver area, require: Kconfig mapping, DTS binding compatibility, and build gate in CI.")
    lines.append("4. Avoid blind subtree copy; port only device-required deltas and validate with runtime checklist.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
