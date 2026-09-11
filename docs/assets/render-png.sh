#!/usr/bin/env bash
# Render README-safe PNGs from the SVG sources.
# GitHub mobile's SVG sanitizer / WebKit drops some of these diagrams
# (evaluation.svg and action-ladder.svg showed broken-image placeholders);
# PNG embeds are reliable. Keep the SVGs as the source of truth.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
FC_DIR="$(mktemp -d)"
trap 'rm -rf "$FC_DIR"' EXIT

# Map CSS system families used in the SVGs to Inter on this machine.
cat >"$FC_DIR/fonts.conf" <<'XML'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <alias>
    <family>ui-sans-serif</family>
    <prefer><family>Inter</family></prefer>
  </alias>
  <alias>
    <family>system-ui</family>
    <prefer><family>Inter</family></prefer>
  </alias>
  <alias>
    <family>sans-serif</family>
    <prefer><family>Inter</family></prefer>
  </alias>
  <alias>
    <family>ui-monospace</family>
    <prefer><family>JetBrains Mono</family></prefer>
  </alias>
  <alias>
    <family>monospace</family>
    <prefer><family>JetBrains Mono</family></prefer>
  </alias>
</fontconfig>
XML

export FONTCONFIG_FILE="$FC_DIR/fonts.conf"

# 2x so GitHub README scaling stays sharp on retina / mobile.
zoom=2
for name in klarpost-mark architecture evaluation action-ladder; do
  src="$ROOT/${name}.svg"
  dst="$ROOT/${name}.png"
  rsvg-convert --zoom="$zoom" "$src" -o "$dst"
  echo "wrote $dst ($(wc -c <"$dst") bytes)"
done
