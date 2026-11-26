#!/usr/bin/env python3
"""Generate EsimCard launcher icons and in-app logo from one square logo.

Usage: python3 tools/esimcard_icons.py path/to/logo.png [--bg "#00AAFF"]

Writes android/app/src/community/res/mipmap-*/ic_launcher*.png and
assets/logo-community.png. The logo should be square, >= 512x512, ideally
with a transparent background.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'android/app/src/community/res'
DENSITIES = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}


def fit(logo, size, scale):
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    inner = max(1, int(size * scale))
    img = logo.copy()
    img.thumbnail((inner, inner), Image.LANCZOS)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('logo', type=Path)
    ap.add_argument('--bg', default='#FFFFFF', help='Adaptive icon background colour')
    a = ap.parse_args()
    logo = Image.open(a.logo).convert('RGBA')
    for name, k in DENSITIES.items():
        d = RES / f'mipmap-{name}'
        d.mkdir(parents=True, exist_ok=True)
        adaptive = int(108 * k)
        # Adaptive foreground: keep the logo inside the 66dp safe zone.
        fit(logo, adaptive, 0.58).save(d / 'ic_launcher_foreground.png')
        Image.new('RGBA', (adaptive, adaptive), a.bg).save(d / 'ic_launcher_background.png')
        legacy = int(48 * k)
        icon = Image.new('RGBA', (legacy, legacy), (0, 0, 0, 0))
        mask = Image.new('L', (legacy, legacy), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, legacy - 1, legacy - 1), radius=legacy // 5, fill=255)
        icon.paste(Image.new('RGBA', (legacy, legacy), a.bg), (0, 0), mask)
        fg = fit(logo, legacy, 0.78)
        icon.alpha_composite(fg)
        icon.save(d / 'ic_launcher.png')
    fit(logo, 128, 1.0).save(ROOT / 'assets/logo-community.png')
    print('Icons written.')


if __name__ == '__main__':
    main()
