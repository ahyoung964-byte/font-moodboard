# -*- coding: utf-8 -*-
"""~/fonts 전수 목록 → fonts_catalog.json
tier: embed(OFL 또는 배포처 허용 근거) / local(PC 에 설치돼 있을 때만 보임 — 바이트를 싣지 않는다)
같은 (family, subfamily) 는 OTF 를 우선하고 하나만 남긴다."""
import os, sys, json, re
from fontTools.ttLib import TTFont
sys.stdout.reconfigure(encoding='utf-8')
base = os.path.expanduser('~/fonts')

# 배포처가 수정·재배포/웹 임베딩을 명시적으로 허용한 폴더 (근거는 build_fonts.py ALLOW 와 같은 줄)
ALLOW_FOLDER = {
    '01_꾸불림체': '우아한형제들 — 자유롭게 수정·변경 허용',
    '22_배민주아체': '우아한형제들 — 자유롭게 수정·변경 허용', '23_배민도현체': '우아한형제들 — 자유롭게 수정·변경 허용', '24_배민연성체': '우아한형제들 — 자유롭게 수정·변경 허용',
    '12_온글잎박다현': '온글잎 — 상업 이용·웹 임베딩 코드 제공', '13_온글잎의연': '온글잎', '14_온글잎쑴': '온글잎', '15_온글잎콘콘': '온글잎', '03_의청수윤영체': '온글잎',
    '55_온글잎시우': '온글잎', '87_온글잎다경': '온글잎', '88_온글잎재선': '온글잎', '89_온글잎주빈': '온글잎',
    '100_카페24모야모야': '카페24 — SIL OFL 고지', '28_카페24당당해': '카페24', '29_카페24빛나는별': '카페24', '27_카페24써라운드': '카페24', '52_카페24슈퍼매직': '카페24',
    '35_마루부리': '네이버 마루부리 — SIL OFL 배포', '36_나눔스퀘어라운드': '네이버 나눔 — SIL OFL', '37_나눔손글씨붓': '네이버 나눔 — SIL OFL', '56_나눔펜': '네이버 나눔 — SIL OFL', '57_나눔바른펜': '네이버 나눔 — SIL OFL',
    '67_리디바탕': '리디 — SIL OFL 배포', '68_아리따부리': '아모레퍼시픽 아리따 — SIL OFL 배포',
    '125_나눔고딕': '네이버 나눔체 — 무료 배포 허용', '126_나눔명조': '네이버 나눔체 — 무료 배포 허용',
    '130_한겨레결체': '한겨레신문 — 무료 배포',
}

# platformID=1 인코딩 깨짐 등으로 family 이름이 올바르게 읽히지 않는 경우 수동 오버라이드
FAMILY_OVERRIDE = {
    '130_한겨레결체': '한겨레결체',
}

def weight_of(sub):
    s = sub.lower()
    for k, w in [('black', 900), ('heavy', 900), ('extrabold', 800), ('extra bold', 800), ('bold', 700), ('semibold', 600), ('demibold', 600), ('medium', 500),
                 ('regular', 400), ('normal', 400), ('light', 300), ('extralight', 200), ('thin', 100)]:
        if k in s: return w
    if s in ('b',): return 700
    if s in ('r',): return 400
    if s in ('l',): return 300
    if s in ('m',): return 500
    return 400

rows = {}
for root, _, files in os.walk(base):
    if '_tools' in root: continue
    for f in files:
        if not f.lower().endswith(('.ttf', '.otf')): continue
        p = os.path.join(root, f)
        folder = os.path.relpath(root, base).split(os.sep)[0]
        try:
            t = TTFont(p, lazy=True); n = t['name']
            fam = (n.getDebugName(16) or n.getDebugName(1) or '').strip()
            sub = (n.getDebugName(17) or n.getDebugName(2) or 'Regular').strip()
            lic = (n.getDebugName(13) or ''); url = (n.getDebugName(14) or '')
            cmap = t.getBestCmap() or {}
            han = sum(1 for c in cmap if 0xAC00 <= c <= 0xD7A3)
            L = lic.lower()
            ofl = ('sil' in L and 'open font' in L) or 'ofl' in L or 'scripts.sil.org' in url.lower()
        except Exception as e:
            print('ERR', p, e); continue
        fam_key = FAMILY_OVERRIDE.get(folder, re.sub(r'\s+(OTF|TTF)$', '', fam, flags=re.I))
        key = (fam_key, sub)
        tier = 'embed' if ofl or folder in ALLOW_FOLDER else 'local'
        rec = dict(folder=folder, family=fam_key, sub=sub, weight=weight_of(sub), han=han, ofl=ofl, tier=tier,
                   reason=('OFL(nameID13)' if ofl else ALLOW_FOLDER.get(folder, '')), path=p, kb=os.path.getsize(p) // 1024,
                   local_name=fam, ps=(n.getDebugName(6) or ''))
        if key in rows and rows[key]['path'].lower().endswith('.otf') and not p.lower().endswith('.otf'):
            continue
        rows[key] = rec
def folder_sort_key(r):
    m = re.match(r'\d+', r['folder'])
    return (int(m.group()) if m else 9999, r['family'], r['weight'])
out = sorted(rows.values(), key=folder_sort_key)
json.dump(out, open('fonts_catalog.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
emb = [r for r in out if r['tier'] == 'embed']; loc = [r for r in out if r['tier'] == 'local']
print('total', len(out), 'embed', len(emb), 'local', len(loc), 'embed families', len({r['family'] for r in emb}), 'local families', len({r['family'] for r in loc}))
for r in out:
    print(f"{r['tier']:5} {r['folder'][:18]:18} {r['family'][:28]:28} {r['sub'][:10]:10} w{r['weight']} 한{r['han']:5} {r['kb']:5}KB")
