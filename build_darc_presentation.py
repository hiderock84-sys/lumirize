from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Cm


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "artifacts" / "official"
OUT_DIR = ROOT / "artifacts" / "output"
PNG_DIR = ROOT / "artifacts" / "designed_slides"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PNG_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
NAVY = (9, 30, 54)
NAVY2 = (15, 52, 88)
BLUE = (37, 116, 255)
CYAN = (16, 176, 210)
GREEN = (17, 190, 138)
ORANGE = (245, 160, 28)
RED = (239, 82, 88)
PURPLE = (126, 91, 255)
PINK = (238, 82, 145)
YELLOW = (255, 217, 74)
BG = (229, 238, 247)
WHITE = (255, 255, 255)
TEXT = (28, 42, 58)
MUTED = (88, 105, 124)
LINE = (204, 218, 230)
INK = (5, 18, 35)

FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_SERIF_BOLD if serif else (FONT_BOLD if bold else FONT_REG), size)


def fit_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    tw, th = size
    ratio = max(tw / iw, th / ih)
    nw, nh = int(iw * ratio), int(ih * ratio)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def paste_cover(base: Image.Image, path: Path, box: tuple[int, int, int, int], overlay=(0, 0, 0, 0)):
    x, y, w, h = box
    im = fit_cover(path, (w, h))
    base.paste(im, (x, y))
    if overlay[3]:
        ov = Image.new("RGBA", (w, h), overlay)
        base.alpha_composite(ov, (x, y))


def shadow_box(img: Image.Image, xy, radius=18, fill=WHITE, outline=LINE, shadow=True):
    x, y, w, h = xy
    if shadow:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((x + 6, y + 8, x + w + 6, y + h + 8), radius, fill=(28, 54, 78, 45))
        layer = layer.filter(ImageFilter.GaussianBlur(8))
        img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius, fill=fill, outline=outline, width=2)


def draw_text(draw: ImageDraw.ImageDraw, xy, text, size=28, fill=TEXT, bold=False, width=None, line_gap=8, anchor=None, serif=False):
    x, y = xy
    f = font(size, bold, serif)
    if width is None:
        draw.text((x, y), text, font=f, fill=fill, anchor=anchor)
        return
    # Wrap by visual length; Japanese chars are roughly full-width.
    chars_per_line = max(6, int(width / (size * 0.62)))
    lines = []
    for paragraph in str(text).split("\n"):
        if not paragraph:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, chars_per_line, break_long_words=True, replace_whitespace=False))
    yy = y
    for line in lines:
        draw.text((x, yy), line, font=f, fill=fill)
        yy += size + line_gap


def pill(draw, x, y, w, h, label, color=BLUE, text_color=WHITE, size=20):
    draw.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=color)
    draw.text((x + w // 2, y + h // 2), label, font=font(size, True), fill=text_color, anchor="mm")


def header(img, title, subtitle, badge, n, total=18, color=NAVY):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 118), fill=color)
    d.rounded_rectangle((36, 30, 86, 80), 14, fill=NAVY2)
    d.text((61, 56), "●", font=font(22, True), fill=CYAN, anchor="mm")
    draw_text(d, (108, 24), title, 34, WHITE, True)
    draw_text(d, (110, 70), subtitle, 16, (190, 212, 230), width=900)
    pill(d, 1515, 32, 300, 48, badge, (236, 242, 248), NAVY, 18)
    d.text((1710, 1030), f"{n}/{total}", font=font(18, True), fill=NAVY, anchor="ra")
    d.rounded_rectangle((1728, 1038, 1875, 1048), 5, fill=(207, 218, 229))
    d.rounded_rectangle((1728, 1038, 1728 + int(147 * n / total), 1048), 5, fill=GREEN if n == total else CYAN)
    draw_text(d, (38, 1030), "相模原ダルク｜依存症からの回復を全力で支えます", 15, MUTED)


def card(img, x, y, w, h, title, lines, accent=BLUE, title_size=24, body_size=20, dark=False):
    fill = NAVY2 if dark else WHITE
    outline = (54, 91, 122) if dark else LINE
    shadow_box(img, (x, y, w, h), 20, fill, outline, shadow=not dark)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + 12), 8, fill=accent)
    if title:
        draw_text(d, (x + 26, y + 28), title, title_size, WHITE if dark else NAVY, True, width=w - 52)
    yy = y + 78
    for line in lines:
        d.rounded_rectangle((x + 26, yy + 3, x + 42, yy + 19), 5, fill=accent)
        draw_text(d, (x + 56, yy), line, body_size, (225, 238, 246) if dark else TEXT, False, width=w - 86, line_gap=5)
        yy += max(42, body_size + 24)


def kpi(img, x, y, w, h, label, value, note, accent):
    shadow_box(img, (x, y, w, h), 18, (17, 50, 82), (44, 87, 122), True)
    d = ImageDraw.Draw(img)
    d.rectangle((x, y, x + w, y + 10), fill=accent)
    draw_text(d, (x + 24, y + 26), label, 18, (187, 214, 232), True)
    draw_text(d, (x + 24, y + 66), value, 44, WHITE, True)
    draw_text(d, (x + 24, y + 126), note, 17, (195, 218, 234), width=w - 48)


def bottom_strip(img, y, title, items, accent=BLUE):
    d = ImageDraw.Draw(img)
    shadow_box(img, (55, y, 1810, 76), 18, WHITE, LINE, True)
    d.rectangle((55, y, 65, y + 76), fill=accent)
    draw_text(d, (86, y + 16), title, 22, NAVY, True)
    x = 440
    for i, item in enumerate(items):
        pill(d, x, y + 19, 34, 34, str(i + 1), accent, WHITE, 15)
        draw_text(d, (x + 46, y + 19), item, 18, TEXT, True, width=250)
        x += 280


