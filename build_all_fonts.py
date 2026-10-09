# -*- coding: utf-8 -*-
"""
전체 폰트 목록 페이지 빌드 스크립트 — 개인 참고용, 라이선스 체크 없이 전 폰트 임베딩
사용: python build_all_fonts.py all_fonts.src.html all_fonts.html
"""
import sys, io, base64, json, re
from collections import defaultdict
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

sys.stdout.reconfigure(encoding='utf-8')
SRC, OUT = sys.argv[1], sys.argv[2]
CATALOG = 'C:/Users/user/fonts/_tools/fonts_catalog.json'

SAMPLE_KO = '가나다라마바사아자차카타파하'
SAMPLE_EN = 'ABCDEFGabcdefg0123456789'
SAMPLE_CHARS = set(SAMPLE_KO + SAMPLE_EN + ' ')

# TPO 태그: 제목 / 본문 / UI앱 / 브랜드 / SNS콘텐츠 / 손글씨 / 귀여운 / 게임 / 픽셀레트로 / 명조세리프
TAGS = {
    '01_꾸불림체':         ['손글씨', 'SNS콘텐츠'],
    '02_기랑해랑체':        ['손글씨', 'SNS콘텐츠'],
    '03_의청수윤영체':       ['손글씨', 'SNS콘텐츠'],
    '04_OK단단체':         ['제목', '브랜드'],
    '05_느좋체':           ['제목', 'SNS콘텐츠'],
    '06_와일드각체':        ['제목', '브랜드'],
    '07_메모먼트꾹꾹체':     ['손글씨', 'SNS콘텐츠'],
    '08_어그로체':         ['제목', '브랜드', 'SNS콘텐츠'],
    '09_양진체':           ['귀여운', 'SNS콘텐츠'],
    '10_하이커체':         ['제목', '브랜드'],
    '11_페어큰부리새':       ['제목', '브랜드'],
    '12_온글잎박다현':       ['손글씨', 'SNS콘텐츠'],
    '13_온글잎의연':        ['손글씨', 'SNS콘텐츠'],
    '14_온글잎쑴':         ['손글씨', 'SNS콘텐츠'],
    '15_온글잎콘콘':        ['손글씨', 'SNS콘텐츠'],
    '16_빙그레메로나':       ['귀여운', 'SNS콘텐츠', '브랜드'],
    '17_빙그레따옴':        ['귀여운', 'SNS콘텐츠'],
    '18_갈무리픽셀':        ['픽셀레트로', '게임'],
    '19_네오둥근모픽셀':     ['픽셀레트로', '게임'],
    '20_페이퍼로지':        ['제목', '브랜드', 'UI앱'],
    '21_SUIT':            ['본문', 'UI앱'],
    '22_배민주아체':        ['브랜드', '제목', 'SNS콘텐츠'],
    '23_배민도현체':        ['본문', 'UI앱'],
    '24_배민연성체':        ['귀여운', 'SNS콘텐츠'],
    '25_여기어때잘난체':     ['제목', '브랜드'],
    '26_에스코어드림':       ['본문', 'UI앱'],
    '27_카페24써라운드':     ['제목', '브랜드'],
    '28_카페24당당해':       ['귀여운', 'SNS콘텐츠'],
    '29_카페24빛나는별':     ['손글씨', 'SNS콘텐츠'],
    '30_지마켓산스':        ['본문', 'UI앱', '브랜드'],
    '31_검은고딕':         ['제목', '브랜드'],
    '32_프리텐다드':        ['본문', 'UI앱'],
    '33_원티드산스':        ['본문', 'UI앱'],
    '34_쿠키런':           ['귀여운', '게임', 'SNS콘텐츠'],
    '35_마루부리':         ['명조세리프', '본문'],
    '36_나눔스퀘어라운드':   ['본문', 'UI앱'],
    '37_나눔손글씨붓':       ['손글씨', 'SNS콘텐츠'],
    '38_티몬몬소리체':       ['제목', 'SNS콘텐츠'],
    '39_롯데리아촵땡겨':     ['귀여운', 'SNS콘텐츠'],
    '40_롯데리아딱붙어':     ['귀여운', 'SNS콘텐츠'],
    '41_해피니스산스타이틀':  ['제목', '브랜드'],
    '42_넥슨Lv2고딕':       ['게임', 'UI앱'],
    '43_메이플스토리':       ['귀여운', '게임'],
    '44_삼립호빵체':        ['귀여운', 'SNS콘텐츠'],
    '45_롯데자이언츠':       ['브랜드', '제목'],
    '46_파셜산스':         ['본문', 'UI앱'],
    '47_티몬티움':         ['본문', 'UI앱'],
    '48_HS집토끼라운드':     ['귀여운', 'SNS콘텐츠'],
    '49_HS산토끼':         ['귀여운', 'SNS콘텐츠'],
    '50_카페24쑥쑥':        ['손글씨', 'SNS콘텐츠'],
    '51_카페24숑숑':        ['귀여운', 'SNS콘텐츠'],
    '52_카페24슈퍼매직':     ['제목', 'SNS콘텐츠'],
    '53_달서힐링':         ['손글씨', 'SNS콘텐츠'],
    '54_가나초콜릿':        ['귀여운', 'SNS콘텐츠'],
    '55_온글잎시우':        ['손글씨', 'SNS콘텐츠'],
    '56_나눔펜':           ['손글씨', 'SNS콘텐츠'],
    '57_나눔바른펜':        ['손글씨', 'SNS콘텐츠'],
    '58_어비세현':         ['손글씨', 'SNS콘텐츠'],
    '59_KCC김훈':          ['손글씨', 'SNS콘텐츠'],
    '60_하이멜로디':        ['손글씨', '귀여운', 'SNS콘텐츠'],
    '61_감자꽃':           ['귀여운', 'SNS콘텐츠'],
    '62_잉크립퀴드':        ['손글씨', '브랜드'],
    '63_라인시드':         ['본문', 'UI앱'],
    '64_해피니스산스':       ['본문', 'UI앱'],
    '65_IBM플렉스산스':      ['본문', 'UI앱'],
    '66_인피니티산스':       ['본문', 'UI앱'],
    '67_리디바탕':         ['명조세리프', '본문'],
    '68_아리따부리':        ['명조세리프', '브랜드'],
    '69_카페24고운밤':       ['손글씨', '명조세리프', 'SNS콘텐츠'],
    '70_조선일보명조':       ['명조세리프', '본문'],
    '71_둥근모':           ['픽셀레트로'],
    '72_도스명조':         ['픽셀레트로'],
    '73_던파비트':         ['픽셀레트로', '게임'],
    '74_이사만루':         ['제목', '브랜드', '게임'],
    '75_학교안심고른제목':   ['제목', 'UI앱'],
    '76_학교안심꼬꼬마':     ['귀여운', 'SNS콘텐츠'],
    '77_학교안심꽈배기':     ['귀여운', 'SNS콘텐츠'],
    '78_학교안심꾸러기':     ['귀여운', 'SNS콘텐츠'],
    '79_학교안심별자리':     ['귀여운', 'SNS콘텐츠'],
    '80_학교안심맑은날':     ['본문', 'UI앱'],
    '81_학교안심나무':       ['본문', 'UI앱'],
    '82_학교안심소나기':     ['귀여운', 'SNS콘텐츠'],
    '83_학교안심봄방학':     ['손글씨', 'SNS콘텐츠'],
    '84_학교안심모험가':     ['제목', 'SNS콘텐츠'],
    '85_학교안심몽글몽글':   ['귀여운', 'SNS콘텐츠'],
    '86_학교안심그림일기':   ['귀여운', 'SNS콘텐츠'],
    '87_온글잎다경':        ['손글씨', 'SNS콘텐츠'],
    '88_온글잎재선':        ['손글씨', 'SNS콘텐츠'],
    '89_온글잎주빈':        ['손글씨', 'SNS콘텐츠'],
    '90_넷마블':           ['게임', '브랜드'],
    '91_카트라이더':        ['게임', '브랜드'],
    '92_마비노기':         ['게임', '브랜드'],
    '93_워헤이븐':         ['게임', '제목'],
    '94_던파포지드':        ['게임', '제목'],
    '95_가비아봄바람':       ['손글씨', 'SNS콘텐츠'],
    '96_가비아청연':        ['명조세리프', '브랜드'],
    '97_가비아마음결':       ['손글씨', 'SNS콘텐츠'],
    '98_가비아납작블록':     ['제목', '브랜드'],
    '99_가비아솔미':        ['귀여운', 'SNS콘텐츠'],
    '100_카페24모야모야':    ['귀여운', 'SNS콘텐츠'],
    '101_카페24오스퀘어':    ['본문', 'UI앱'],
    '102_카페24러빙유':      ['브랜드', '제목'],
    '103_잠실체':          ['제목', '브랜드'],
    '104_서울남산':         ['본문', 'UI앱'],
    '105_서울한강':         ['본문', 'UI앱'],
    '106_티웨이하늘':        ['손글씨', 'SNS콘텐츠'],
    '107_추사사랑':         ['손글씨', 'SNS콘텐츠'],
    '108_단조':            ['제목', '브랜드'],
    '109_한돈삼겹살':        ['귀여운', 'SNS콘텐츠'],
    '110_땅스부대찌개':      ['귀여운', 'SNS콘텐츠'],
    '111_설레임':           ['귀여운', 'SNS콘텐츠'],
    '112_수박화채':         ['귀여운', 'SNS콘텐츠'],
    '113_KoPub바탕':        ['명조세리프', '본문'],
    '114_이서윤체':         ['손글씨', 'SNS콘텐츠'],
    '115_제주돌담체':        ['손글씨', 'SNS콘텐츠'],
    '116_부크크명조':        ['명조세리프', '본문'],
    '117_HS여름물빛체':      ['손글씨', 'SNS콘텐츠'],
    '118_한국기계연구원':     ['본문', 'UI앱'],
    '119_부크크고딕':        ['본문', 'UI앱'],
    '120_몬세라트':         ['제목', '브랜드'],
    '121_피플퍼스트자립':     ['본문', 'UI앱'],
    '122_신촌랩소디':        ['손글씨', 'SNS콘텐츠'],
    '123_속초바다':         ['명조세리프', 'SNS콘텐츠'],
    '124_가평물결':         ['손글씨', 'SNS콘텐츠'],
    'Diphylleia':          ['명조세리프', '브랜드'],
    'Pretendard':          ['본문', 'UI앱'],
    '125_나눔고딕':         ['본문', 'UI앱'],
    '126_나눔명조':         ['명조세리프', '본문'],
    '127_카카오큰글씨':      ['제목', '브랜드', 'UI앱'],
    '128_카카오작은글씨':     ['본문', 'UI앱'],
    '129_스포카한산스네오':   ['본문', 'UI앱', '브랜드'],
    '130_한겨레결체':        ['명조세리프', '브랜드'],
    '131_닉곤폰트':         ['제목', '브랜드'],
    '132_고운돋움':         ['본문', 'UI앱'],
    '133_고운바탕':         ['명조세리프', '본문'],
    '134_강원교육튼튼체':    ['귀여운', 'SNS콘텐츠'],
    '135_강원교육새음체':    ['귀여운', 'SNS콘텐츠'],
    '136_강원교육모두체':    ['귀여운', 'UI앱'],
    '137_이롭게바탕':        ['명조세리프', '본문'],
}

