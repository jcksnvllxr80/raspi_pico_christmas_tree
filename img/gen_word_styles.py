"""Generate stylized word images for LED effect labels (128x64, black bg, white text).

Also updates img_utils.py with MONO_HLSB bytearrays for the SSD1306 display.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np
import re

W, H = 128, 64
OUT = 'C:/Users/A-A-Ron/git/raspi_pico_christmas_tree/img/words'


def fit_font(path, text, max_w, max_h, start=80, minimum=16):
    for size in range(start, minimum - 1, -1):
        font = ImageFont.truetype(path, size)
        tmp = Image.new('L', (W * 4, H * 4))
        d = ImageDraw.Draw(tmp)
        bb = d.textbbox((0, 0), text, font=font)
        if (bb[2] - bb[0]) <= max_w and (bb[3] - bb[1]) <= max_h:
            return font, size
    return ImageFont.truetype(path, minimum), minimum


def get_text_pos(draw, w, h, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (w - tw) // 2 - bb[0]
    y = (h - th) // 2 - bb[1]
    return x, y


def draw_centered(draw, w, h, text, font, fill=(255, 255, 255), **kwargs):
    x, y = get_text_pos(draw, w, h, text, font)
    draw.text((x, y), text, font=font, fill=fill, **kwargs)


# ── AURORA ── Gabriola (ornate flowing script), clean white on black
font, sz = fit_font('C:/Windows/Fonts/Gabriola.ttf', 'aurora', 122, 54)
print(f'aurora: Gabriola size {sz}')
aurora_img = Image.new('RGB', (W, H), 0)
ad = ImageDraw.Draw(aurora_img)
draw_centered(ad, W, H, 'aurora', font, (255, 255, 255))
aurora_img.save(f'{OUT}/aurora.png')
print('aurora saved')


# ── COMET ── Agency FB Bold, italic shear only (clean label)
SCALE = 3
font_big, _ = fit_font('C:/Windows/Fonts/AGENCYB.TTF', 'comet',
                       112 * SCALE, 54 * SCALE, start=240)
big = Image.new('RGB', (W * SCALE, H * SCALE), 0)
bd = ImageDraw.Draw(big)
draw_centered(bd, W * SCALE, H * SCALE, 'comet', font_big, (255, 255, 255))

# italic shear (lean right)
arr = np.array(big, dtype=np.uint8)
sheared = np.zeros_like(arr)
for row in range(H * SCALE):
    shift = int((H * SCALE // 2 - row) * 0.22)
    src = arr[row]
    shifted = np.roll(src, shift, axis=0)
    if shift > 0:
        shifted[:shift] = 0
    elif shift < 0:
        shifted[shift:] = 0
    sheared[row] = shifted

comet_img = Image.fromarray(sheared).resize((W, H), Image.LANCZOS)
comet_img.save(f'{OUT}/comet.png')
print('comet saved')


# ── EMBER ── Jokerman (wild organic decorative font, no extra effects)
font, sz = fit_font('C:/Windows/Fonts/JOKERMAN.TTF', 'ember', 122, 54)
print(f'ember: Jokerman size {sz}')
ember_img = Image.new('RGB', (W, H), 0)
ed = ImageDraw.Draw(ember_img)
draw_centered(ed, W, H, 'ember', font, (255, 255, 255))
ember_img.save(f'{OUT}/ember.png')
print('ember saved')


# ── SOLSTICE ── Onyx (extreme high-contrast display caps) + star corner accents
font, sz = fit_font('C:/Windows/Fonts/ONYX.TTF', 'SOLSTICE', 122, 54)
print(f'solstice: Onyx size {sz}')
solstice_img = Image.new('RGB', (W, H), 0)
ssd = ImageDraw.Draw(solstice_img)
draw_centered(ssd, W, H, 'SOLSTICE', font, (255, 255, 255))

# tiny 4-point star accents in corners
def star(draw, cx, cy, r=2):
    draw.point((cx, cy), fill=(255, 255, 255))
    for d in range(1, r + 1):
        v = max(0, 255 - d * 85)
        draw.point((cx + d, cy), fill=(v, v, v))
        draw.point((cx - d, cy), fill=(v, v, v))
        draw.point((cx, cy + d), fill=(v, v, v))
        draw.point((cx, cy - d), fill=(v, v, v))

star(ssd, 4, 5, 2)
star(ssd, 123, 58, 2)
star(ssd, 122, 5, 1)
star(ssd, 5, 58, 1)

solstice_img.save(f'{OUT}/solstice.png')
print('solstice saved')


# ── VORTEX ── Magneto Bold with a keystone perspective (funnel-into-screen)
SCALE = 3
font_big, sz = fit_font('C:/Windows/Fonts/MAGNETOB.TTF', 'VORTEX',
                        W * SCALE, H * SCALE, start=240)
print(f'vortex: Magneto size {sz}')
big = Image.new('RGB', (W * SCALE, H * SCALE), 0)
bd = ImageDraw.Draw(big)
draw_centered(bd, W * SCALE, H * SCALE, 'VORTEX', font_big, (255, 255, 255))

# Keystone perspective: shrink top, full width at bottom → spinning-into-screen feel
arr = np.array(big, dtype=np.float32)
out_arr = np.zeros_like(arr)
rows = H * SCALE
cols = W * SCALE
cx_big = cols / 2.0
for row in range(rows):
    # scale factor: 0.45 at top row → 1.0 at bottom row
    t = row / (rows - 1)
    scale_x = 0.45 + 0.55 * t
    for col in range(cols):
        src_x = cx_big + (col - cx_big) / scale_x
        if 0 <= src_x < cols - 1:
            x0 = int(src_x)
            frac = src_x - x0
            out_arr[row, col] = arr[row, x0] * (1 - frac) + arr[row, x0 + 1] * frac
        elif 0 <= int(src_x) < cols:
            out_arr[row, col] = arr[row, int(src_x)]

vortex_big = Image.fromarray(out_arr.astype(np.uint8))
vortex_img = vortex_big.resize((W, H), Image.LANCZOS)

# thin spin arcs beneath text
vd = ImageDraw.Draw(vortex_img)
cx2, cy2 = W // 2, H - 9
for rx, ry, ang_start, ang_end, brightness in [
    (38, 5, 195, 345, 180),
    (28, 4, 210, 330, 140),
]:
    vd.arc([cx2 - rx, cy2 - ry, cx2 + rx, cy2 + ry],
           start=ang_start, end=ang_end, fill=(brightness, brightness, brightness), width=1)

vortex_img.save(f'{OUT}/vortex.png')
print('vortex saved')

print('\nAll done.')


# ── FIREBALL ── Chiller (wild dripping font) + upward flame tips
SCALE = 3
font_big, sz = fit_font('C:/Windows/Fonts/CHILLER.TTF', 'fireball',
                        112 * SCALE, 52 * SCALE, start=240)
print(f'fireball: Chiller size {sz}')
big = Image.new('RGB', (W * SCALE, H * SCALE), 0)
bd = ImageDraw.Draw(big)
draw_centered(bd, W * SCALE, H * SCALE, 'fireball', font_big, (255, 255, 255))

# italic shear (lean right, same as comet)
arr = np.array(big, dtype=np.uint8)
sheared = np.zeros_like(arr)
for row in range(H * SCALE):
    shift = int((H * SCALE // 2 - row) * 0.18)
    src = arr[row]
    shifted = np.roll(src, shift, axis=0)
    if shift > 0:
        shifted[:shift] = 0
    elif shift < 0:
        shifted[shift:] = 0
    sheared[row] = shifted

fireball_img = Image.fromarray(sheared).resize((W, H), Image.LANCZOS)

# add small upward flame spikes above the text
fd = ImageDraw.Draw(fireball_img)
import random as _rng
_rng.seed(42)
for _ in range(18):
    cx = _rng.randint(8, W - 8)
    base_y = _rng.randint(2, 10)
    height = _rng.randint(3, 8)
    half = _rng.randint(1, 3)
    fd.polygon([(cx - half, base_y + height),
                (cx,        base_y),
                (cx + half, base_y + height)],
               fill=(255, 255, 255))

fireball_img.save(f'{OUT}/fireball.png')
print('fireball saved')


# ── Update img_utils.py with MONO_HLSB bytearrays ──────────────────────────

IMGUTILS = 'C:/Users/A-A-Ron/git/raspi_pico_christmas_tree/img/img_utils.py'
THRESHOLD = 80   # pixel value above this → white (1) in 1-bit

NAMES = ['aurora', 'comet', 'ember', 'fireball', 'solstice', 'vortex']


def to_mono_hlsb(png_path, threshold=THRESHOLD):
    """Convert a PNG to a MONO_HLSB bytearray for framebuf.FrameBuffer."""
    img = Image.open(png_path).convert('L')
    arr = []
    for y in range(H):
        for x_byte in range(W // 8):
            byte = 0
            for bit in range(8):
                x = x_byte * 8 + bit
                if img.getpixel((x, y)) > threshold:
                    byte |= (1 << (7 - bit))
            arr.append(byte)
    return bytearray(arr)


print('\nUpdating img_utils.py ...')
with open(IMGUTILS, 'r') as f:
    src = f.read()

for name in NAMES:
    ba = to_mono_hlsb(f'{OUT}/{name}.png')
    ba_repr = "bytearray(b'" + ''.join(f'\\x{b:02x}' for b in ba) + "')"
    # Match the assignment + bytearray call; preserve any trailing comment
    pattern = rf'^({name}_ba\s*=\s*)bytearray\(.*?\)'
    replacement = rf'\g<1>{ba_repr}'
    new_src, n = re.subn(pattern, lambda m: m.group(1) + ba_repr, src, flags=re.MULTILINE)
    if n == 1:
        src = new_src
        print(f'  {name}_ba updated ({len(ba)} bytes)')
    else:
        print(f'  WARNING: {name}_ba not found or matched {n} times — skipped')

with open(IMGUTILS, 'w') as f:
    f.write(src)

print('img_utils.py saved.')
