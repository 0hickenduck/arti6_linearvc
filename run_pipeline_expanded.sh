#!/bin/bash
# Autonomous Downloader Execution Script - Expanded Version

set -e

DOWNLOADER="arti6_linearvc_demo/downloader.py"

echo "Starting autonomous download pipeline (EXPANDED)..."

# Enna Alouette
echo "Downloading Enna Alouette data..."
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/watch?v=lv4vIggzKOs" || true
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/watch?v=HvmLyijz_1I" || true
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/watch?v=ndj2qYnvT_s" || true
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/watch?v=2SZbnGJAymg" || true
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/live/7HOkTSZ3rCs" || true

# Takanashi Kiara
echo "Downloading Takanashi Kiara data..."
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://youtu.be/QI96hnhcr2E" || true
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://youtu.be/eDfMDkgheQY" || true
python3 $DOWNLOADER --identity Kiara --lang EN_JP_DE --url "https://www.youtube.com/playlist?list=PLsAbCDORf2yRlokPRc_dP1GCnNdWjJkVM" || true
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://www.youtube.com/watch?v=XLowkpk5Hfg" || true
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://www.youtube.com/watch?v=tNpd1gT1J_g" || true
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://www.youtube.com/watch?v=SF4rteXN57w" || true

# FuwaMoco
echo "Downloading FuwaMoco data..."
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/watch?v=Yr1EI_jYBB8" || true
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/watch?v=aThUfmKQgaY" || true
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/watch?v=Nj17tbZP4oA" || true
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/playlist?list=PLf4O_VcbYo27DpnCJZXRsxov6_DD2Q1NS" || true

# Mori Calliope
echo "Downloading Mori Calliope data..."
python3 $DOWNLOADER --identity Mori --lang EN_JP --url "https://www.youtube.com/playlist?list=PLi0GFY6W7Kh3UAQPP-POsTFsZj_XlhgSe" || true
python3 $DOWNLOADER --identity Mori --lang EN_JP --url "https://www.youtube.com/watch?v=4xxkUEkUCoU" || true
python3 $DOWNLOADER --identity Mori --lang EN_JP --url "https://www.youtube.com/watch?v=5y3xh8gs24c" || true

# Final Packaging
echo "Packaging all data..."
python3 $DOWNLOADER --package

echo "Pipeline complete."
