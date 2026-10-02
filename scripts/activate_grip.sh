# Source this file from any working directory: source /home/ubuntu/faliure/scripts/activate_grip.sh
GRIP_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$GRIP_PROJECT_ROOT/.venv/bin/activate"
export UV_CACHE_DIR="$GRIP_PROJECT_ROOT/.cache/uv"
export MPLCONFIGDIR="$GRIP_PROJECT_ROOT/.cache/matplotlib"
export MS_ASSET_DIR="$GRIP_PROJECT_ROOT/.maniskill/assets"
export MS_SKIP_ASSET_DOWNLOAD_PROMPT=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
if [[ -z "${VK_ICD_FILENAMES:-}" && -f /usr/share/vulkan/icd.d/lvp_icd.x86_64.json ]]; then
    export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json
fi
