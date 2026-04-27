from pathlib import Path

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Cm, Pt


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "artifacts" / "official"
OUT_DIR = ROOT / "artifacts" / "output"
PREVIEW_DIR = ROOT / "artifacts" / "generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

W = Cm(33.867)
H = Cm(19.05)

NAVY = RGBColor(13, 34, 58)
NAVY_2 = RGBColor(21, 58, 94)
BG = RGBColor(241, 246, 250)
WHITE = RGBColor(255, 255, 255)
TEXT = RGBColor(31, 44, 57)
MUTED = RGBColor(91, 107, 124)
LINE = RGBColor(215, 225, 232)
BLUE = RGBColor(45, 122, 255)
CYAN = RGBColor(22, 176, 205)
GREEN = RGBColor(23, 188, 139)
ORANGE = RGBColor(245, 164, 35)
RED = RGBColor(238, 87, 91)
PURPLE = RGBColor(133, 99, 255)
PINK = RGBColor(236, 88, 143)
DARK_CARD = RGBColor(18, 47, 75)

FONT = "Noto Sans JP"
FONT_EN = "Aptos Display"


def cm(v):
    return Cm(v)


def text(slide, x, y, w, h, value, size=12, color=TEXT, bold=False,
         align=PP_ALIGN.LEFT, font=FONT, leading=1.08):
    box = slide.shapes.add_textbox(cm(x), cm(y), cm(w), cm(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = cm(0.05)
    tf.margin_right = cm(0.05)
    tf.margin_top = cm(0.02)
    tf.margin_bottom = cm(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = leading
    run = p.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def multiline(slide, x, y, w, h, lines, size=11.0, color=MUTED, bullet=False):
    box = slide.shapes.add_textbox(cm(x), cm(y), cm(w), cm(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = cm(0.05)
    tf.margin_right = cm(0.05)
    tf.margin_top = cm(0.02)
    tf.margin_bottom = cm(0.02)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {line}" if bullet else line
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(4)
        p.line_spacing = 1.12
    return box


def rect(slide, x, y, w, h, fill, line=None, radius=False, transparency=0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, cm(x), cm(y), cm(w), cm(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.fill.transparency = transparency
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.7)
    return shp


def pill(slide, x, y, w, h, value, fill=BLUE, color=WHITE, size=9.5):
    shp = rect(slide, x, y, w, h, fill, radius=True)
    tf = shp.text_frame
    tf.clear()
    tf.margin_left = cm(0.15)
    tf.margin_right = cm(0.15)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = value
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color
    return shp


def image_cover(slide, path, x, y, w, h, overlay=None):
    if not Path(path).exists():
        return None
    im = Image.open(path)
    iw, ih = im.size
    box = w / h
    ratio = iw / ih
    if ratio > box:
        nh = h
        nw = h * ratio
    else:
        nw = w
        nh = w / ratio
    left = x - (nw - w) / 2
    top = y - (nh - h) / 2
    pic = slide.shapes.add_picture(str(path), cm(left), cm(top), width=cm(nw), height=cm(nh))
    pic.crop_left = max(0, (x - left) / nw)
    pic.crop_top = max(0, (y - top) / nh)
    pic.crop_right = max(0, (left + nw - (x + w)) / nw)
    pic.crop_bottom = max(0, (top + nh - (y + h)) / nh)
    if overlay:
        color, trans = overlay
        rect(slide, x, y, w, h, color, transparency=trans)
    return pic


def header(slide, title, subtitle="", tag="", icon="▣"):
    rect(slide, 0, 0, 33.867, 2.03, NAVY)
    pill(slide, 0.75, 0.45, 0.72, 0.72, icon, NAVY_2, WHITE, 10)
    text(slide, 1.72, 0.35, 20.5, 0.62, title, 20, WHITE, True)
    if subtitle:
        text(slide, 1.75, 1.1, 22, 0.42, subtitle, 8.8, RGBColor(190, 211, 226))
    if tag:
        pill(slide, 26.4, 0.55, 5.9, 0.58, tag, RGBColor(237, 243, 248), NAVY, 8.5)


def footer(slide, n, total=18):
    text(slide, 0.75, 18.3, 16, 0.35, "相模原ダルク｜依存症からの回復を全力で支えます", 7.2, MUTED)
    text(slide, 27.95, 18.24, 1.5, 0.35, f"{n}/{total}", 7.8, NAVY, True, PP_ALIGN.RIGHT, FONT_EN)
    rect(slide, 29.65, 18.36, 3.0, 0.08, LINE, radius=True)
    rect(slide, 29.65, 18.36, 3.0 * n / total, 0.08, GREEN if n == total else CYAN, radius=True)


def card(slide, x, y, w, h, title="", body=None, accent=BLUE, title_size=12.5):
    rect(slide, x, y, w, h, WHITE, LINE, radius=True)
    rect(slide, x, y, 0.08, h, accent)
    if title:
        text(slide, x + 0.35, y + 0.28, w - 0.7, 0.45, title, title_size, NAVY, True)
    if isinstance(body, list):
        multiline(slide, x + 0.35, y + 0.92, w - 0.7, h - 1.05, body, 9.8, MUTED, True)
    elif body:
        text(slide, x + 0.35, y + 0.92, w - 0.7, h - 1.0, body, 10.2, MUTED, leading=1.16)


def insight_strip(slide, x, y, w, title, items, accent=BLUE):
    rect(slide, x, y, w, 1.6, WHITE, LINE, radius=True)
    rect(slide, x, y, 0.08, 1.6, accent)
    text(slide, x + 0.35, y + 0.18, w - 0.7, 0.32, title, 9.2, NAVY, True)
    col_w = (w - 0.7) / len(items)
    for i, item in enumerate(items):
        ix = x + 0.35 + i * col_w
        pill(slide, ix, y + 0.73, 0.45, 0.45, str(i + 1), accent, WHITE, 7)
        text(slide, ix + 0.58, y + 0.66, col_w - 0.7, 0.45, item, 8.2, MUTED, True)


def dense_note(slide, x, y, w, h, title, body, accent=ORANGE):
    rect(slide, x, y, w, h, RGBColor(255, 249, 235), RGBColor(245, 219, 160), radius=True)
    rect(slide, x, y, 0.1, h, accent)
    text(slide, x + 0.35, y + 0.18, w - 0.7, 0.32, title, 8.8, NAVY, True)
    text(slide, x + 0.35, y + 0.62, w - 0.7, h - 0.78, body, 8.2, RGBColor(104, 83, 35), leading=1.16)


def kpi_card(slide, x, y, w, h, label, value, note, color=BLUE):
    rect(slide, x, y, w, h, DARK_CARD, RGBColor(35, 80, 118), radius=True)
    rect(slide, x, y, w, 0.1, color)
    text(slide, x + 0.35, y + 0.35, w - 0.7, 0.35, label, 7.6, RGBColor(184, 210, 226), True)
    text(slide, x + 0.35, y + 0.86, w - 0.7, 0.72, value, 19, WHITE, True, font=FONT_EN)
    text(slide, x + 0.35, y + 1.58, w - 0.7, 0.32, note, 6.8, RGBColor(184, 210, 226))


def mini_item(slide, x, y, color, title, body=""):
    pill(slide, x, y, 0.7, 0.7, "", color)
    text(slide, x + 0.95, y + 0.02, 5.5, 0.36, title, 9.8, NAVY, True)
    if body:
        text(slide, x + 0.95, y + 0.47, 5.8, 0.42, body, 7.7, MUTED)


def donut_png(path):
    im = Image.new("RGBA", (420, 420), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    bbox = (35, 35, 385, 385)
    start = -90
    parts = [(45.5, (45, 122, 255)), (45.1, (238, 87, 91)), (9.4, (23, 188, 139))]
    for pct, color in parts:
        d.arc(bbox, start, start + pct * 3.6, fill=color, width=72)
        start += pct * 3.6
    d.ellipse((135, 135, 285, 285), fill=(255, 255, 255, 255))
    im.save(path)


def bg(slide):
    rect(slide, 0, 0, 33.867, 19.05, BG)


def add_logo(slide, x=0.82, y=0.55, dark=False):
    logo = ASSET_DIR / "logo03.png"
    if logo.exists():
        slide.shapes.add_picture(str(logo), cm(x), cm(y), height=cm(0.62))
    else:
        text(slide, x, y, 4, 0.4, "DARC", 12, WHITE if dark else NAVY, True, font=FONT_EN)


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    blank = prs.slide_layouts[6]
    slides = [prs.slides.add_slide(blank) for _ in range(18)]

    # 1 cover
    s = slides[0]
    rect(s, 0, 0, 33.867, 19.05, RGBColor(7, 25, 45))
    rect(s, 17.0, 0, 16.867, 19.05, RGBColor(16, 131, 134), transparency=0.12)
    image_cover(s, ASSET_DIR / "facility_main.jpg", 20.2, 0, 13.7, 19.05, (RGBColor(7, 25, 45), 0.55))
    add_logo(s, 1.25, 0.9, True)
    pill(s, 20.9, 0.72, 10.1, 0.72, "2026年4月25日  横浜ひまわり家族会採用", RGBColor(21, 58, 94), WHITE, 9.2)
    text(s, 3.7, 3.2, 12.5, 1.0, "CHANGE", 28, WHITE, True, font=FONT_EN)
    text(s, 3.7, 4.3, 12.5, 1.0, "YOUR LIFE!", 28, GREEN, True, font=FONT_EN)
    text(s, 16.0, 3.05, 18, 3.0, "DARC", 88, RGBColor(220, 242, 240), True, font=FONT_EN)
    text(s, 3.7, 6.6, 13.2, 0.8, "依存症からの回復支援施設・施設紹介 2026", 14.5, WHITE, True)
    text(s, 3.7, 8.0, 14.2, 1.2, "変われる。変わった仲間がいる。\n安心できる共同の場と誠実な対話を通じて、当事者の生き直す力を呼び起こします。", 10.5, RGBColor(214, 229, 238))
    rect(s, 3.7, 9.7, 13.8, 2.6, RGBColor(14, 48, 78), RGBColor(38, 88, 122), True)
    text(s, 4.15, 10.05, 12.8, 0.42, "本資料の位置づけ", 11.5, WHITE, True)
    text(s, 4.15, 10.75, 12.7, 0.95, "家族会・医療福祉関係者・行政/司法関係者に向けて、相模原ダルクの支援体制、実績、回復プログラム、連携方法を短時間で理解できるよう再構成した説明資料です。", 8.8, RGBColor(209, 228, 239), leading=1.2)
    metrics = [("回復支援実績", "400+", "名以上", BLUE), ("卒業継続率", "90+", "%以上", GREEN), ("安心の見守り", "24h", "体制", ORANGE), ("連携ネットワーク", "7", "拠点", PURPLE)]
    for i, m in enumerate(metrics):
        kpi_card(s, 1.45 + i * 7.75, 14.2, 7.1, 2.35, *m)
    dense_note(s, 3.7, 10.1, 13.8, 2.3, "本資料の位置づけ", "家族会・相談面談・関係機関説明で使える施設紹介資料。依存症の理解、回復プログラム、家族支援、連携体制まで一気通貫で説明します。", GREEN)
    pill(s, 3.7, 12.85, 3.7, 0.56, "相談", BLUE, WHITE, 8.8)
    pill(s, 7.75, 12.85, 3.7, 0.56, "入所", GREEN, WHITE, 8.8)
    pill(s, 11.8, 12.85, 3.7, 0.56, "回復", ORANGE, WHITE, 8.8)
    text(s, 1.45, 17.6, 12, 0.35, "〒252-0237 神奈川県相模原市中央区千代田3-3-20", 6.8, RGBColor(162, 187, 202))
    text(s, 28.3, 17.6, 3.5, 0.35, "042-707-0391", 6.8, RGBColor(162, 187, 202), False, PP_ALIGN.RIGHT)

    # 2 agenda
    s = slides[1]; bg(s); header(s, "本日のご説明内容｜本日のテーマ", "依存症からの回復支援体制、5ステージ制プログラム、実績、連携ネットワークについて", "予定時間：約60分", "▣")
    agenda = [
        ("01", "日本の依存症情勢（2024-2025）", "最新の薬物事犯検挙と若年層の依存症傾向分析", BLUE),
        ("02", "予防の3段階と当施設の役割", "第一次・第二次予防のフレームワークと実践", GREEN),
        ("03", "組織概要・理念と実績", "2014年設立、400名以上の支援実績", ORANGE),
        ("04", "相模原ダルクの8つの強み", "回復支援の核心となる8つの競争優位性", RED),
        ("05", "5ステージ制回復プログラム", "段階的な目標設定と役割付与による自立支援", PURPLE),
        ("06", "施設・サービスの全体像", "5つの拠点と支援機能のネットワーク", BLUE),
        ("07", "回復プログラム詳細", "デイ・ナイト・個別の包括的アプローチ", GREEN),
        ("08", "依存症の理解（7つの特徴）", "科学的理解に基づく回復支援の前提条件", ORANGE),
        ("09", "家族支援・連携ネットワーク", "CRAFTプログラムと地域連携体制", RED),
        ("10", "お問い合わせ", "初回相談無料・秘密厳守", PURPLE),
    ]
    for i, (n, title, sub, color) in enumerate(agenda):
        col = 0 if i < 5 else 1
        row = i if i < 5 else i - 5
        x, y = 1.5 + col * 15.8, 3.25 + row * 2.6
        rect(s, x, y, 14.5, 1.95, WHITE, LINE, True)
        pill(s, x + 0.35, y + 0.43, 1.28, 1.05, n, color, WHITE, 11)
        text(s, x + 1.95, y + 0.38, 11.6, 0.42, title, 11.6, NAVY, True)
        text(s, x + 1.95, y + 0.95, 11.6, 0.4, sub, 7.8, MUTED)
    insight_strip(s, 1.5, 16.25, 30.3, "資料を読む視点", ["依存症を病気として理解する", "回復の仕組みを段階で把握する", "家族・地域・専門職の役割を整理する", "相談につながる行動を決める"], BLUE)
    insight_strip(s, 1.5, 16.35, 30.3, "本資料の使い方", ["相談前の全体説明", "家族会での共有", "関係機関への紹介", "入所検討時の判断材料"], BLUE)
    footer(s, 2)

    # 3 trend
    s = slides[2]; bg(s); header(s, "日本の依存症情勢 2024-2025最新", "薬物・アルコール・ギャンブル依存が複合化するなか、早期相談と地域支援が重要に", "2024-2025", "▤")
    card(s, 1.25, 3.05, 14.4, 4.2, "2024年 薬物事犯 検挙人員", None, BLUE)
    text(s, 2.1, 4.22, 7.0, 1.1, "13,462", 33, NAVY, True, font=FONT_EN)
    text(s, 9.5, 4.15, 4.5, 0.45, "前年比 +13,462人", 8.5, GREEN, True)
    text(s, 2.1, 5.75, 10.8, 0.42, "覚醒剤 45.5%　　大麻 45.1%", 10, MUTED, True)
    donut = PREVIEW_DIR / "donut.png"; donut_png(donut)
    card(s, 1.25, 8.0, 14.4, 7.4, "薬物事犯の内訳", None, NAVY)
    s.shapes.add_picture(str(donut), cm(5.2), cm(9.0), height=cm(4.9))
    mini_item(s, 2.1, 13.2, RED, "覚醒剤", "45.5%")
    mini_item(s, 7.0, 13.2, BLUE, "大麻", "45.1%")
    mini_item(s, 11.2, 13.2, GREEN, "その他", "9.4%")
    card(s, 17.0, 3.05, 14.9, 7.4, "注目トピック（2024-25）", None, NAVY)
    for i, item in enumerate([("大麻類似法改正", "2024年12月施行", CYAN), ("SNS売買急増", "若年層で急増", BLUE), ("暴力団関与", "覚醒剤事犯約50%", GREEN)]):
        x = 17.8 + i * 4.55
        rect(s, x, 5.0, 3.7, 3.6, RGBColor(249, 252, 255), LINE, True)
        pill(s, x + 1.45, 5.55, 0.8, 0.8, "", item[2])
        text(s, x + 0.35, 6.65, 3.0, 0.5, item[0], 9.3, NAVY, True, PP_ALIGN.CENTER)
        text(s, x + 0.35, 7.35, 3.0, 0.45, item[1], 7.5, MUTED, False, PP_ALIGN.CENTER)
    card(s, 17.0, 11.05, 14.9, 3.0, "重要なポイント", "2024年12月に大麻取締法が改正され、SNSを介した若年層の薬物売買が増加しています。暴力団は覚醒剤事犯に関与し続けています。", ORANGE)
    insight_strip(s, 1.25, 15.35, 30.65, "支援現場で押さえる論点", ["若年層の入口はSNS化し、早期発見が難しい", "大麻・処方薬・市販薬・ギャンブル等の複合化に注意", "本人だけでなく家族支援を同時に設計する", "医療・福祉・司法への早期接続が再発を減らす"], ORANGE)
    insight_strip(s, 17.0, 14.55, 14.9, "相談現場で押さえる視点", ["若年層の入口", "SNS経由の拡大", "複合依存", "早期相談の重要性"], ORANGE)
    footer(s, 3)

    # 4 prevention role
    s = slides[3]; bg(s); header(s, "3段階予防と相模原ダルクの役割", "第一次：啓発／第二次：早期介入／第三次：リハビリ・社会復帰", "予防から回復まで", "●")
    text(s, 1.4, 2.55, 25, 0.5, "相模原ダルクは、予防から社会復帰まで切れ目ない支援を提供します。第一次予防、第二次予防、第三次予防（回復・社会復帰）の3段階で、依存症の予防と回復を実現します。", 10.5, MUTED)
    text(s, 29.0, 2.55, 3.0, 0.8, "400+", 20, NAVY, True, font=FONT_EN)
    stages = [
        ("第一次予防（啓発）", ["講演・研修による乱用防止啓発", "学校・地域イベントでのエイサー演舞", "学校への薬物乱用防止教室", "ニュースレター発行"], BLUE),
        ("第二次予防（介入）", ["医療・行政・司法と連携した早期発見", "個別相談と初期カウンセリング", "家族からの相談対応", "弁護士・専門職との連携"], ORANGE),
        ("第三次予防（回復）", ["入寮・通所による集中的な回復プログラム", "24時間体制の見守りサポート", "アフターケアと地域連携の継続", "社会復帰支援"], GREEN),
    ]
    for i, (title, rows, color) in enumerate(stages):
        x = 1.25 + i * 10.75
        card(s, x, 4.05, 10.05, 11.7, title, rows, color, 13.0)
    insight_strip(s, 1.25, 16.05, 31.0, "相模原ダルクが担う接続機能", ["啓発で孤立を防ぐ", "相談で問題を整理する", "入寮・通所で生活を立て直す", "地域連携で社会参加へつなぐ"], GREEN)
    insight_strip(s, 1.25, 16.05, 31.0, "3段階を切れ目なく接続", ["啓発で入口を減らす", "相談で孤立を止める", "入寮・通所で生活を整える", "地域連携で定着させる"], GREEN)
    footer(s, 4)

    # 5 philosophy
    s = slides[4]; bg(s); header(s, "組織概要・理念｜PHILOSOPHY & MISSION", "人としての尊厳を大切に、生き直す力を支える", "設立 2014年", "▣")
    card(s, 1.4, 3.2, 7.0, 11.6, "相模原ダルク", ["設立：2014年3月3日", "代表理事：田中 秀泰", "所在地：神奈川県相模原市", "支援実績：延べ400名以上"], BLUE)
    card(s, 9.4, 3.2, 22.1, 4.6, "PHILOSOPHY｜理念", "「人としての尊厳を大切に、生き直す力を支える」全員が一人ひとりを尊重する関係性を大切にし、安心して自分を表現できる共同の場をつくります。", BLUE)
    card(s, 9.4, 8.45, 22.1, 5.8, "MISSION｜使命", "「生き直す力で依存症からの回復を」依存症からの回復には、人が本来持つ生き直す力を呼び起こし、育てることが必要不可欠です。恐れや圧力ではなく、安心できる環境、誠実な人との関わりや対話によって育てます。", GREEN)
    insight_strip(s, 1.4, 15.2, 30.1, "理念を支援に落とし込む3つの原則", ["尊厳：本人を問題行動だけで見ない", "安心：失敗を責めず、語れる環境をつくる", "対話：仲間と支援者の関わりで生き直す力を育てる"], BLUE)
    insight_strip(s, 9.4, 14.85, 22.1, "理念を実務に落とす4つの姿勢", ["尊厳を守る", "安心の場をつくる", "対話を重ねる", "回復をあきらめない"], BLUE)
    footer(s, 5)

    # 6 highlight
    s = slides[5]; bg(s); header(s, "実績ハイライト｜データで見る相模原ダルク", "開設以来400名以上の依存症当事者を支援し、再使用率低減と卒業後継続率を追求", "400名以上の支援実績", "▣")
    text(s, 1.4, 2.65, 23.5, 0.62, "相模原ダルクは、創設以来400名以上の依存症当事者を支援し、5%以下の再使用率、90%以上の卒業後継続率を達成しています。", 12.2, NAVY, True)
    highlights = [("400", "名以上", "回復支援実績", "多様な依存対象・背景を持つ当事者を継続的に支援", BLUE), ("5", "%以下", "入所中の再使用率", "徹底した見守りとプログラムによりリスクを低減", RED), ("90", "%以上", "卒業後の継続率", "医療・所属先・地域と接続して定着を支援", GREEN), ("70", "名程度", "受け入れ体制", "大型寮と個室寮で段階的な自立をサポート", PURPLE)]
    for i, (v, unit, title, body, color) in enumerate(highlights):
        x = 1.35 + i * 8.05
        card(s, x, 5.0, 7.25, 9.45, "", None, color)
        pill(s, x + 2.9, 5.7, 1.2, 1.2, "", color)
        text(s, x + 0.5, 7.1, 4.2, 1.25, v, 30, NAVY, True, PP_ALIGN.RIGHT, FONT_EN)
        text(s, x + 4.85, 7.75, 1.6, 0.45, unit, 12, MUTED, True)
        text(s, x + 0.6, 9.0, 6.05, 0.55, title, 13, NAVY, True, PP_ALIGN.CENTER)
        text(s, x + 0.7, 10.1, 5.85, 1.25, body, 9.0, MUTED, False, PP_ALIGN.CENTER)
        rect(s, x + 0.75, 13.05, 5.7, 0.12, LINE, radius=True)
        rect(s, x + 0.75, 13.05, 4.7 if i != 1 else 0.7, 0.12, color, radius=True)
    insight_strip(s, 1.35, 15.0, 31.45, "数字が示す価値", ["生活環境とプログラムを同時に整える", "見守りと役割付与で再使用リスクを下げる", "卒業後も地域・家族・専門職と接続する", "段階別支援で社会参加へ橋渡しする"], CYAN)
    insight_strip(s, 1.35, 15.1, 31.4, "数字の見せ方", ["支援実績", "再使用リスク", "卒業後継続", "受け入れ体制", "地域連携"], GREEN)
    footer(s, 6)

    # 7-9 strengths
    strength_sets = [
        ("相模原ダルクの強み（1/3）", "実質的な実績／最新プログラム／24時間見守り／5段階ステージ制", "400+", [
            ("実質的な実績", ["テーマで寄り添った回復支援", "支援実績400名以上", "継続率90%以上", "初回相談から入所まで一貫支援", "卒業後も地域で見守る"], BLUE),
            ("最新プログラム", ["科学的知見と実践経験を融合", "MATRIX/CBTベースの再発予防", "12ステッププログラム", "個別カウンセリングを統合", "毎年アップデートを継続"], ORANGE),
            ("24時間見守り", ["初期回復の安全・安心を担保", "夜間スタッフ体制", "緊急リスクを軽減", "生活リズムを毎日確認", "孤立をつくらない環境"], GREEN),
            ("5段階ステージ制", ["回復の見える化と段階的自立", "役割・目標を明確化", "本人の主体性を育てる", "小さな達成を積み重ねる", "社会復帰まで道筋を設計"], PURPLE),
        ]),
        ("相模原ダルクの強み（2/3）", "関東圏最大規模の設備／当事者スタッフ／経験豊富な理事陣／就労継続支援B型", "70名", [
            ("関東圏最大規模の設備", ["大型寮で70名程度を受け入れ", "大空間デイケア＋個室寮", "専用車での送迎支援あり", "生活訓練と居住を一体運用", "段階に応じた環境選択"], CYAN),
            ("当事者スタッフ多数在籍", ["経験者だからできる寄り添い", "深い共感と実践的助言", "ピア支援で回復を後押し", "否認をほどく対話力", "日常の変化に気づく観察力"], ORANGE),
            ("経験豊富な理事陣", ["法務・福祉・司法と連携する知見", "開設から10年以上の安定運営", "組織全体で回復にコミット", "地域資源をつなぐ調整力", "制度利用の実務に対応"], GREEN),
            ("就労継続支援B型", ["自立に向けた就労のステップ", "短時間から開始可能", "一般就労へのステップとして機能", "作業習慣と責任感を育成", "社会参加の足場を作る"], PURPLE),
        ]),
        ("相模原ダルクの強み（3/3）", "医療・行政・司法連携／地域社会への参加／家族支援／相談窓口を常設", "24h", [
            ("医療・行政・司法連携", ["KRPP/FLOW/TANARPP等への協力", "保護観察所との連携", "医療機関との情報共有", "解毒入院後の受け皿", "裁判・保護観察中の支援"], BLUE),
            ("地域社会への参加", ["地域イベントでの演舞参加", "清掃ボランティアの実施", "学校・地域での啓発活動", "偏見を減らす発信活動", "回復者の役割づくり"], ORANGE),
            ("家族支援を継続", ["毎週の家族相談を実施", "月1回の家族会・学習ミーティング", "CRAFT等を活用", "家族の疲弊を軽減", "本人との関わり方を再設計"], GREEN),
            ("相談窓口を常設", ["初回相談無料・秘密厳守", "本人・家族・周囲の方でも対応", "平日9:00-17:00／土祝9:00-14:00", "入所・見学・各種依頼に対応", "電話/フォームで受付"], PURPLE),
        ]),
    ]
    for idx, (title, sub, tag, rows) in enumerate(strength_sets, start=7):
        s = slides[idx - 1]; bg(s); header(s, title, sub, f"{tag} の中核能力", "★")
        text(s, 1.35, 2.65, 25.0, 0.7, "相模原ダルクは、依存症からの回復を全力で支えます。医療・行政・司法・地域・家族をつなぎ、包括的な回復支援を提供します。", 11.6, NAVY, True)
        for i, (ttl, bullets, color) in enumerate(rows):
            x = 1.25 + (i % 2) * 15.8
            y = 4.05 + (i // 2) * 5.15
            card(s, x, y, 14.6, 4.85, ttl, bullets, color, 13.2)
        insight_strip(s, 1.25, 14.95, 30.4, "強みを支える運用原則", ["当事者性", "24時間の安心", "段階的な役割", "専門職連携", "家族支援"], BLUE if idx == 7 else GREEN if idx == 8 else PURPLE)
        footer(s, idx)

    # 10 five stages
    s = slides[9]; bg(s); header(s, "5ステージ制 回復プログラム", "段階的な目標設定と具体的な治療プログラムによる回復ロードマップ", "5段階のステップ", "▦")
    stages = [("MEMBER", "0-3ヶ月", BLUE, ["基礎知識の学習", "共同生活への適応", "生活習慣の再構築", "毎日の振り返り", "安全確保を優先"]), ("SUPPORT", "3-6ヶ月", ORANGE, ["掃除・調理など役割付与", "プログラム参加継続", "振り返りの習慣化", "後輩への声かけ", "生活課題の整理"]), ("TRAINEE", "6-12ヶ月", GREEN, ["リーダーシップの練習", "他者支援への参加", "外部活動への接続", "再発予防計画", "家族関係の再構築"]), ("CHIEF", "12-18ヶ月", PURPLE, ["後輩への声かけ", "面談・相談の補助", "自立準備の具体化", "就労準備を開始", "地域資源を活用"]), ("MANAGER", "18ヶ月-", PINK, ["運営補助", "社会参加・就労準備", "再発予防計画の完成", "退寮後の計画", "支える側への移行"])]
    for i, (name, period, color, bullets) in enumerate(stages):
        x = 1.0 + i * 6.55
        card(s, x, 4.0, 6.0, 10.6, "", None, color)
        pill(s, x + 0.35, 4.35, 5.3, 0.85, f"{name}\n{period}", color, WHITE, 8.5)
        multiline(s, x + 0.45, 5.7, 5.1, 5.0, bullets, 8.2, MUTED, True)
        text(s, x + 0.45, 12.55, 5.1, 1.15, "達成基準\n生活安定・役割達成・次段階の準備", 8.0, color, True)
    insight_strip(s, 1.0, 15.25, 32.0, "ステージ制の狙い", ["回復を可視化", "小さな成功体験", "役割で自己効力感", "再発予防計画", "社会参加へ接続"], PURPLE)
    footer(s, 10)

    # 11 facilities
    s = slides[10]; bg(s); header(s, "相模原ダルクグループ", "5つの拠点と依存症支援を支える包括的ネットワーク", "全体像の説明", "▦")
    image_cover(s, ASSET_DIR / "facility_main.jpg", 1.2, 3.2, 9.0, 5.0, None)
    card(s, 10.6, 3.2, 9.8, 5.0, "相模原ダルク デイケアセンター", ["各種依存症の総合相談窓口", "日中活動・プログラム提供", "医療・行政連携の中心"], BLUE)
    image_cover(s, ASSET_DIR / "business01.jpg", 21.0, 3.2, 9.0, 5.0, None)
    card(s, 1.2, 9.0, 6.9, 3.3, "大和PCC", "プライマリーケア機能／生活再建と共同生活支援", GREEN)
    card(s, 8.7, 9.0, 6.9, 3.3, "町田RC", "リカバリーセンター／段階的な自立準備", ORANGE)
    card(s, 16.2, 9.0, 6.9, 3.3, "愛川TC", "トリートメントセンター／集中回復環境", PURPLE)
    card(s, 23.7, 9.0, 6.9, 3.3, "上溝HRC", "ヒーリングセンター／生活改善と回復支援", BLUE)
    card(s, 1.2, 13.0, 14.4, 2.6, "相模原WPH", "就労準備ホーム。自立に集中できる住環境を提供。", GREEN)
    card(s, 16.2, 13.0, 14.4, 2.6, "相模原DTC", "オキュペーショントレーニングセンター。作業訓練・社会参加を支援。", ORANGE)
    insight_strip(s, 1.2, 16.0, 29.4, "施設群の価値", ["相談", "生活訓練", "就労準備", "個室寮", "地域移行"], BLUE)
    footer(s, 11)

    # 12 programs
    s = slides[11]; bg(s); header(s, "回復プログラム（デイ・ナイト・個別）", "デイケア、ナイトケア、個別サポートの3つのプログラムを組み合わせて包括支援", "3つの支援プログラム", "▦")
    text(s, 1.35, 2.55, 25.0, 0.55, "回復プログラムは、デイケア（通所）、ナイトケア（寮）、個別サポートの3つのプログラムを統合した包括的な支援体制です。", 11.5, NAVY, True)
    programs = [("デイケア（通所）", "仲間と学ぶ・話し合う", ["ミーティング／プログラム", "12ステッププログラム", "SAGARP（再発予防CBT）", "ワークショップ・アート", "感情・認知の整理", "日中活動の習慣化"], BLUE), ("ナイトケア（寮）", "生活の基盤づくりと習慣化", ["生活習慣の改善", "金銭・食事の管理", "入寮生活の安定", "24時間体制", "睡眠リズムの回復", "共同生活での役割"], ORANGE), ("個別サポート", "状況に合わせた個別支援", ["個別面談", "債務・司法相談", "家族支援", "就労準備", "医療・福祉との調整", "退寮後の生活設計"], GREEN)]
    for i, (ttl, sub, rows, color) in enumerate(programs):
        x = 1.35 + i * 10.55
        card(s, x, 4.7, 9.5, 10.35, ttl, rows, color, 13.5)
        text(s, x + 0.5, 5.78, 8.0, 0.35, sub, 9.0, color, True)
    insight_strip(s, 1.35, 15.25, 30.6, "3プログラムを組み合わせる理由", ["日中活動", "夜間の安全", "個別課題", "家族対応", "司法・債務"], GREEN)
    footer(s, 12)

    # 13 seven features
    s = slides[12]; bg(s); header(s, "依存症の理解（7つの特徴）", "科学的理解に基づく回復支援の前提条件", "7つの特徴", "◆")
    text(s, 1.3, 2.5, 26, 0.62, "依存症は、7つの特徴を持つ複雑な病気です。これらを正しく理解することで、適切な治療アプローチを選択し、回復への道筋を確立できます。", 11.4, NAVY, True)
    features = [("一次性の病気", "原因は依存症そのもの。意思や性格の問題ではありません。", BLUE), ("慢性の病気", "完治ではなく、やめ続けるためのケアが必要です。", GREEN), ("進行性の病気", "放置すれば失うものが大きくなります。", ORANGE), ("死亡率が高い", "事故・自殺・オーバードーズ等のリスクがあります。", RED), ("性格が変化する", "病気の進行に伴い、人間関係が崩れます。", PURPLE), ("依存対象が他へ移行", "交差依存により、対象が移ることがあります。", PINK), ("人を巻き込む病気", "家族・周囲への影響と支援が重要です。", CYAN)]
    for i, (ttl, body, color) in enumerate(features):
        x = 1.1 + (i % 4) * 8.0
        y = 4.2 + (i // 4) * 4.6
        card(s, x, y, 7.3, 3.8, ttl, body, color, 11)
    rect(s, 1.3, 15.05, 30.9, 0.9, NAVY, radius=True)
    text(s, 1.7, 15.28, 29.5, 0.38, "「意志の弱さ」ではなく治療が必要な病気としての理解が、回復への第一歩です", 10.8, WHITE, True, PP_ALIGN.CENTER)
    insight_strip(s, 1.3, 16.25, 30.9, "理解が変わると支援が変わる", ["責めない", "孤立させない", "専門支援へつなぐ", "家族も支える", "継続を前提にする"], RED)
    footer(s, 13)

    # 14 cross addiction
    s = slides[13]; bg(s); header(s, "交差依存（クロスアディクション）", "「本命を止めても他の依存へ移り、最終的にスリップする悪循環」", "注意：悪循環を止める", "↻")
    text(s, 1.3, 2.6, 26.4, 0.55, "交差依存は、本命の依存をやめても他の依存へ移行し、最終的にスリップする構造です。適切な対策を取ることで、依存の対象が変化しながら依存症が継続します。", 10.8, NAVY, True)
    center_x, center_y = 16.2, 9.8
    rect(s, center_x - 2.3, center_y - 1.4, 4.6, 2.8, BLUE, radius=True)
    text(s, center_x - 1.4, center_y - 0.55, 2.8, 0.5, "本命へ戻る", 14, WHITE, True, PP_ALIGN.CENTER)
    for i, (ttl, desc, color, x, y) in enumerate([
        ("第一の依存をやめる", "覚醒剤・酒など", BLUE, 14.0, 4.1),
        ("本命へ戻る", "スリップ・再使用", PURPLE, 14.0, 13.2),
        ("他の依存へ移行", "処方薬・ギャンブル", GREEN, 8.0, 9.0),
        ("苦しみが増える", "不安・渇望", ORANGE, 23.2, 9.0),
        ("本命の依存をやめる", "治療開始", RED, 3.2, 6.0),
    ]):
        card(s, x, y, 7.2, 2.6, ttl, desc, color, 10.5)
    card(s, 26.0, 4.2, 5.8, 4.2, "悪循環の流れ", ["本命の依存をやめる", "苦しみが増える", "他の依存へ移行", "本命へ戻る"], ORANGE)
    card(s, 26.0, 9.2, 5.8, 3.8, "予防策", ["早期介入", "包括的な再発予防", "ピア支援・12ステップ"], GREEN)
    insight_strip(s, 1.3, 14.75, 24.0, "交差依存への対応", ["対象ではなく病気を見る", "生活全体を整える", "代替行動を設計", "早期に共有する"], ORANGE)
    footer(s, 14)

    # 15 PAWS
    s = slides[14]; bg(s); header(s, "長期離脱症状（PAWS）の理解", "治療後に現れる長期離脱症状を理解し、波を乗り返しながら徐々に回復します", "12-24ヶ月の期間", "◆")
    text(s, 1.4, 2.55, 22.5, 0.55, "PAWSは、治療後に現れる長期離脱症状です。「波を乗り返しながら徐々に回復します。」", 12, NAVY, True)
    text(s, 25.5, 2.45, 2.5, 0.7, "3-6", 20, NAVY, True, font=FONT_EN)
    text(s, 28.8, 2.45, 2.8, 0.7, "12-24", 20, NAVY, True, font=FONT_EN)
    symptoms = [("睡眠障害", "不眠・過眠・中途覚醒", BLUE), ("ストレス過敏", "音・視線・人混みへの過敏", ORANGE), ("記憶障害", "覚えられない・忘れる", GREEN), ("感情障害", "怒りっぽい・情緒不安定", RED), ("身体バランス", "疲れやすい・めまい", PURPLE), ("思考障害", "集中力低下・判断ミス", PINK)]
    for i, (ttl, body, color) in enumerate(symptoms):
        x = 1.25 + (i % 3) * 10.75
        y = 4.6 + (i // 3) * 4.25
        card(s, x, y, 9.8, 3.4, ttl, body, color, 12)
    rect(s, 2.0, 15.2, 22.5, 0.22, LINE, radius=True)
    rect(s, 2.0, 15.2, 6.0, 0.22, BLUE, radius=True)
    rect(s, 8.0, 15.2, 8.5, 0.22, ORANGE, radius=True)
    rect(s, 16.5, 15.2, 8.0, 0.22, GREEN, radius=True)
    text(s, 2.0, 15.7, 22.5, 0.4, "回復のプロセス：「波を乗り返しながら、徐々に回復に向かいます」", 9.0, MUTED)
    rect(s, 11.6, 16.6, 17.0, 0.6, RGBColor(255, 231, 233), RGBColor(255, 190, 196), True)
    text(s, 12.0, 16.75, 16.0, 0.3, "この時期のスリップに注意。一人で抱えずチームで支援", 8.5, RED, True, PP_ALIGN.CENTER)
    insight_strip(s, 1.25, 16.05, 9.7, "支援者の対応", ["睡眠", "食事", "予定", "相談"], BLUE)
    footer(s, 15)

    # 16 CRAFT
    s = slides[15]; bg(s); header(s, "家族支援プログラム（CRAFT／家族会）", "家族は回復の重要パートナー。ポジティブな関わりが変化を生む", "家族支援", "♣")
    text(s, 1.35, 2.55, 25, 0.62, "家族支援プログラムは、CRAFT（Community Reinforcement and Family Training）を基盤とし、家族が依存症者を支援するための実践的なスキルと知識を提供します。", 11.2, NAVY, True)
    steps = [("1", "理解・学ぶ", "依存症の正しい知識とCRAFTの基本"), ("2", "相談・家族会", "仲間との分かち合い"), ("3", "関わりを変える", "効果的な対話と境界線設定"), ("4", "パターンを断つ", "巻き込まれを減らす"), ("5", "継続と強化", "回復行動を支える")]
    for i, (n, ttl, body) in enumerate(steps):
        x = 1.3 + i * 4.45
        card(s, x, 5.1, 4.0, 5.0, "", None, BLUE)
        pill(s, x + 1.45, 5.65, 1.0, 1.0, n, BLUE, WHITE, 12)
        text(s, x + 0.35, 7.1, 3.3, 0.5, ttl, 10.2, NAVY, True, PP_ALIGN.CENTER)
        text(s, x + 0.35, 8.0, 3.3, 0.9, body, 7.5, MUTED, False, PP_ALIGN.CENTER)
    card(s, 24.2, 5.1, 7.4, 8.4, "援助の質を高める5つのポイント", ["原因を探さない", "責めない・さばかない", "知っておくべきこと", "タイミングがすべて", "ネイティブな言葉を避ける"], GREEN)
    card(s, 1.3, 11.2, 22.0, 2.7, "援助の質を高めるポイント", "家族は回復の重要パートナーです。ポジティブな関わりが依存症者の変化を生み出します。", ORANGE)
    insight_strip(s, 1.3, 14.45, 30.3, "家族支援で目指す変化", ["知識を得る", "巻き込まれを減らす", "対話を変える", "安全を守る", "本人を支援へつなぐ"], GREEN)
    footer(s, 16)

    # 17 network
    s = slides[16]; bg(s); header(s, "連携機関とネットワーク", "医療・行政・司法・地域と連携し、予防から社会復帰までを支援", "計4つの連携分野", "▦")
    text(s, 1.35, 2.55, 25.5, 0.62, "相模原ダルクは、2026年1月時点の最新情報を反映しています。協定書・覚書に基づく正式連携および実績ベースの協力関係を含み、包括的な支援ネットワークを構築しています。", 10.6, NAVY, True)
    nets = [("医療（MEDICAL PARTNERS）", ["北里大学病院", "相模湖病院", "高尾厚生病院"], BLUE), ("行政（PUBLIC SECTOR）", ["相模原市精神保健福祉センター", "東京都多摩総合精神保健福祉センター"], GREEN), ("司法（JUSTICE）", ["横浜保護観察所", "府中刑務所", "八王子少年鑑別所"], ORANGE), ("地域（COMMUNITY）", ["地域行政", "専門病院", "学校", "企業"], PURPLE)]
    for i, (ttl, rows, color) in enumerate(nets):
        x = 1.25 + (i % 2) * 15.8
        y = 4.35 + (i // 2) * 5.35
        card(s, x, y, 14.6, 4.35, ttl, rows, color, 12.4)
    insight_strip(s, 1.25, 15.05, 30.4, "ネットワーク活用の場面", ["医療受診", "福祉サービス", "刑事裁判", "債務整理", "地域定着"], PURPLE)
    footer(s, 17)

    # 18 contact
    s = slides[17]; bg(s); header(s, "お問い合わせ｜CHANGE YOUR LIFE!", "依存症からの回復を全力で支えます", "初回相談無料", "♪")
    text(s, 7.2, 3.0, 19.5, 0.95, "CHANGE YOUR LIFE!", 29, NAVY, True, PP_ALIGN.CENTER, FONT_EN)
    text(s, 8.1, 4.15, 17.8, 0.55, "変われる。変われた仲間がいる。相模原ダルクは、依存症からの回復を全力で支えます。", 11.2, MUTED, True, PP_ALIGN.CENTER)
    card(s, 1.4, 6.0, 8.2, 3.0, "電話でのご相談", ["042-707-0391", "平日 9:00-17:00／土祝 9:00-14:00"], BLUE)
    card(s, 10.2, 6.0, 8.2, 3.0, "お問い合わせフォーム", ["https://s-darc.com", "24時間受付可能"], GREEN)
    card(s, 19.0, 6.0, 8.2, 3.0, "所在地", ["〒252-0237", "相模原市中央区千代田3-3-20"], ORANGE)
    card(s, 1.4, 10.1, 8.2, 4.4, "ご相談できる内容", ["入所したい", "見学したい", "家族として相談したい", "医療・司法・行政からの依頼", "講演・啓発活動の依頼"], CYAN)
    rect(s, 20.6, 10.1, 10.8, 4.4, BLUE, radius=True)
    text(s, 21.3, 10.55, 9.6, 0.55, "お電話でのご相談", 13, WHITE, True, PP_ALIGN.CENTER)
    text(s, 21.3, 11.45, 9.6, 1.2, "042-707-\n0391", 27, WHITE, True, PP_ALIGN.CENTER, FONT_EN)
    text(s, 21.3, 13.1, 9.6, 0.4, "受付：平日9:00-17:00／土祝9:00-14:00", 8.2, RGBColor(215, 230, 255), False, PP_ALIGN.CENTER)
    rect(s, 20.6, 15.0, 10.8, 0.8, RGBColor(255, 232, 235), RGBColor(255, 187, 195), True)
    text(s, 21.0, 15.18, 10.0, 0.35, "初回相談無料・秘密厳守", 11.2, RED, True, PP_ALIGN.CENTER)
    card(s, 10.2, 10.1, 8.2, 4.4, "運営情報", ["一般社団法人 相模原ダルク", "代表理事：田中 秀泰", "日曜定休"], PURPLE)
    insight_strip(s, 1.4, 15.95, 18.4, "相談時に確認すること", ["本人/家族", "依存対象", "緊急度", "入所希望", "連絡方法"], BLUE)
    footer(s, 18)

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if not r.font.name:
                            r.font.name = FONT

    out = OUT_DIR / "sagamihara_darc_professional_presentation_2026.pptx"
    prs.save(out)
    root_copy = ROOT / "Sagamihara_DARC_Professional_2026.pptx"
    prs.save(root_copy)
    print(out)
    print(root_copy)


if __name__ == "__main__":
    build()