ALL_TAGS = ['제목', '본문', 'UI앱', '브랜드', 'SNS콘텐츠', '손글씨', '귀여운', '게임', '픽셀레트로', '명조세리프']
TAG_LABELS = {
    '제목':    '📌 제목·헤드라인',
    '본문':    '📖 본문·긴글',
    'UI앱':   '📱 앱·웹 UI',
    '브랜드':  '✦ 브랜딩·로고',
    'SNS콘텐츠': '📷 SNS·콘텐츠',
    '손글씨':  '✍ 손글씨',
    '귀여운':  '🐱 귀여운·캐릭터',
    '게임':   '🎮 게임',
    '픽셀레트로': '👾 픽셀·레트로',
    '명조세리프': '🖋 명조·세리프',
}

data = json.load(open(CATALOG, encoding='utf-8'))

by_folder = defaultdict(list)
for d in data:
    by_folder[d['folder']].append(d)

def pick_representative(entries):
    target = min(entries, key=lambda e: abs(e['weight'] - 400))
    return target

def subset_font(path, chars):
    t = TTFont(path)
    cmap = t.getBestCmap()
    want = {ord(c) for c in chars if ord(c) in cmap}
    if not want:
        return None
    opt = Options()
    opt.flavor = 'woff2'
    opt.layout_features = ['*']
    opt.name_IDs = ['*']
    opt.notdef_outline = True
    opt.hinting = False
    opt.desubroutinize = True
    s = Subsetter(options=opt)
    s.populate(unicodes=sorted(want))
    s.subset(t)
    buf = io.BytesIO()
    t.flavor = 'woff2'
    t.save(buf)
    return buf.getvalue()

