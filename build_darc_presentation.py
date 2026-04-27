from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Cm, Pt


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "artifacts" / "output"
ASSET_DIR = ROOT / "artifacts" / "official"
OUT_DIR.mkdir(parents=True, exist_ok=True)


W = Cm(33.867)
H = Cm(19.05)

NAVY = RGBColor(9, 28, 50)
NAVY_2 = RGBColor(13, 47, 80)
TEAL = RGBColor(0, 149, 158)
TEAL_2 = RGBColor(32, 181, 184)
GREEN = RGBColor(20, 122, 92)
GOLD = RGBColor(225, 169, 74)
WHITE = RGBColor(255, 255, 255)
OFFWHITE = RGBColor(247, 250, 249)
MIST = RGBColor(232, 241, 239)
TEXT = RGBColor(28, 38, 47)
MUTED = RGBColor(83, 96, 109)
LINE = RGBColor(205, 219, 219)
RED = RGBColor(196, 72, 64)

FONT = "Noto Sans JP"
FONT_EN = "Aptos"


def cm(value):
    return Cm(value)


def add_bg(slide, color=OFFWHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_textbox(slide, x, y, w, h, text, size=18, color=TEXT, bold=False,
                align=PP_ALIGN.LEFT, font=FONT, line_spacing=1.0):
    box = slide.shapes.add_textbox(cm(x), cm(y), cm(w), cm(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_multiline(slide, x, y, w, h, lines, size=17, color=TEXT, bullet=False,
                  gap=0, bold_first=False):
    box = slide.shapes.add_textbox(cm(x), cm(y), cm(w), cm(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = cm(0.05)
    tf.margin_right = cm(0.05)
    tf.margin_top = cm(0.03)
    tf.margin_bottom = cm(0.03)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        p.space_after = Pt(gap)
        if bullet:
            p.text = f"・{line}"
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold_first and i == 0
        p.line_spacing = 1.13
    return box


def add_pill(slide, x, y, w, h, text, fill=TEAL, color=WHITE, size=12):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cm(x), cm(y), cm(w), cm(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    tf = shape.text_frame
    tf.clear()
    tf.margin_left = cm(0.25)
    tf.margin_right = cm(0.25)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.name = FONT_EN
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color
    return shape


def add_title(slide, title, subtitle=None, section="SAGAMIHARA DARC"):
    add_textbox(slide, 1.55, 1.0, 16.2, 0.55, section, 10.5, TEAL, True, font=FONT_EN)
    add_textbox(slide, 1.5, 1.55, 20.8, 1.55, title, 30, NAVY, True)
    if subtitle:
        add_textbox(slide, 1.55, 3.12, 20.8, 0.9, subtitle, 12.5, MUTED)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(1.55), cm(4.22), cm(5.0), cm(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = TEAL
    line.line.fill.background()


def add_footer(slide, num):
    add_textbox(slide, 1.5, 18.05, 6, 0.35, "相模原ダルク｜回復支援施設", 8.5, MUTED)
    add_textbox(slide, 30.5, 18.05, 1.5, 0.35, f"{num:02d}", 8.5, MUTED, align=PP_ALIGN.RIGHT, font=FONT_EN)


def image_cover(slide, path, x, y, w, h, transparency_overlay=None):
    src = Image.open(path)
    sw, sh = src.size
    box_ratio = w / h
    img_ratio = sw / sh
    if img_ratio > box_ratio:
        new_h = h
        new_w = h * img_ratio
    else:
        new_w = w
        new_h = w / img_ratio
    left = x - (new_w - w) / 2
    top = y - (new_h - h) / 2
    pic = slide.shapes.add_picture(str(path), cm(left), cm(top), width=cm(new_w), height=cm(new_h))
    crop_l = max(0, (x - left) / new_w)
    crop_t = max(0, (y - top) / new_h)
    crop_r = max(0, (left + new_w - (x + w)) / new_w)
    crop_b = max(0, (top + new_h - (y + h)) / new_h)
    pic.crop_left = crop_l
    pic.crop_top = crop_t
    pic.crop_right = crop_r
    pic.crop_bottom = crop_b
    if transparency_overlay is not None:
        overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(x), cm(y), cm(w), cm(h))
        overlay.fill.solid()
        overlay.fill.fore_color.rgb = transparency_overlay[0]
        overlay.fill.transparency = transparency_overlay[1]
        overlay.line.fill.background()
    return pic


def add_card(slide, x, y, w, h, title, body=None, accent=TEAL, title_size=18):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cm(x), cm(y), cm(w), cm(h))
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = LINE
    card.line.width = Pt(0.7)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(x), cm(y), cm(0.12), cm(h))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    add_textbox(slide, x + 0.45, y + 0.35, w - 0.8, 0.55, title, title_size, NAVY, True)
    if body:
        if isinstance(body, list):
            add_multiline(slide, x + 0.45, y + 1.12, w - 0.8, h - 1.35, body, 12.2, MUTED, bullet=True, gap=3)
        else:
            add_textbox(slide, x + 0.45, y + 1.12, w - 0.8, h - 1.35, body, 12.2, MUTED)
    return card


def add_metric(slide, x, y, label, value, note, color=TEAL):
    add_textbox(slide, x, y, 5.0, 0.45, label, 10.5, MUTED, True)
    add_textbox(slide, x, y + 0.45, 5.7, 1.0, value, 30, color, True, font=FONT_EN)
    add_textbox(slide, x, y + 1.42, 5.9, 0.65, note, 10.8, MUTED)


def create_deck():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    blank = prs.slide_layouts[6]

    slides = []
    for _ in range(12):
        slides.append(prs.slides.add_slide(blank))

    # 01 Cover
    s = slides[0]
    add_bg(s, NAVY)
    image_cover(s, ASSET_DIR / "facility_main.jpg", 16.0, 0, 17.9, 19.05, (NAVY, 0.15))
    grad = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, cm(19.0), H)
    grad.fill.solid()
    grad.fill.fore_color.rgb = NAVY
    grad.fill.transparency = 0.02
    grad.line.fill.background()
    if (ASSET_DIR / "logo03.png").exists():
        s.shapes.add_picture(str(ASSET_DIR / "logo03.png"), cm(1.55), cm(1.15), height=cm(1.3))
    add_pill(s, 1.55, 4.15, 5.2, 0.65, "RECOVERY SUPPORT / 2026", TEAL)
    add_textbox(s, 1.5, 5.25, 16.2, 2.2, "生き直す力で、\n依存症からの回復を。", 34, WHITE, True)
    add_textbox(s, 1.58, 8.05, 13.7, 1.2, "人としての尊厳を大切に、安心して自分を表現できる共同の場をつくります。", 15, MIST)
    add_textbox(s, 1.55, 16.55, 9.0, 0.5, "一般社団法人 相模原ダルク", 13.5, WHITE, True)
    add_textbox(s, 1.55, 17.15, 12.8, 0.45, "アルコール依存症・薬物依存症・ギャンブル依存症の回復支援施設", 9.5, MIST)
    add_footer(s, 1)

    # 02 Executive message
    s = slides[1]
    add_bg(s)
    add_title(s, "この資料で伝えること", "相模原ダルクの支援価値を、紹介・相談・連携の場面でそのまま使える形に整理。")
    items = [
        ("01", "依存症は「意思の弱さ」ではなく、正しい理解と継続的支援が必要な病気です。"),
        ("02", "相模原ダルクは、安心できる共同の場と専門プログラムで回復を支えます。"),
        ("03", "本人・家族・医療・行政・司法・地域がつながることで、回復の可能性は広がります。"),
    ]
    for i, (n, text) in enumerate(items):
        y = 5.15 + i * 3.1
        add_textbox(s, 2.0, y, 1.6, 0.7, n, 20, TEAL, True, font=FONT_EN)
        add_textbox(s, 3.85, y - 0.05, 24.0, 1.0, text, 21, NAVY, True)
        line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(3.85), cm(y + 1.1), cm(22.5), cm(0.03))
        line.fill.solid()
        line.fill.fore_color.rgb = LINE
        line.line.fill.background()
    add_footer(s, 2)

    # 03 Philosophy
    s = slides[2]
    add_bg(s)
    image_cover(s, ASSET_DIR / "outline01.jpg", 22.2, 0, 11.7, 19.05, (NAVY, 0.35))
    add_title(s, "理念と使命", "公式サイト掲載の理念・使命を、支援現場で伝わる言葉に再編集。")
    add_card(s, 1.55, 5.1, 9.8, 5.0, "理念", [
        "人としての尊厳を大切にする",
        "安心して自分を表現できる共同の場をつくる",
        "誠実な関わりと対話で、生き直す力を育てる",
    ], TEAL)
    add_card(s, 12.0, 5.1, 9.8, 5.0, "使命", [
        "依存症からの回復支援を通じて社会に貢献する",
        "恐れや圧力ではなく、安心できる環境を整える",
        "地域・社会の中に共同の場をつくり続ける",
    ], GREEN)
    add_textbox(s, 2.1, 12.05, 18.8, 1.4, "依存症は困難な病気です。\nそれでも、私たちは回復をあきらめません。", 25, NAVY, True)
    add_footer(s, 3)

    # 04 Problem framing
    s = slides[3]
    add_bg(s, RGBColor(250, 252, 252))
    add_title(s, "依存症を取り巻く課題", "本人だけでなく、家族・職場・地域にも影響が広がるため、孤立させない支援が必要です。")
    problems = [
        ("コントロール困難", "飲酒・薬物・ギャンブル等をやめようとしても繰り返してしまう"),
        ("生活バランスの崩れ", "仕事・家庭・健康よりも依存対象が優先され、孤立が進む"),
        ("家族・周囲への影響", "会話の減少、口論、経済問題、関係悪化が重なっていく"),
        ("再発リスク", "離脱症状や強い欲求により、ひとりでは継続が難しい"),
    ]
    for i, (title, body) in enumerate(problems):
        x = 1.65 + (i % 2) * 15.3
        y = 5.0 + (i // 2) * 4.25
        add_card(s, x, y, 13.8, 3.25, title, body, [RED, GOLD, TEAL, GREEN][i], 17)
    add_pill(s, 10.6, 14.35, 12.6, 0.75, "必要なのは、正しい理解と専門的な治療・支援", NAVY, WHITE, 13)
    add_footer(s, 4)

    # 05 Recovery model
    s = slides[4]
    add_bg(s)
    add_title(s, "相模原ダルクの回復支援モデル", "安全な環境、仲間との関わり、専門機関連携を組み合わせて、回復の継続を支えます。")
    steps = [
        ("相談", "本人・家族・周囲の方から状況を丁寧に聴く"),
        ("安心できる場", "共同生活・日中活動を通じて孤立をほどく"),
        ("プログラム", "回復段階に応じて生活訓練・就労支援を行う"),
        ("社会参加", "医療・福祉・司法・地域とつながり直す"),
    ]
    for i, (title, body) in enumerate(steps):
        x = 1.8 + i * 7.8
        add_pill(s, x, 5.2, 1.25, 1.25, f"{i+1}", TEAL if i < 3 else GREEN, WHITE, 20)
        add_textbox(s, x, 6.8, 6.5, 0.55, title, 18, NAVY, True)
        add_textbox(s, x, 7.55, 6.5, 1.4, body, 12.5, MUTED)
        if i < 3:
            arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, cm(x + 5.9), cm(5.55), cm(1.2), cm(0.55))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = LINE
            arrow.line.fill.background()
    add_textbox(s, 2.0, 12.25, 28.5, 1.0, "「一人でやめ続ける」から、「仲間と支援につながり続ける」へ。", 26, NAVY, True, align=PP_ALIGN.CENTER)
    add_footer(s, 5)

    # 06 Services
    s = slides[5]
    add_bg(s)
    add_title(s, "事業内容", "障害福祉サービス、入寮、相談、連携、予防啓発を一体的に展開。")
    services = [
        ("01", "障害福祉サービス", "自立訓練（生活訓練）／就労継続支援B型"),
        ("02", "入寮事業", "依存症治療専用ナイトケアハウスを運営"),
        ("03", "相談事業", "本人・家族・周囲の方など、どなたでも相談可能"),
        ("04", "連携・協力事業", "医療機関・行政機関・地域団体とネットワーク形成"),
        ("05", "予防・啓発事業", "講演活動や地域イベントを通じた啓発"),
    ]
    for i, (n, title, body) in enumerate(services):
        x = 1.55 + (i % 3) * 10.45
        y = 5.05 + (i // 3) * 4.45
        w = 9.35 if i < 3 else 14.25
        if i >= 3:
            x = 4.25 + (i - 3) * 15.1
        add_card(s, x, y, w, 3.45, f"{n}  {title}", body, TEAL if i % 2 == 0 else GREEN, 15.5)
    add_footer(s, 6)

    # 07 Supported addictions
    s = slides[6]
    add_bg(s, RGBColor(249, 252, 251))
    add_title(s, "対応できる依存症・関連課題", "公式サイト掲載の主要領域を、相談時に見渡せる一覧に。")
    cols = [
        ("主要領域", ["アルコール依存症", "薬物依存症", "ギャンブル依存症"]),
        ("広がる相談領域", ["ゲーム・ネット・スマホ依存", "処方薬・市販薬依存", "大麻・危険ドラッグ依存"]),
        ("関連課題", ["窃盗依存（クレプトマニア）", "性依存・性嗜好障害", "共依存"]),
    ]
    for i, (title, rows) in enumerate(cols):
        add_card(s, 1.75 + i * 10.35, 5.0, 9.2, 7.2, title, rows, [TEAL, GREEN, GOLD][i], 17)
    add_textbox(s, 2.0, 13.5, 28.9, 1.2, "初期段階の相談から、入所・生活再建・家族支援・司法/債務課題まで、状況に応じてつなげます。", 18, NAVY, True, align=PP_ALIGN.CENTER)
    add_footer(s, 7)

    # 08 Facility and living support
    s = slides[7]
    add_bg(s)
    image_cover(s, ASSET_DIR / "business02.jpg", 0, 0, 14.5, 19.05, (NAVY, 0.28))
    add_textbox(s, 15.4, 1.25, 14.8, 0.55, "RESIDENTIAL CARE", 10.5, TEAL, True, font=FONT_EN)
    add_textbox(s, 15.35, 1.8, 15.8, 1.45, "入寮事業と安心できる住環境", 28, NAVY, True)
    add_textbox(s, 15.45, 3.5, 15.0, 1.0, "依存症治療専用ナイトケアハウス（寮）を運営。集団療法の効果を高める大型寮と、自立準備のための個室寮を用意しています。", 13.5, MUTED)
    add_metric(s, 15.55, 5.35, "大型寮", "5", "集団療法の効果を最大化", TEAL)
    add_metric(s, 22.4, 5.35, "個室寮", "9", "自立に向けた練習環境", GREEN)
    add_metric(s, 15.55, 8.25, "費用", "176,000円", "月額・税込／生活保護の方は相談可", GOLD)
    add_card(s, 15.55, 11.7, 14.7, 3.35, "大切にしていること", [
        "安全で安心して暮らせること",
        "回復初期から中期・後期まで段階に応じて支えること",
        "日々の生活そのものを回復の土台にすること",
    ], TEAL)
    add_footer(s, 8)

    # 09 Consultation
    s = slides[8]
    add_bg(s)
    add_title(s, "相談から支援につながるまで", "本人・家族・友人知人・関係機関など、どなたでも相談可能です。秘密は守られます。")
    flow = [
        ("1", "問い合わせ", "電話・Webフォームから相談"),
        ("2", "状況整理", "依存対象、生活、家族、医療・司法課題を確認"),
        ("3", "見学・面談", "本人の意向と安全を確認し、支援方針を検討"),
        ("4", "利用開始", "相談・通所・入寮・連携支援へ接続"),
    ]
    for i, (n, title, body) in enumerate(flow):
        y = 5.0 + i * 2.55
        add_pill(s, 2.0, y, 1.3, 1.3, n, TEAL, WHITE, 18)
        add_textbox(s, 3.7, y + 0.03, 7.0, 0.55, title, 17.5, NAVY, True)
        add_textbox(s, 10.0, y + 0.03, 18.8, 0.8, body, 14.5, MUTED)
    add_card(s, 2.0, 15.0, 27.8, 1.55, "相談費用", "初回無料／2回目以降 3,000円（税込）", GREEN, 17)
    add_footer(s, 9)

    # 10 Partnership
    s = slides[9]
    add_bg(s)
    image_cover(s, ASSET_DIR / "business01.jpg", 22.6, 0, 11.3, 19.05, (NAVY, 0.38))
    add_title(s, "連携で回復の可能性を広げる", "医療・福祉・行政・司法・地域団体とつながり、本人と家族を孤立させない。")
    partners = [
        ("医療機関", "解毒入院、薬物療法、精神科・身体面の治療と連携"),
        ("行政・福祉", "障害福祉サービス、生活保護、地域生活支援につなぐ"),
        ("司法・専門職", "刑事裁判支援、債務整理支援などを弁護士・司法書士と連携"),
        ("地域・教育", "予防啓発、講演、イベント参加を通じて理解を広げる"),
    ]
    for i, (title, body) in enumerate(partners):
        add_card(s, 1.65 + (i % 2) * 10.3, 5.0 + (i // 2) * 4.15, 9.3, 3.25, title, body, [TEAL, GREEN, GOLD, TEAL_2][i], 16)
    add_footer(s, 10)

    # 11 Credibility / outline
    s = slides[10]
    add_bg(s, RGBColor(250, 252, 252))
    add_title(s, "施設概要", "相談先として必要な基本情報を1枚に集約。")
    rows = [
        ("事業者", "一般社団法人 相模原ダルク"),
        ("代表理事", "田中 秀泰"),
        ("設立", "2014年3月3日"),
        ("所在地", "〒252-0237 神奈川県相模原市中央区千代田3-3-20"),
        ("TEL / FAX", "TEL 042-707-0391 / FAX 042-707-0392"),
        ("営業時間", "平日 9:00-17:00／土・祝 9:00-14:00（日曜定休）"),
    ]
    y = 5.0
    for k, v in rows:
        add_textbox(s, 2.0, y, 5.0, 0.5, k, 12.2, TEAL, True)
        add_textbox(s, 7.2, y, 20.5, 0.6, v, 15, NAVY, True if k in ["事業者", "TEL / FAX"] else False)
        line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(2.0), cm(y + 0.78), cm(26.5), cm(0.025))
        line.fill.solid()
        line.fill.fore_color.rgb = LINE
        line.line.fill.background()
        y += 1.55
    add_textbox(s, 2.0, 15.3, 26.5, 0.7, "※ 事前予約によりデイケア横の駐車スペースが利用可能。", 11.5, MUTED)
    add_footer(s, 11)

    # 12 Closing
    s = slides[11]
    add_bg(s, NAVY)
    image_cover(s, ASSET_DIR / "activity.jpg", 18.7, 0, 15.2, 19.05, (NAVY, 0.24))
    add_pill(s, 1.55, 2.0, 4.8, 0.65, "CONTACT", TEAL)
    add_textbox(s, 1.55, 3.2, 15.9, 1.9, "まず一歩、\nご相談ください。", 36, WHITE, True)
    add_textbox(s, 1.65, 6.25, 14.0, 1.0, "同じ悩みを抱える方々から、多数ご相談をいただいています。本人・ご家族・関係者、どなたでもご相談ください。", 14.5, MIST)
    add_card(s, 1.65, 9.0, 13.8, 4.8, "お問い合わせ", [
        "TEL：042-707-0391",
        "Web：https://s-darc.com/contact/",
        "営業時間：平日 9:00-17:00／土・祝 9:00-14:00",
        "定休日：日曜日",
    ], TEAL)
    add_textbox(s, 1.65, 15.7, 12.8, 0.5, "CHANGE YOUR LIFE!", 20, TEAL_2, True, font=FONT_EN)
    add_textbox(s, 1.65, 16.35, 15.0, 0.55, "変われる。変われた仲間がいる。共に変わろう。共に進もう。", 13.2, WHITE, True)
    add_footer(s, 12)

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if not r.font.name:
                            r.font.name = FONT

    out = OUT_DIR / "sagamihara_darc_professional_presentation_2026.pptx"
    prs.save(out)
    return out


if __name__ == "__main__":
    path = create_deck()
    print(path)
