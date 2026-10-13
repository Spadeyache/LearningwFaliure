"""Seven matched conditions per seed, with optional controlled full-episode retries."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

import numpy as np

from . import SCHEMA_VERSION
from .environment import CollectionEnv, normalized_properties
from .residuals import build_residual
from .schema import describe, save_episode, validate_episode


def matched_conditions(base_properties):
    from .collect import digest
    base = normalized_properties(base_properties)
    if base["static_friction"] <= 0 or base["dynamic_friction"] <= 0:
        raise ValueError("Matched friction factors require positive baseline coefficients")
    if base["inertia_principal_kg_m2"] is not None:
        raise ValueError("Mass sweeps use density changes: omit explicit inertia so it scales with mass")
    conditions = []
    for variable, magnitude in [("none", 1.0)] + [(v, m) for v in ("mass", "friction") for m in (0.5, 2.0, 4.0)]:
        properties = dict(base)
        keys = {"none": (), "mass": ("mass_kg",), "friction": ("static_friction", "dynamic_friction")}[variable]
        for key in keys:
            properties[key] *= magnitude
        properties = normalized_properties(properties)
        conditions.append({"condition_index": len(conditions), "condition_id": digest(properties)[:16],
                           "shifted_variable": variable, "shift_magnitude": magnitude,
                           "properties": properties})
    return conditions


def force_evidence(data):
    """Check both object-contact forces while the simulator reports a grasp."""
    force = np.asarray(data["sim__object_pair_force_peak_norm_n"])
    grasp = np.asarray(data["sim__is_grasped"], dtype=bool)[1:]
    if force.shape != (len(grasp), 2) or not np.isfinite(force).all():
        raise ValueError("Invalid contact-force recording")
    return {"grasp_samples": int(grasp.sum()), "peak_contact_force_n": float(force.max()),
            "nonzero_during_grasp": bool(np.any(np.all(force[grasp] > 1e-6, axis=1))),
            "grasp_sample_peak_per_finger_n": force[grasp].max(axis=0).tolist() if grasp.any() else [0., 0.]}


def _load(path):
    with np.load(path, allow_pickle=False) as saved:
        validate_episode(saved)
        return {key: saved[key] for key in saved.files}


def _identity(data, fingerprint, episode_id, condition, seed):
    if (str(data["meta__run_fingerprint"]) != fingerprint or str(data["meta__episode_id"]) != episode_id
            or int(data["label__seed"]) != seed or str(data["meta__condition_id"]) != condition["condition_id"]):
        raise ValueError("Existing episode has mismatched identity")


def collect_matched(args, config, conditions, policy, policy_info):
    from .collect import ROOT, check_replay, digest, rollout, runtime_metadata, write_json
    from .recovery import recovery_capability, recovery_result
    total = len(conditions) * len(config["seeds"])
    limit = min(total, args.max_episodes or total)
    runtime = runtime_metadata()
    contract = {"schema_version": SCHEMA_VERSION, "config": config, "policy": policy_info, "runtime": runtime}
    fingerprint = digest(contract)
    output = (args.output or ROOT / "runs/failure_collection" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")).resolve()
    if args.resume:
        manifest = json.loads((output / "manifest.json").read_text())
        if manifest["run_fingerprint"] != fingerprint:
            raise ValueError("Resume refused: config, policy, source, or runtime differs from saved run")
        for partial in output.rglob("*.npz.tmp"):
            partial.unlink()
    else:
        output.mkdir(parents=True, exist_ok=False)
        manifest = {**contract, "run_fingerprint": fingerprint, "planned_episodes": total,
                    "conditions": conditions, "created_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "collecting", "retry_budget_is_additional": True,
                    "experiment_semantics": "One property family shifted; same seeded initial state, goal and deterministic closed-loop policy. Mass also scales inertia. Friction changes object static/dynamic coefficients, with finger/table materials fixed."}
        write_json(output / "manifest.json", manifest)
        saved_config = {key: value for key, value in config.items()
                        if key != "seeds" or "seed_count" not in config}
        write_json(output / "config.json", saved_config)
        snapshot = output / "source_snapshot"
        snapshot.mkdir()
        for source in Path(__file__).parent.glob("*.py"):
            shutil.copy2(source, snapshot / source.name)
    print(f"Output: {output}\nPlan: {total} primary attempts; optional retries additional", flush=True)
    rows, retries, skipped, checked, schema_fields = [], [], [], False, {}

    def decorate(data, episode_id, index, condition, role):
        data.update({
            "meta__run_fingerprint": np.asarray(fingerprint), "meta__episode_id": np.asarray(episode_id),
            "meta__episode_index": np.asarray(index), "meta__run_role": np.asarray(role),
            "meta__condition_id": np.asarray(condition["condition_id"]),
            "meta__properties_requested_json": np.asarray(json.dumps(condition["properties"], sort_keys=True)),
            "meta__policy_provenance_json": np.asarray(json.dumps(policy_info, sort_keys=True)),
            "meta__runtime_json": np.asarray(json.dumps(runtime, sort_keys=True)),
            "label__shifted_variable": np.asarray(condition["shifted_variable"]),
            "label__shift_magnitude": np.asarray(condition["shift_magnitude"]),
            "label__baseline_properties_json": np.asarray(json.dumps(conditions[0]["properties"], sort_keys=True)),
        })
        return data

    def row_for(data, path):
        return {"episode_id": str(data["meta__episode_id"]), "file": str(path.relative_to(output)),
                "seed": int(data["label__seed"]), "role": str(data["meta__run_role"]),
                "shifted_variable": str(data["label__shifted_variable"]),
                "shift_magnitude": float(data["label__shift_magnitude"]),
                "success_final": bool(data["label__success_final"]),
                "failure_mode": str(data["label__failure_mode"]),
                "failure_type": str(data["label__failure_type"]), "force": force_evidence(data)}

    def inventory(data):
        descriptor = describe(data)
        old_count = len(schema_fields)
        schema_fields.update(descriptor["fields"])
        if len(schema_fields) != old_count:
            descriptor["fields"] = schema_fields.copy()
            write_json(output / "schema.json", descriptor)

    try:
        for condition in conditions:
            env = None
            try:
                for seed_index, seed in enumerate(config["seeds"]):
                    index = condition["condition_index"] * len(config["seeds"]) + seed_index
                    if index >= limit:
                        break
                    episode_id = f"{fingerprint[:12]}:episode_{index:06d}"
                    path = output / f"episode_{index:06d}.npz"
                    normal = None if condition["shifted_variable"] == "none" else _load(output / f"episode_{seed_index:06d}.npz")
                    if path.exists():
                        data = _load(path)
                        _identity(data, fingerprint, episode_id, condition, seed)
                        if normal is not None and str(data["matched_normal_run_id"]) != str(normal["meta__episode_id"]):
                            raise ValueError("Saved residual references a different baseline")
                    else:
                        if env is None:
                            env = CollectionEnv(condition["properties"])
                        video = output / "previews" / f"episode_{index:06d}.gif" if seed_index < args.record_seeds else None
                        data, _ = rollout(env, policy, seed, config, video_path=video)
                        if args.check_determinism and not checked:
                            replay = check_replay(env, policy, seed, config, data)
                            write_json(output / "determinism.json", replay)
                            if not replay["bitwise_equal"]:
                                raise ValueError("Same-seed replay failed; inspect determinism.json before collecting")
                            checked = True
                        decorate(data, episode_id, index, condition, "normal" if normal is None else "shifted")
                        if normal is not None:
                            data.update(build_residual(data, normal))
                            data["label__matched_normal_success"] = normal["label__success_final"].copy()
                        save_episode(path, data)
                    inventory(data)
                    rows.append(row_for(data, path))
                    print(f"[{index + 1}/{limit}] seed={seed} {condition['shifted_variable']} x{condition['shift_magnitude']:g}: {data['label__failure_mode']}", flush=True)
                    if normal is None or bool(data["label__success_final"]) or not config["recovery"]["enabled"]:
                        continue
                    # Retries reset the failed physical condition from the start. They are
                    # separate episodes, not online recovery after a detected failure.
                    for correction_index, correction in enumerate(config["recovery"]["corrections"]):
                        retry_path = output / "retries" / f"episode_{index:06d}_correction_{correction_index:02d}.npz"
                        retry_id = f"{episode_id}:retry_{correction_index:02d}"
                        if retry_path.exists():
                            retry = _load(retry_path)
                            _identity(retry, fingerprint, retry_id, condition, seed)
                            if (str(retry["meta__parent_episode_id"]) != episode_id
                                    or str(retry["matched_normal_run_id"]) != str(normal["meta__episode_id"])
                                    or str(retry["label__reset_state_hash"]) != str(data["label__reset_state_hash"])
                                    or json.loads(str(retry["meta__recovery_correction_json"])) != correction):
                                raise ValueError("Saved recovery is not matched to the requested parent/correction")
                        else:
                            retry_env = CollectionEnv(condition["properties"])
                            try:
                                capability = recovery_capability(retry_env, correction)
                                if not capability["supported"]:
                                    skipped.append({"parent_episode_id": episode_id, "correction": correction, "reason": capability["reason"]})
                                    continue
                                retry, _ = rollout(retry_env, policy, seed, config, correction=correction)
                            finally:
                                retry_env.close()
                            decorate(retry, retry_id, index, condition, "retry")
                            if str(retry["label__reset_state_hash"]) != str(data["label__reset_state_hash"]):
                                raise ValueError("Retry reset state differs from its failed parent")
                            retry.update(build_residual(retry, normal))
                            retry["meta__parent_episode_id"] = np.asarray(episode_id)
                            retry.update(recovery_result(data, retry, correction))
                            retry_path.parent.mkdir(exist_ok=True)
                            save_episode(retry_path, retry)
                        inventory(retry)
                        retry_row = row_for(retry, retry_path)
                        retry_row["parent_episode_id"] = episode_id
                        retry_row["correction"] = correction
                        retry_row["effect_observed"] = bool(retry["label__recovery_effect_observed"])
                        retry_row["recovered"] = bool(retry["label__recovery_recovered"])
                        retries.append(retry_row)
                        print(f"  retry {correction}: success={retry_row['success_final']}", flush=True)
            finally:
                if env is not None:
                    env.close()
            if len(rows) >= limit:
                break
        all_rows = rows + retries
        grasp_rows = [row for row in all_rows if row["force"]["grasp_samples"]]
        force_check = {"grasp_runs": len(grasp_rows),
                       "nonzero_grasp_runs": sum(r["force"]["nonzero_during_grasp"] for r in grasp_rows),
                       "passed": len(grasp_rows) >= 3 and all(r["force"]["nonzero_during_grasp"] for r in grasp_rows),
                       "by_role": {role: {"runs": sum(r["role"] == role for r in all_rows),
                                           "nonzero_grasp_runs": sum(r["role"] == role and r["force"]["nonzero_during_grasp"] for r in all_rows)}
                                   for role in ("normal", "shifted", "retry")},
                       "semantics": "At least three grasping runs, each with bilateral nonzero object-contact force during grasp. No-grasp attempts may correctly have zero force."}
        minimum_tested = []
        for parent_id in sorted({r["parent_episode_id"] for r in retries}):
            for kind in ("slow_lift", "grip_limit"):
                candidates = [r for r in retries if r["parent_episode_id"] == parent_id
                              and r["correction"]["kind"] == kind and r["recovered"]]
                if candidates:
                    best = min(candidates, key=lambda r: abs(r["correction"]["factor"] - 1.0))
                    minimum_tested.append({"parent_episode_id": parent_id, "kind": kind,
                                           "smallest_tested_successful_factor": best["correction"]["factor"],
                                           "retry_episode_id": best["episode_id"]})
        summary = {"episodes": len(rows), "planned_episodes": total,
                   "success_final": sum(r["success_final"] for r in rows),
                   "outcome_counts": dict(Counter(r["failure_mode"] for r in rows)),
                   "contact_force_check": force_check, "episodes_detail": rows,
                   "retry_episodes": len(retries), "retries": retries, "skipped_retries": skipped,
                   "smallest_tested_recoveries": minimum_tested}
        write_json(output / "summary.json", summary)
        write_json(output / "force_verification.json", force_check)
        manifest.update(status="complete" if len(rows) == total else "partial", completed_episodes=len(rows), retry_episodes=len(retries))
        write_json(output / "manifest.json", manifest)
        print(json.dumps({k: v for k, v in summary.items() if k not in ("episodes_detail", "retries", "skipped_retries")}, indent=2), flush=True)
    except BaseException as exc:
        manifest.update(status="interrupted", error=f"{type(exc).__name__}: {exc}")
        write_json(output / "manifest.json", manifest)
        raise