html = io.open(SRC, encoding='utf-8').read()

# 태그 버튼 HTML 삽입
tag_btns = '\n'.join(
    f'<button class="filter-btn" data-filter="{t}">{TAG_LABELS[t]}</button>'
    for t in ALL_TAGS
)
html = html.replace('<!--@TAG_BUTTONS@-->', tag_btns)

fontfaces = []
cards_html = []
total_kb = 0
ok_count = 0
err_count = 0

folders = sorted(by_folder.keys(), key=lambda f: int(re.match(r'^(\d+)', f).group(1)) if re.match(r'^(\d+)', f) else 9999)

for i, folder in enumerate(folders):
    entries = by_folder[folder]
    entry = pick_representative(entries)
    folder_label = re.sub(r'^\d+_', '', folder)
    family = entry['family']
    ofl = entry['ofl']
    weight = entry['weight']
    path = entry['path']
    css_family = f'AF_{i}'
    tags = TAGS.get(folder, [])
    tags_attr = ' '.join(tags)
    tag_badges = ''.join(
        f'<span class="badge badge-tag" data-tag="{t}">{TAG_LABELS[t]}</span>'
        for t in tags
    )

    try:
        font_bytes = subset_font(path, SAMPLE_CHARS)
        if not font_bytes:
            raise ValueError('서브셋 결과 없음')
        total_kb += len(font_bytes)
        b64 = base64.b64encode(font_bytes).decode('ascii')
        fontfaces.append(
            f"@font-face{{font-family:'{css_family}';font-weight:{weight};"
            f"font-style:normal;font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
        sample_style = f"font-family:'{css_family}',sans-serif;font-weight:{weight}"
        ofl_badge = '<span class="badge badge-ofl">OFL</span>' if ofl else ''
        cards_html.append(
            f'<div class="card" data-type="all" data-name="{family}" data-folder="{folder_label}" data-tags="{tags_attr}">'
            f'<div class="sample" style="{sample_style}">{SAMPLE_KO[:8]}</div>'
            f'<div class="card-info">'
            f'<div class="font-name">{family}</div>'
            f'<div class="font-sub">{folder_label}</div>'
            f'<div class="badges">{ofl_badge}{tag_badges}</div>'
            f'</div></div>'
        )
        ok_count += 1
        print(f'  [OK] {family:35} {len(font_bytes)//1024}KB  {tags}')
    except Exception as e:
        err_count += 1
        print(f'  [ERR] {family}: {e}')
        cards_html.append(
            f'<div class="card" data-type="all" data-name="{family}" data-folder="{folder_label}" data-tags="{tags_attr}" style="opacity:.4">'
            f'<div class="sample" style="color:var(--faint)">{folder_label}</div>'
            f'<div class="card-info">'
            f'<div class="font-name">{family}</div>'
            f'<div class="font-sub">{folder_label}</div>'
            f'<div class="badges">{tag_badges}</div>'
            f'</div></div>'
        )

print(f'\n합계: {total_kb//1024}KB / 성공 {ok_count}종 · 실패 {err_count}종')

out = html.replace('/*@FONTFACES@*/', '\n'.join(fontfaces))
out = out.replace('<!--@CARDS@-->', '\n'.join(cards_html))
io.open(OUT, 'w', encoding='utf-8').write(out)
print(f'→ {OUT} ({len(out.encode("utf-8"))//1024}KB)')
