import argparse, json, os, shutil, hashlib, sys, datetime
from pathlib import Path

PHASES = ["preseed", "seed", "series-a", "series-b"]

def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def list_files(base: Path):
    for p in sorted(base.rglob("*")):
        if p.is_file():
            yield p

def render_placeholders(text: str, phase: str, cloud: str, region: str) -> str:
    return (text
        .replace("{{PHASE}}", phase)
        .replace("{{CLOUD}}", cloud)
        .replace("{{REGION}}", region)
        .replace("{{GENERATED_AT}}", datetime.datetime.utcnow().isoformat() + "Z")
    )

def copy_template(template_dir: Path, out_bundle: Path, phase: str, cloud: str, region: str):
    if out_bundle.exists():
        shutil.rmtree(out_bundle)
    shutil.copytree(template_dir, out_bundle)

    # render placeholders in text-ish files
    for p in list_files(out_bundle):
        if p.suffix.lower() in [".tf", ".md", ".yml", ".yaml", ".json", ".rego", ".txt"]:
            try:
                raw = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            p.write_text(render_placeholders(raw, phase, cloud, region), encoding="utf-8")

def make_manifest(out_root: Path, phase: str, cloud: str, region: str):
    bundle = out_root / "bundle"
    evidence = out_root / "EVIDENCE"
    files = []

    for p in list_files(bundle):
        rel = str(p.relative_to(out_root)).replace("\\\\", "/")
        files.append({"path": rel, "sha256": sha256_file(p)})

    if evidence.exists():
        for p in list_files(evidence):
            rel = str(p.relative_to(out_root)).replace("\\\\", "/")
            files.append({"path": rel, "sha256": sha256_file(p)})

    manifest = {
        "name": "startup-terraform-phases",
        "profile": "EVALUATION",
        "phase": phase,
        "cloud": cloud,
        "region": region,
        "generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "files": files,
    }
    (out_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def write_demo_evidence(out_root: Path, phase: str, cloud: str, region: str):
    # Demo-only evidence (no real terraform run, no credentials)
    evidence = out_root / "EVIDENCE"
    if phase in ["series-a", "series-b"]:
        evidence.mkdir(parents=True, exist_ok=True)

        plan_stub = {
            "demo": True,
            "note": "EVAL stub evidence. Not a real terraform plan.",
            "phase": phase,
            "cloud": cloud,
            "region": region,
            "generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "checks": [
                {"id": "tags_required", "status": "pass", "required": ["owner", "purpose", "risk", "cost_center"]},
                {"id": "region_guardrails", "status": "pass", "mode": "allowlist"},
            ]
        }
        (evidence / "plan.json").write_text(json.dumps(plan_stub, indent=2), encoding="utf-8")

    if phase == "series-b":
        policy_report = {
            "demo": True,
            "note": "EVAL stub policy report (OPA/Conftest hook demo).",
            "phase": phase,
            "result": "pass",
            "policies": [
                {"policy": "deny_missing_tags", "result": "pass"},
                {"policy": "deny_disallowed_regions", "result": "pass"},
            ]
        }
        (evidence / "policy_report.json").write_text(json.dumps(policy_report, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(prog="startup-terraform-phases")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("generate", help="Generate a phase bundle into /out")
    g.add_argument("--phase", required=True, choices=PHASES)
    g.add_argument("--cloud", required=True)
    g.add_argument("--region", required=True)
    g.add_argument("--out", default="/out")

    args = ap.parse_args()

    if args.cmd != "generate":
        ap.print_help()
        sys.exit(1)

    phase = args.phase.strip()
    cloud = args.cloud.strip().lower()
    region = args.region.strip()

    # FAIL-CLOSED constraints for EVAL
    if cloud != "aws":
        fail("EVAL constraint: --cloud must be 'aws'")

    if not region:
        fail("Missing --region")

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    template_dir = Path("/app/templates") / phase
    if not template_dir.exists():
        fail(f"Missing template for phase: {phase}")

    out_bundle = out_root / "bundle"
    copy_template(template_dir, out_bundle, phase, cloud, region)
    write_demo_evidence(out_root, phase, cloud, region)
    make_manifest(out_root, phase, cloud, region)

    print(f"OK: generated phase='{phase}' to {out_root}")

if __name__ == "__main__":
    main()