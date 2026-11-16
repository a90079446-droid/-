#!/usr/bin/env bash
# Essentia 분석 모델 내려받기 (약 28MB). 출처: https://essentia.upf.edu/models/
# 모델 라이선스: CC BY-NC-SA 4.0 (비상업). 개인 레퍼런스 분석 용도로 사용.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p models
B=https://essentia.upf.edu/models
FILES=(
  feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb
)
for h in genre_discogs400 mtg_jamendo_instrument mtg_jamendo_moodtheme voice_instrumental gender danceability; do
  FILES+=("classification-heads/$h/$h-discogs-effnet-1.pb" "classification-heads/$h/$h-discogs-effnet-1.json")
done
for f in "${FILES[@]}"; do
  out="models/$(basename "$f")"
  if [ -s "$out" ]; then echo "있음: $out"; continue; fi
  echo "받는 중: $out"
  curl -fsSL -o "$out" "$B/$f"
done
echo "완료"
