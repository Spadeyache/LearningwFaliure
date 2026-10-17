#!/usr/bin/env bash
set -euo pipefail
analysis_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${COLLECTION_PYTHON:-${analysis_root}/../.venv/bin/python}" "${analysis_root}/run.py" "$@"