def section_label(img, x, y, label, color=CYAN):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + 15, y + 52), 7, fill=color)
    draw_text(d, (x + 26, y + 9), label, 25, NAVY, True)


def executive_note(img, x, y, w, title, body, accent=CYAN):
    d = ImageDraw.Draw(img)
    shadow_box(img, (x, y, w, 118), 18, (246, 251, 253), LINE, True)
    d.rectangle((x, y, x + 12, y + 118), fill=accent)
    draw_text(d, (x + 34, y + 18), title, 24, NAVY, True)
    draw_text(d, (x + 34, y + 58), body, 20, TEXT, width=w - 68, line_gap=6)


def matrix_card(img, x, y, w, h, title, cols, rows, accent=BLUE):
    d = ImageDraw.Draw(img)
    shadow_box(img, (x, y, w, h), 18, WHITE, LINE, True)
    d.rectangle((x, y, x + w, y + 12), fill=accent)
    draw_text(d, (x + 28, y + 24), title, 26, NAVY, True)
    top = y + 82
    col_w = (w - 56) // len(cols)
    for i, col in enumerate(cols):
        d.rounded_rectangle((x + 28 + i * col_w, top, x + 20 + (i + 1) * col_w, top + 48), 10, fill=(235, 243, 249))
        d.text((x + 24 + i * col_w + col_w // 2, top + 24), col, font=font(18, True), fill=accent, anchor="mm")
    yy = top + 66
    for row in rows:
        for i, item in enumerate(row):
            d.rounded_rectangle((x + 28 + i * col_w, yy, x + 20 + (i + 1) * col_w, yy + 52), 10, fill=(248, 251, 253), outline=(222, 232, 240))
            draw_text(d, (x + 42 + i * col_w, yy + 13), item, 16, TEXT, True, width=col_w - 34)
        yy += 62


def executive_footer(img, message, accent=CYAN):
    d = ImageDraw.Draw(img)
    shadow_box(img, (55, 900, 1810, 82), 18, NAVY, (42, 84, 116), True)
    d.rounded_rectangle((78, 923, 118, 963), 10, fill=accent)
    d.text((98, 943), "✓", font=font(24, True), fill=WHITE, anchor="mm")
    draw_text(d, (140, 922), message, 25, WHITE, True, width=1620)


def mini_kpi_light(img, x, y, label, value, accent=BLUE):
    d = ImageDraw.Draw(img)
    shadow_box(img, (x, y, 250, 112), 16, WHITE, LINE, True)
    d.rounded_rectangle((x + 18, y + 18, x + 56, y + 56), 10, fill=accent)
    draw_text(d, (x + 74, y + 14), label, 17, MUTED, True, width=150)
    draw_text(d, (x + 74, y + 46), value, 34, NAVY, True)


def draw_bar_chart(img, x, y, w, h, labels, values, colors):
    d = ImageDraw.Draw(img)
    max_v = max(values)
    bar_w = w // len(values) - 28
    for i, (lab, val, col) in enumerate(zip(labels, values, colors)):
        bx = x + i * (w // len(values)) + 18
        bh = int((h - 70) * val / max_v)
        d.rounded_rectangle((bx, y + h - bh - 42, bx + bar_w, y + h - 42), 8, fill=col)
        d.text((bx + bar_w // 2, y + h - bh - 70), str(val), font=font(24, True), fill=NAVY, anchor="mm")
        d.text((bx + bar_w // 2, y + h - 18), lab, font=font(17, True), fill=MUTED, anchor="mm")


def draw_donut(img, cx, cy, r, parts, labels):
    d = ImageDraw.Draw(img)
    start = -90
    for pct, col in parts:
        d.arc((cx - r, cy - r, cx + r, cy + r), start, start + pct * 3.6, fill=col, width=46)
        start += pct * 3.6
    d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=WHITE)
    d.text((cx, cy - 8), "内訳", font=font(20, True), fill=NAVY, anchor="mm")
    d.text((cx, cy + 22), "2024", font=font(16, True), fill=MUTED, anchor="mm")
    lx = cx + r + 55
    ly = cy - 90
    for lab, col in labels:
        d.rounded_rectangle((lx, ly, lx + 20, ly + 20), 5, fill=col)
        draw_text(d, (lx + 32, ly - 4), lab, 18, TEXT, True)
        ly += 44


def premium_background() -> Image.Image:
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    for y in range(118, H, 44):
        d.line((0, y, W, y), fill=(214, 225, 236, 62), width=1)
    for x in range(0, W, 64):
        d.line((x, 118, x, H), fill=(214, 225, 236, 45), width=1)
    d.polygon([(0, 118), (520, 118), (0, 420)], fill=(219, 232, 244, 135))
    d.polygon([(W, 118), (W, 460), (1450, 118)], fill=(219, 232, 244, 125))
    d.rectangle((0, H - 44, W, H), fill=(244, 248, 252, 230))
    return img


def make_slide(n: int) -> Image.Image:
    return premium_background()


def slide_cover() -> Image.Image:
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(img)
    paste_cover(img, ASSET_DIR / "facility_main.jpg", (1010, 0, 910, 1080), (4, 24, 43, 120))
    for i in range(0, 740, 48):
        d.line((0, i + 40, 1040, i + 260), fill=(19, 87, 112, 60), width=2)
    d.rectangle((0, 0, 1040, 1080), fill=(7, 25, 45, 228))
    draw_text(d, (94, 52), "一般社団法人 相模原ダルク", 22, (210, 226, 238))
    pill(d, 1185, 52, 515, 56, "2026年4月25日 横浜ひまわり家族会採用", (20, 63, 104), WHITE, 21)
    draw_text(d, (116, 206), "CHANGE", 72, WHITE, True)
    draw_text(d, (116, 292), "YOUR LIFE!", 72, GREEN, True)
    draw_text(d, (690, 168), "DARC", 188, (230, 248, 245), True, serif=True)
    draw_text(d, (116, 430), "依存症からの回復支援施設・施設紹介 2026", 33, WHITE, True)
    draw_text(d, (116, 504), "変われる。変わった仲間がいる。\n安心できる共同の場と誠実な対話を通じて、\n当事者の生き直す力を呼び起こします。", 26, (222, 238, 248), width=760, line_gap=12)
    d.rounded_rectangle((115, 590, 945, 628), 18, fill=(19, 82, 117))
    draw_text(d, (145, 598), "FOR FAMILY / MEDICAL / WELFARE / JUSTICE PARTNERS", 19, (216, 241, 245), True)
    # Dense message board
    shadow_box(img, (115, 645, 830, 122), 18, (241, 248, 252), (77, 135, 168), True)
    draw_text(d, (145, 670), "本資料で伝える核心", 25, NAVY, True)
    draw_text(d, (145, 714), "依存症は孤立の病です。相模原ダルクは、共同生活・日中活動・家族支援・地域連携を一体化し、回復の継続を支えます。", 21, TEXT, width=760, line_gap=7)
    for i, label in enumerate(["本人相談", "家族相談", "関係機関連携"]):
        pill(d, 1018 + i * 260, 650, 220, 46, label, [BLUE, GREEN, ORANGE][i], WHITE, 20)
    for i, (label, value, col) in enumerate([
        ("対象", "本人・家族・関係機関", BLUE),
        ("目的", "相談から回復支援までの全体理解", GREEN),
        ("形式", "説明会・家族会・連携提案", ORANGE),
    ]):
        x = 118 + i * 276
        d.rounded_rectangle((x, 782, x + 245, 810), 14, fill=col)
        d.text((x + 122, 796), label, font=font(15, True), fill=WHITE, anchor="mm")
        draw_text(d, (x, 818), value, 17, (222, 238, 248), True, width=250)
    metrics = [("回復支援実績", "400+", "名以上", BLUE), ("卒業継続率", "90+", "%以上", GREEN), ("安心の見守り", "24h", "体制", ORANGE), ("連携ネットワーク", "7", "拠点", PURPLE)]
    for i, m in enumerate(metrics):
        kpi(img, 95 + i * 438, 825, 402, 165, *m)
    return img


AGENDA = [
    ("01", "日本の依存症情勢", "2024-2025最新トレンド", BLUE),
    ("02", "予防の3段階と役割", "啓発・介入・回復支援", GREEN),
    ("03", "組織概要・理念", "PHILOSOPHY & MISSION", ORANGE),
    ("04", "実績ハイライト", "データで見る支援体制", RED),
    ("05", "相模原ダルクの強み", "3枚で整理する競争優位", PURPLE),
    ("06", "5ステージ制プログラム", "段階的回復ロードマップ", BLUE),
    ("07", "施設・サービス全体像", "グループ拠点と支援機能", GREEN),
    ("08", "依存症の理解", "7つの特徴・交差依存・PAWS", ORANGE),
    ("09", "家族支援・連携", "CRAFTと地域ネットワーク", RED),
    ("10", "お問い合わせ", "初回相談無料・秘密厳守", PURPLE),
]


def slide_agenda() -> Image.Image:
    img = make_slide(2)
    header(img, "本日のご説明内容｜本日のテーマ", "説明会・家族会・関係機関向けに、相談から回復支援までを一気通貫で理解する構成です", "予定時間：約60分", 2)
    d = ImageDraw.Draw(img)
    draw_text(d, (70, 150), "本日は相模原ダルクの施設紹介を通じて、依存症からの回復支援体制、5ステージ制プログラム、実績、連携ネットワークについてご説明します。", 25, TEXT, True, width=1500)
    for i, (num, title, sub, col) in enumerate(AGENDA):
        x = 65 + (i % 2) * 900
        y = 235 + (i // 2) * 146
        shadow_box(img, (x, y, 835, 116), 18, WHITE, LINE, True)
        pill(d, x + 28, y + 26, 72, 64, num, col, WHITE, 24)
        draw_text(d, (x + 125, y + 25), title, 28, NAVY, True)
        draw_text(d, (x + 125, y + 66), sub, 19, MUTED, width=620)
        d.rounded_rectangle((x + 720, y + 36, x + 792, y + 80), 20, fill=(235, 243, 249))
        d.text((x + 756, y + 58), "▶", font=font(22, True), fill=col, anchor="mm")
    executive_footer(img, "本資料は、依存症支援の全体像・回復プロセス・家族/地域連携を一枚ずつ理解できるよう設計しています。", BLUE)
    return img


def slide_trend() -> Image.Image:
    img = make_slide(3)
    header(img, "日本の依存症情勢 2024-2025最新", "薬物・アルコール・ギャンブル依存が複合化。早期相談と地域支援がますます重要です", "2024-2025", 3)
    d = ImageDraw.Draw(img)
    card(img, 60, 150, 585, 250, "2024年 薬物事犯 検挙人員", ["覚醒剤・大麻が大半を占める", "若年層ではSNS経由の接触が増加", "家族が異変に気づいた時点で相談が重要"], BLUE, 28, 21)
    draw_text(d, (105, 250), "13,462", 70, NAVY, True)
    draw_text(d, (390, 278), "人", 28, MUTED, True)
    shadow_box(img, (690, 150, 520, 250), 18, WHITE, LINE, True)
    draw_text(d, (720, 176), "薬物事犯の内訳", 26, NAVY, True)
    draw_donut(img, 850, 285, 105, [(45.5, BLUE), (45.1, RED), (9.4, GREEN)], [("覚醒剤 45.5%", BLUE), ("大麻 45.1%", RED), ("その他 9.4%", GREEN)])
    card(img, 1250, 150, 600, 250, "注目トピック", ["大麻類似法改正：2024年12月施行", "SNS売買急増：若年層の入口に", "暴力団関与：覚醒剤事犯約50%", "家庭・学校・地域での早期発見が鍵"], ORANGE, 28, 21)
    shadow_box(img, (60, 435, 880, 330), 18, WHITE, LINE, True)
    draw_text(d, (90, 465), "相談現場で見える変化", 28, NAVY, True)
    draw_bar_chart(img, 115, 545, 780, 170, ["薬物", "酒", "ギャンブル", "処方薬", "ネット"], [85, 72, 68, 44, 52], [BLUE, ORANGE, GREEN, PURPLE, CYAN])
    card(img, 980, 435, 870, 330, "重要なポイント", ["依存症は本人の意思だけで解決できる問題ではありません", "発覚直後は家族も混乱し、責める・隠す・抱え込む行動が起きやすい", "早期相談により、医療・福祉・司法・生活支援へつなぐ選択肢が広がります", "相模原ダルクは本人・家族・関係者のいずれからの相談にも対応します"], RED, 28, 22)
    executive_footer(img, "依存症支援では、発覚直後の孤立を止め、医療・福祉・司法・生活支援へ早期に接続することが重要です。", ORANGE)
    return img


def slide_prevention() -> Image.Image:
    img = make_slide(4)
    header(img, "3段階予防と相模原ダルクの役割", "第一次：啓発／第二次：早期介入／第三次：リハビリ・社会復帰まで切れ目なく支援", "予防から回復まで", 4)
    d = ImageDraw.Draw(img)
    stages = [
        ("第一次予防（啓発）", ["講演・研修による乱用防止啓発", "学校・地域イベントでの情報発信", "ニュースレター・活動レポート", "偏見を減らす地域啓発"], BLUE),
        ("第二次予防（介入）", ["医療・行政・司法と連携した早期発見", "本人・家族への初期相談", "見学・面談による状況整理", "弁護士・専門職との協力"], ORANGE),
        ("第三次予防（回復）", ["入寮・通所による集中支援", "24時間体制の見守り", "5ステージ制で役割を獲得", "卒業後も地域連携で定着"], GREEN),
    ]
    for i, (title, lines, col) in enumerate(stages):
        x = 55 + i * 620
        card(img, x, 160, 575, 560, title, lines, col, 31, 23)
        d.text((x + 500, 210), f"{i+1}", font=font(70, True), fill=(230, 239, 247), anchor="mm")
    shadow_box(img, (55, 750, 1810, 142), 20, NAVY, (38, 76, 110), True)
    draw_text(d, (95, 780), "相模原ダルクが担う価値", 30, WHITE, True)
    draw_text(d, (95, 828), "「啓発で入口を減らす」「相談で孤立を止める」「入寮・通所で生活を整える」「地域連携で定着させる」までを一つの支援線として設計します。", 25, (220, 238, 248), width=1600)
    executive_footer(img, "啓発・相談・入所/通所・社会参加を分断せず、一つの支援線として設計することが回復継続の鍵です。", GREEN)
    return img


def slide_philosophy() -> Image.Image:
    img = make_slide(5)
    header(img, "組織概要・理念｜PHILOSOPHY & MISSION", "人としての尊厳を大切に、生き直す力を支える", "設立 2014年", 5)
    d = ImageDraw.Draw(img)
    paste_cover(img, ASSET_DIR / "outline01.jpg", (55, 155, 500, 655), (9, 30, 54, 80))
    card(img, 585, 155, 1265, 210, "PHILOSOPHY｜理念", ["人としての尊厳を大切に、生き直す力を支える", "安心して自分を表現できる共同の場をつくる", "誠実な人との関わりや対話を通じて、本来持つ力を呼び起こす"], BLUE, 30, 22)
    card(img, 585, 395, 1265, 250, "MISSION｜使命", ["依存症からの回復支援を通じて社会に貢献する", "恐れや圧力ではなく、安心できる環境・誠実な関わりによって回復を支える", "施設の中、地域の中、日本の社会の中に共同の場をつくり続ける"], GREEN, 30, 22)
    info = [("事業者", "一般社団法人 相模原ダルク"), ("代表理事", "田中 秀泰"), ("設立", "2014年3月3日"), ("所在地", "神奈川県相模原市中央区千代田3-3-20")]
    x0, y0 = 585, 675
    for i, (k, v) in enumerate(info):
        shadow_box(img, (x0 + (i % 2) * 635, y0 + (i // 2) * 95, 600, 70), 14, WHITE, LINE, True)
        draw_text(d, (x0 + (i % 2) * 635 + 24, y0 + (i // 2) * 95 + 18), k, 18, BLUE, True)
        draw_text(d, (x0 + (i % 2) * 635 + 150, y0 + (i // 2) * 95 + 18), v, 20, NAVY, True, width=420)
    executive_footer(img, "理念はスローガンではなく、安心できる場・誠実な対話・仲間との関係を日々の支援に落とし込むための判断軸です。", BLUE)
    return img


def slide_highlight() -> Image.Image:
    img = make_slide(6)
    header(img, "実績ハイライト｜データで見る相模原ダルク", "400名以上の支援実績、90%以上の卒業後継続率を軸に回復を支えます", "400名以上", 6)
    d = ImageDraw.Draw(img)
    draw_text(d, (70, 150), "相模原ダルクは、開設以来400名以上の依存症当事者を支援。生活の安定、仲間との関係、医療・福祉・司法との連携を通じて回復の継続を支えています。", 27, NAVY, True, width=1680)
    data = [("400+", "回復支援実績", "多様な背景を持つ当事者を継続支援", BLUE), ("5%以下", "入所中の再使用率", "見守りとプログラムでリスク低減", RED), ("90%+", "卒業後継続率", "地域連携で回復を定着", GREEN), ("70名", "受入体制", "大型寮・個室寮で段階的支援", PURPLE)]
    for i, (v, t, note, col) in enumerate(data):
        x = 65 + i * 462
        shadow_box(img, (x, 275, 420, 360), 22, WHITE, LINE, True)
        pill(d, x + 155, 310, 110, 54, "KPI", col, WHITE, 22)
        draw_text(d, (x + 42, 390), v, 64, NAVY, True, width=335)
        draw_text(d, (x + 42, 480), t, 30, NAVY, True, width=335)
        draw_text(d, (x + 42, 530), note, 21, MUTED, width=335)
        d.rounded_rectangle((x + 42, 595, x + 360, 608), 6, fill=(218, 228, 238))
        d.rounded_rectangle((x + 42, 595, x + 310, 608), 6, fill=col)
    shadow_box(img, (65, 690, 1770, 185), 20, WHITE, LINE, True)
    draw_text(d, (100, 720), "支援成果を生む仕組み", 31, NAVY, True)
    for i, (label, col) in enumerate([("相談入口", BLUE), ("安全な生活", GREEN), ("仲間との対話", ORANGE), ("専門連携", PURPLE), ("卒業後支援", CYAN)]):
        x = 110 + i * 340
        pill(d, x, 785, 240, 54, label, col, WHITE, 23)
        if i < 4:
            d.line((x + 250, 812, x + 318, 812), fill=LINE, width=5)
            d.polygon([(x + 318, 812), (x + 300, 800), (x + 300, 824)], fill=LINE)
    executive_footer(img, "支援実績・安全性・継続率・受入規模を組み合わせて、回復を支える運営基盤の強さを示します。", GREEN)
    return img


def slide_strength(n: int, title: str, tag: str, rows, badge_color) -> Image.Image:
    img = make_slide(n)
    header(img, title, "支援現場で評価される相模原ダルクの中核能力を具体項目で整理", tag, n)
    d = ImageDraw.Draw(img)
    for i, (ttl, lines, col) in enumerate(rows):
        x = 60 + (i % 2) * 910
        y = 155 + (i // 2) * 360
        card(img, x, y, 860, 315, ttl, lines, col, 29, 21)
    shadow_box(img, (60, 890, 1770, 70), 18, NAVY, (42, 84, 116), True)
    draw_text(d, (95, 907), "強みは単独ではなく、相談・生活・プログラム・家族・連携が同時に動くことで効果を発揮します。", 25, WHITE, True, width=1600)
    executive_footer(img, "強みは単独の制度ではなく、当事者性・24時間の安心・段階的役割・専門職連携が同時に機能することで価値になります。", badge_color)
    return img


def slide_stages() -> Image.Image:
    img = make_slide(10)
    header(img, "5ステージ制 回復プログラム", "段階的な目標設定と役割付与により、回復を見える化するロードマップ", "5段階のステップ", 10)
    stages = [
        ("MEMBER", "0-3ヶ月", BLUE, ["基礎知識の学習", "共同生活への適応", "生活習慣の再構築", "毎日の予定を守る", "仲間との関係づくり"]),
        ("SUPPORT", "3-6ヶ月", ORANGE, ["掃除・調理など役割付与", "振り返りの習慣化", "感情の言語化", "再発リスクの把握", "基本役割を担う"]),
        ("TRAINEE", "6-12ヶ月", GREEN, ["リーダーシップ練習", "他者支援への参加", "外部活動へ接続", "家族関係の整理", "生活管理の自立"]),
        ("CHIEF", "12-18ヶ月", PURPLE, ["後輩への声かけ", "相談補助", "就労・通院の定着", "地域生活の練習", "自立準備"]),
        ("MANAGER", "18ヶ月-", PINK, ["運営補助", "社会参加・就労準備", "再発予防計画完成", "支える側へ", "卒業後計画"]),
    ]
    for i, (name, period, col, lines) in enumerate(stages):
        x = 50 + i * 374
        shadow_box(img, (x, 165, 342, 690), 20, WHITE, LINE, True)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x + 22, 188, x + 320, 258), 18, fill=col)
        d.text((x + 171, 213), name, font=font(25, True), fill=WHITE, anchor="mm")
        d.text((x + 171, 239), period, font=font(18, True), fill=(235, 246, 250), anchor="mm")
        yy = 298
        for line in lines:
            d.rounded_rectangle((x + 30, yy + 2, x + 50, yy + 22), 6, fill=col)
            draw_text(d, (x + 66, yy - 3), line, 21, TEXT, True, width=230)
            yy += 70
        d.rounded_rectangle((x + 28, 780, x + 314, 825), 12, fill=(238, 246, 250))
        d.text((x + 171, 803), "達成基準 → 次段階へ", font=font(18, True), fill=col, anchor="mm")
    executive_footer(img, "ステージ制は、回復を可視化し、小さな成功体験を積み上げながら社会参加へ進むためのロードマップです。", PURPLE)
    return img


def slide_facilities() -> Image.Image:
    img = make_slide(11)
    header(img, "相模原ダルクグループ", "複数拠点と依存症支援サービスを組み合わせる包括的ネットワーク", "全体像", 11)
    paste_cover(img, ASSET_DIR / "facility_main.jpg", (55, 155, 520, 300), (0, 0, 0, 15))
    paste_cover(img, ASSET_DIR / "business01.jpg", (610, 155, 520, 300), (0, 0, 0, 15))
    paste_cover(img, ASSET_DIR / "business02.jpg", (1165, 155, 700, 300), (0, 0, 0, 30))
    rows = [
        ("デイケアセンター", ["総合相談窓口", "日中プログラム", "医療・行政連携"], BLUE),
        ("OTC", ["作業訓練", "社会参加", "就労準備"], GREEN),
        ("大和PCC", ["共同生活", "生活再建", "初期回復支援"], ORANGE),
        ("町田RC", ["自立準備", "段階的支援", "地域移行"], PURPLE),
        ("愛川TC", ["集中回復", "生活訓練", "環境調整"], CYAN),
        ("上溝HRC", ["ヒーリング", "生活改善", "安定化"], RED),
    ]
    for i, (ttl, lines, col) in enumerate(rows):
        x = 55 + (i % 3) * 610
        y = 500 + (i // 3) * 180
        card(img, x, y, 560, 140, ttl, lines, col, 24, 18)
    executive_footer(img, "複数拠点を連動させることで、相談・生活訓練・就労準備・地域移行までを一体的に支援します。", BLUE)
    return img


def slide_programs() -> Image.Image:
    img = make_slide(12)
    header(img, "回復プログラム（デイ・ナイト・個別）", "通所・入寮・個別サポートを組み合わせ、生活全体を回復環境に変える", "3つの支援", 12)
    programs = [
        ("デイケア（通所）", ["ミーティング／プログラム", "12ステップ", "SAGARP（再発予防CBT）", "ワークショップ・アート", "感情・行動の振り返り", "生活課題の共有"], BLUE),
        ("ナイトケア（寮）", ["生活習慣の改善", "金銭・食事の管理", "夜間の不安への対応", "24時間体制", "共同生活", "孤立をつくらない"], ORANGE),
        ("個別サポート", ["個別面談", "債務・司法相談", "家族支援", "就労準備", "医療・福祉接続", "退所後計画"], GREEN),
    ]
    for i, (ttl, lines, col) in enumerate(programs):
        card(img, 60 + i * 620, 165, 570, 650, ttl, lines, col, 31, 23)
    executive_footer(img, "デイ・ナイト・個別支援を組み合わせることで、日中活動だけでは拾えない生活・家族・司法/債務課題まで支援できます。", GREEN)
    return img


def slide_features() -> Image.Image:
    img = make_slide(13)
    header(img, "依存症の理解（7つの特徴）", "科学的理解に基づく回復支援の前提条件", "7つの特徴", 13)
    features = [
        ("一次性の病気", "原因は依存症そのもの。意思や性格の問題ではありません。", BLUE),
        ("慢性の病気", "完治ではなく、やめ続けるためのケアが必要です。", GREEN),
        ("進行性の病気", "放置すれば失うものが大きくなります。", ORANGE),
        ("死亡率が高い", "事故・自殺・オーバードーズ等のリスクがあります。", RED),
        ("性格が変化", "病気の進行に伴い、人間関係が崩れます。", PURPLE),
        ("対象が移行", "交差依存により、対象が移ることがあります。", PINK),
        ("人を巻き込む", "家族・周囲への影響と支援が重要です。", CYAN),
    ]
    for i, (ttl, body, col) in enumerate(features):
        x = 60 + (i % 4) * 455
        y = 160 + (i // 4) * 265
        card(img, x, y, 410, 220, ttl, [body, "支援では責めるより理解し、継続的につなぐ姿勢が重要です。"], col, 24, 18)
    d = ImageDraw.Draw(img)
    shadow_box(img, (60, 735, 1770, 145), 20, NAVY, (45, 84, 118), True)
    draw_text(d, (100, 770), "「意志の弱さ」ではなく治療が必要な病気として理解することが、本人・家族・支援者の第一歩です。", 30, WHITE, True, width=1650)
    executive_footer(img, "依存症を病気として理解することが、本人を責めず、家族も支え、専門支援につなぐ第一歩になります。", RED)
    return img


def slide_cross() -> Image.Image:
    img = make_slide(14)
    header(img, "交差依存（クロスアディクション）", "本命を止めても他の依存へ移り、最終的にスリップする悪循環", "悪循環を止める", 14)
    d = ImageDraw.Draw(img)
    cx, cy = 960, 520
    d.ellipse((cx - 205, cy - 205, cx + 205, cy + 205), outline=(176, 196, 215), width=8)
    nodes = [("本命をやめる", 960, 230, BLUE), ("苦しみが増える", 1330, 520, ORANGE), ("他の依存へ移行", 960, 810, GREEN), ("本命へ戻る", 590, 520, PURPLE)]
    for ttl, x, y, col in nodes:
        shadow_box(img, (x - 160, y - 55, 320, 110), 20, WHITE, LINE, True)
        pill(d, x - 132, y - 22, 42, 42, "", col)
        draw_text(d, (x - 78, y - 24), ttl, 24, NAVY, True, width=230)
    d.rounded_rectangle((815, 455, 1105, 585), 28, fill=BLUE)
    d.text((960, 520), "交差依存\nサイクル", font=font(31, True), fill=WHITE, anchor="mm")
    card(img, 60, 170, 390, 620, "依存のタイプ", ["物質依存：アルコール・薬物", "プロセス依存：ギャンブル・ネット", "関係依存：共依存など", "対象が変わっても病気は続く"], RED, 28, 21)
    card(img, 1470, 170, 390, 620, "予防策", ["早期介入", "包括的な再発予防", "12ステップとピア支援", "家族・専門職と共有", "生活全体の再設計"], GREEN, 28, 21)
    executive_footer(img, "交差依存では対象だけを止めるのではなく、生活全体を再設計し、代替行動と支援チームを作ることが必要です。", ORANGE)
    return img


def slide_paws() -> Image.Image:
    img = make_slide(15)
    header(img, "長期離脱症状（PAWS）の理解", "治療後に現れる長期離脱症状を理解し、波を乗り返しながら徐々に回復します", "12-24ヶ月", 15)
    symptoms = [("睡眠障害", "不眠・過眠・中途覚醒", BLUE), ("ストレス過敏", "音・視線・人混みに反応", ORANGE), ("記憶障害", "忘れる・覚えられない", GREEN), ("感情障害", "怒り・落ち込み・不安定", RED), ("身体バランス", "疲れやすい・めまい", PURPLE), ("思考障害", "集中力低下・判断ミス", PINK)]
    for i, (ttl, body, col) in enumerate(symptoms):
        x = 60 + (i % 3) * 620
        y = 165 + (i // 3) * 255
        card(img, x, y, 570, 210, ttl, [body, "症状の波を前提に、予定・睡眠・食事・相談を整えます。"], col, 28, 20)
    d = ImageDraw.Draw(img)
    shadow_box(img, (60, 710, 1770, 150), 20, WHITE, LINE, True)
    draw_text(d, (100, 740), "回復のプロセス", 30, NAVY, True)
    d.rounded_rectangle((405, 780, 1620, 810), 15, fill=(210, 222, 232))
    d.rounded_rectangle((405, 780, 760, 810), 15, fill=BLUE)
    d.rounded_rectangle((760, 780, 1180, 810), 15, fill=ORANGE)
    d.rounded_rectangle((1180, 780, 1620, 810), 15, fill=GREEN)
    draw_text(d, (405, 825), "急性期", 20, BLUE, True)
    draw_text(d, (760, 825), "波が出る時期", 20, ORANGE, True)
    draw_text(d, (1180, 825), "安定化", 20, GREEN, True)
    executive_footer(img, "PAWSの時期は症状の波を前提に、睡眠・食事・予定・相談を整え、一人で抱え込ませない体制が重要です。", BLUE)
    return img


def slide_family() -> Image.Image:
    img = make_slide(16)
    header(img, "家族支援プログラム（CRAFT／家族会）", "家族は回復の重要パートナー。ポジティブな関わりが変化を生む", "家族支援", 16)
    steps = [("1", "理解・学ぶ", BLUE), ("2", "相談・家族会", BLUE), ("3", "関わりを変える", BLUE), ("4", "パターンを断つ", BLUE), ("5", "継続と強化", BLUE)]
    d = ImageDraw.Draw(img)
    for i, (num, title, col) in enumerate(steps):
        x = 60 + i * 330
        shadow_box(img, (x, 170, 300, 320), 20, WHITE, LINE, True)
        pill(d, x + 102, 205, 96, 96, num, col, WHITE, 34)
        draw_text(d, (x + 35, 330), title, 27, NAVY, True, width=230)
        draw_text(d, (x + 35, 385), "本人を責めるのではなく、家族自身の安全と関わり方を整えます。", 19, MUTED, width=230)
    card(img, 60, 540, 860, 300, "援助の質を高めるポイント", ["原因探しをしすぎない", "責めない・さばかない", "回復行動を強化する", "タイミングを見て伝える", "家族だけで抱え込まない"], ORANGE, 28, 21)
    card(img, 960, 540, 870, 300, "家族会で扱うテーマ", ["依存症の正しい理解", "本人との距離の取り方", "境界線と安全確保", "相談・入所・治療へのつなぎ方", "家族自身の回復"], GREEN, 28, 21)
    executive_footer(img, "家族支援は、本人を動かすためだけでなく、家族自身の安全・理解・関わり方を再構築する支援です。", GREEN)
    return img


def slide_network() -> Image.Image:
    img = make_slide(17)
    header(img, "連携機関とネットワーク", "医療・行政・司法・地域と連携し、予防から社会復帰までを支援", "4つの連携分野", 17)
    nets = [
        ("医療（MEDICAL）", ["北里大学病院", "相模湖病院", "高尾厚生病院", "解毒入院後の受け皿"], BLUE),
        ("行政（PUBLIC）", ["相模原市精神保健福祉センター", "東京都多摩総合精神保健福祉センター", "福祉サービス利用調整"], GREEN),
        ("司法（JUSTICE）", ["横浜保護観察所", "府中刑務所", "八王子少年鑑別所", "弁護士・司法書士"], ORANGE),
        ("地域（COMMUNITY）", ["地域行政", "専門病院", "学校・教育", "企業・地域団体"], PURPLE),
    ]
    for i, (ttl, lines, col) in enumerate(nets):
        x = 60 + (i % 2) * 910
        y = 160 + (i // 2) * 355
        card(img, x, y, 860, 305, ttl, lines, col, 30, 22)
    executive_footer(img, "回復支援は施設内で完結しません。医療・福祉・司法・地域とつながることで、生活再建の選択肢が広がります。", PURPLE)
    return img


def slide_contact() -> Image.Image:
    img = make_slide(18)
    header(img, "お問い合わせ｜CHANGE YOUR LIFE!", "依存症からの回復を全力で支えます", "初回相談無料", 18)
    d = ImageDraw.Draw(img)
    draw_text(d, (450, 160), "CHANGE YOUR LIFE!", 58, NAVY, True)
    draw_text(d, (520, 238), "変われる。変われた仲間がいる。相模原ダルクは、依存症からの回復を全力で支えます。", 26, MUTED, True, width=980)
    card(img, 70, 350, 480, 220, "電話でのご相談", ["042-707-0391", "平日 9:00-17:00", "土・祝 9:00-14:00"], BLUE, 28, 22)
    card(img, 590, 350, 480, 220, "お問い合わせフォーム", ["https://s-darc.com", "24時間受付可能", "本人・家族・関係者から相談可"], GREEN, 28, 22)
    card(img, 1110, 350, 480, 220, "所在地", ["〒252-0237", "相模原市中央区千代田3-3-20", "日曜日定休"], ORANGE, 28, 22)
    shadow_box(img, (1160, 640, 580, 210), 24, BLUE, (64, 125, 255), True)
    draw_text(d, (1208, 665), "お電話でのご相談", 30, WHITE, True)
    draw_text(d, (1208, 715), "042-707-0391", 54, WHITE, True)
    draw_text(d, (1208, 795), "初回相談無料・秘密厳守", 27, (231, 245, 255), True)
    card(img, 70, 640, 1030, 210, "相談時に確認すること", ["本人・家族・関係者のどなたからの相談か", "依存対象、生活状況、緊急性、入所・見学希望", "電話またはフォームで連絡可能な時間帯"], PURPLE, 28, 22)
    executive_footer(img, "まずは相談から。本人・家族・関係者のどなたからでも、状況整理と次の一歩を一緒に考えます。", BLUE)
    return img


def build_images() -> list[Path]:
    strengths = [
        ("相模原ダルクの強み（1/3）", "400+ の中核能力", [
            ("実質的な実績", ["支援実績400名以上", "卒業継続率90%以上", "初回相談から入所まで一貫支援", "卒業後も地域で見守る"], BLUE),
            ("最新プログラム", ["科学的知見と実践経験を融合", "MATRIX/CBTベース", "12ステッププログラム", "個別カウンセリングを統合"], ORANGE),
            ("24時間見守り", ["初期回復の安全・安心を担保", "夜間スタッフ体制", "生活リズムを毎日確認", "孤立をつくらない環境"], GREEN),
            ("5段階ステージ制", ["回復の見える化", "役割・目標を明確化", "小さな達成を積み重ねる", "社会復帰まで道筋を設計"], PURPLE),
        ], BLUE),
        ("相模原ダルクの強み（2/3）", "70名 の中核能力", [
            ("関東圏最大規模の設備", ["大型寮で70名程度を受け入れ", "大空間デイケア＋個室寮", "生活訓練と居住を一体運用", "段階に応じた環境選択"], CYAN),
            ("当事者スタッフ多数在籍", ["経験者だからできる寄り添い", "深い共感と実践的助言", "否認をほどく対話力", "日常の変化に気づく観察力"], ORANGE),
            ("経験豊富な理事陣", ["法務・福祉・司法と連携する知見", "開設から10年以上の安定運営", "地域資源をつなぐ調整力", "制度利用の実務に対応"], GREEN),
            ("就労継続支援B型", ["自立に向けた就労ステップ", "短時間から開始可能", "作業習慣と責任感を育成", "社会参加の足場を作る"], PURPLE),
        ], GREEN),
        ("相模原ダルクの強み（3/3）", "24h の中核能力", [
            ("医療・行政・司法連携", ["保護観察所との連携", "医療機関との情報共有", "解毒入院後の受け皿", "裁判・保護観察中の支援"], BLUE),
            ("地域社会への参加", ["地域イベントでの演舞参加", "清掃ボランティア", "学校・地域での啓発活動", "回復者の役割づくり"], ORANGE),
            ("家族支援を継続", ["毎週の家族相談", "家族会・学習ミーティング", "CRAFT等を活用", "本人との関わり方を再設計"], GREEN),
            ("相談窓口を常設", ["初回相談無料・秘密厳守", "本人・家族・周囲から相談可", "入所・見学・各種依頼に対応", "電話/フォームで受付"], PURPLE),
        ], PURPLE),
    ]
    slides = [
        slide_cover(),
        slide_agenda(),
        slide_trend(),
        slide_prevention(),
        slide_philosophy(),
        slide_highlight(),
        slide_strength(7, *strengths[0]),
        slide_strength(8, *strengths[1]),
        slide_strength(9, *strengths[2]),
        slide_stages(),
        slide_facilities(),
        slide_programs(),
        slide_features(),
        slide_cross(),
        slide_paws(),
        slide_family(),
        slide_network(),
        slide_contact(),
    ]
    paths = []
    for i, im in enumerate(slides, 1):
        path = PNG_DIR / f"visual-slide-{i:02d}.png"
        im.convert("RGB").save(path, quality=95)
        paths.append(path)
    return paths


def build_pptx(paths: list[Path]) -> Path:
    prs = Presentation()
    prs.slide_width = Cm(33.867)
    prs.slide_height = Cm(19.05)
    blank = prs.slide_layouts[6]
    for p in paths:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(p), 0, 0, width=prs.slide_width, height=prs.slide_height)
    out = OUT_DIR / "sagamihara_darc_professional_presentation_2026.pptx"
    root_copy = ROOT / "Sagamihara_DARC_Professional_2026.pptx"
    prs.save(out)
    prs.save(root_copy)
    return root_copy


if __name__ == "__main__":
    image_paths = build_images()
    pptx = build_pptx(image_paths)
    print(pptx)
