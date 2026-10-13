#!/usr/bin/env bash
# Frozen policy data collection only; all CLI arguments pass through.
set -euo pipefail
collection_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
collection_python="${COLLECTION_PYTHON:-${collection_root}/.venv/bin/python}"
collection_checkpoint="${COLLECTION_CHECKPOINT:-${collection_root}/runs/learning/20261009T045047-c852bfc9/final_ckpt.pt}"
export PYTHONPATH="${collection_root}${PYTHONPATH:+:$PYTHONPATH}"
export MS_ASSET_DIR="${MS_ASSET_DIR:-${collection_root}/.maniskill/assets}"
export MS_SKIP_ASSET_DOWNLOAD_PROMPT=1
export VK_ICD_FILENAMES="${VK_ICD_FILENAMES:-/usr/share/vulkan/icd.d/lvp_icd.x86_64.json}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/failure-mpl}"
exec "$collection_python" -m failure_collection.varied --checkpoint "$collection_checkpoint" "$@"
