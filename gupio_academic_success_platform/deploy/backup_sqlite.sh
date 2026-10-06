#!/usr/bin/env bash
set -euo pipefail

SRC="${SRC_DB:-./backend/gupio.db}"
OUT_DIR="${OUT_DIR:-./backups}"
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT_DIR"
cp "$SRC" "$OUT_DIR/gupio_${STAMP}.db"
# Production: encrypt the backup and copy it to an isolated off-site bucket/storage account.
echo "Created local backup: $OUT_DIR/gupio_${STAMP}.db"
