#!/bin/bash
# Autonomous Downloader Execution Script

set -e

DOWNLOADER="arti6_linearvc_demo/downloader.py"
BROWSER="chrome"

echo "Starting autonomous download pipeline..."

# Enna Alouette
echo "Downloading Enna Alouette data..."
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/watch?v=lv4vIggzKOs" || true
python3 $DOWNLOADER --identity Enna --lang EN --url "https://www.youtube.com/live/7HOkTSZ3rCs" || true

# Takanashi Kiara
echo "Downloading Takanashi Kiara data..."
python3 $DOWNLOADER --identity Kiara --lang EN --url "https://youtu.be/QI96hnhcr2E" || true
python3 $DOWNLOADER --identity Kiara --lang EN_JP_DE --url "https://www.youtube.com/playlist?list=PLsAbCDORf2yRlokPRc_dP1GCnNdWjJkVM" || true

# FuwaMoco
echo "Downloading FuwaMoco data..."
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/watch?v=Yr1EI_jYBB8" || true
python3 $DOWNLOADER --identity FuwaMoco --lang EN_JP --url "https://www.youtube.com/watch?v=DzP0jXgOC4I" || true

# Mori Calliope
echo "Downloading Mori Calliope data..."
python3 $DOWNLOADER --identity Mori --lang EN_JP --url "https://www.youtube.com/watch?v=5y3xh8gs24c" || true
python3 $DOWNLOADER --identity Mori --lang EN_JP --url "https://www.youtube.com/watch?v=4xxkUEkUCoU" || true

# Final Packaging
echo "Packaging all data..."
python3 $DOWNLOADER --package

echo "Pipeline complete."
