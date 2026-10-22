#!/usr/bin/env bash
# Official frozen policy; native task; nominal quality gate; single-factor sweeps.
set -euo pipefail
stock_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
stock_python="${COLLECTION_PYTHON:-${stock_root}/.venv/bin/python}"
export PYTHONPATH="${stock_root}${PYTHONPATH:+:$PYTHONPATH}"
export MS_ASSET_DIR="${MS_ASSET_DIR:-${stock_root}/.maniskill/assets}"
export MS_SKIP_ASSET_DOWNLOAD_PROMPT=1
export VK_ICD_FILENAMES="${VK_ICD_FILENAMES:-/usr/share/vulkan/icd.d/lvp_icd.x86_64.json}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/failure-mpl}"
exec "$stock_python" -m robot_adaptation.collection.stock "$@"
