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

data = json.load(open(CATALOG, encoding='utf-8'))

by_folder = defaultdict(list)
for d in data:
    by_folder[d['folder']].append(d)

def pick_representative(entries):
    """폴더에서 대표 폰트 1개 선택 (400 우선, 없으면 weight 차이 최소)"""
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
        badge = '<span class="badge badge-ofl">OFL</span>' if ofl else ''
        cards_html.append(
            f'<div class="card" data-type="all" data-name="{family}" data-folder="{folder_label}">'
            f'<div class="sample" style="{sample_style}">{SAMPLE_KO[:8]}</div>'
            f'<div class="card-info">'
            f'<div class="font-name">{family}</div>'
            f'<div class="font-sub">{folder_label}</div>'
            f'<div class="badges">{badge}</div>'
            f'</div></div>'
        )
        ok_count += 1
        print(f'  [OK] {family:35} {len(font_bytes)//1024}KB')
    except Exception as e:
        err_count += 1
        print(f'  [ERR] {family}: {e}')
        cards_html.append(
            f'<div class="card" data-type="all" data-name="{family}" data-folder="{folder_label}" style="opacity:.4">'
            f'<div class="sample" style="color:var(--faint)">{folder_label}</div>'
            f'<div class="card-info">'
            f'<div class="font-name">{family}</div>'
            f'<div class="font-sub">{folder_label}</div>'
            f'</div></div>'
        )

print(f'\n합계: {total_kb//1024}KB / 성공 {ok_count}종 · 실패 {err_count}종')

out = html.replace('/*@FONTFACES@*/', '\n'.join(fontfaces))
out = out.replace('<!--@CARDS@-->', '\n'.join(cards_html))
io.open(OUT, 'w', encoding='utf-8').write(out)
print(f'→ {OUT} ({len(out.encode("utf-8"))//1024}KB)')
