#!/usr/bin/env python3
"""Build compact readings.js from Unihan JSON files."""
import json, os

# Romaji to Hiragana conversion
R2H = {
    "A":"あ","I":"い","U":"う","E":"え","O":"お",
    "KA":"か","KI":"き","KU":"く","KE":"け","KO":"こ",
    "SA":"さ","SI":"し","SHI":"し","SU":"す","SE":"せ","SO":"そ",
    "TA":"た","TI":"ち","CHI":"ち","TU":"つ","TSU":"つ","TE":"て","TO":"と",
    "NA":"な","NI":"に","NU":"ぬ","NE":"ね","NO":"の",
    "HA":"は","HI":"ひ","HU":"ふ","FU":"ふ","HE":"へ","HO":"ほ",
    "MA":"ま","MI":"み","MU":"む","ME":"め","MO":"も",
    "YA":"や","YU":"ゆ","YO":"よ",
    "RA":"ら","RI":"り","RU":"る","RE":"れ","RO":"ろ",
    "WA":"わ","WI":"ゐ","WE":"ゑ","WO":"を",
    "GA":"が","GI":"ぎ","GU":"ぐ","GE":"げ","GO":"ご",
    "ZA":"ざ","ZI":"じ","JI":"じ","ZU":"ず","ZE":"ぜ","ZO":"ぞ",
    "DA":"だ","DI":"ぢ","DU":"づ","DE":"で","DO":"ど",
    "BA":"ば","BI":"び","BU":"ぶ","BE":"べ","BO":"ぼ",
    "PA":"ぱ","PI":"ぴ","PU":"ぷ","PE":"ぺ","PO":"ぽ",
    "KYA":"きゃ","KYU":"きゅ","KYO":"きょ",
    "SHA":"しゃ","SHU":"しゅ","SHO":"しょ",
    "CHA":"ちゃ","CHU":"ちゅ","CHO":"ちょ",
    "NYA":"にゃ","NYU":"にゅ","NYO":"にょ",
    "HYA":"ひゃ","HYU":"ひゅ","HYO":"ひょ",
    "MYA":"みゃ","MYU":"みゅ","MYO":"みょ",
    "RYA":"りゃ","RYU":"りゅ","RYO":"りょ",
    "GYA":"ぎゃ","GYU":"ぎゅ","GYO":"ぎょ",
    "JA":"じゃ","JU":"じゅ","JO":"じょ",
    "BYA":"びゃ","BYU":"びゅ","BYO":"びょ",
    "PYA":"ぴゃ","PYU":"ぴゅ","PYO":"ぴょ",
}

def romaji_to_hira(rom):
    rom = rom.upper().strip()
    if rom in R2H:
        return R2H[rom]
    result = ""
    i = 0
    while i < len(rom):
        matched = False
        for length in range(min(4, len(rom)-i), 0, -1):
            chunk = rom[i:i+length]
            if chunk in R2H:
                result += R2H[chunk]
                i += length
                matched = True
                break
        if not matched:
            if rom[i] == "N" and i+1 < len(rom) and rom[i+1] not in "AIUEOY":
                result += "ん"
                i += 1
            elif rom[i] == "N" and i+1 == len(rom):
                result += "ん"
                i += 1
            else:
                # Double consonant → っ
                if i+1 < len(rom) and rom[i] == rom[i+1] and rom[i] in "KSTPGZDBHFMR":
                    result += "っ"
                    i += 1
                else:
                    result += rom[i].lower()
                    i += 1
    return result

# 1. Japanese on'yomi: romaji → hiragana, take first reading
with open("kJapaneseOn.json", "r", encoding="utf-8") as f:
    jp_raw = json.load(f)
jp = {}
for ch, readings in jp_raw.items():
    if readings:
        r = readings[0] if isinstance(readings, list) else readings
        jp[ch] = romaji_to_hira(r)
print(f"JP: {len(jp)} entries")

# 2. Korean: extract hangul key
with open("kHangul.json", "r", encoding="utf-8") as f:
    kr_raw = json.load(f)
kr = {}
for ch, val in kr_raw.items():
    if isinstance(val, dict):
        hangul = list(val.keys())[0] if val else ""
        if hangul:
            kr[ch] = hangul
    elif isinstance(val, str):
        kr[ch] = val
print(f"KR: {len(kr)} entries")

# 3. Vietnamese: take first reading
with open("kVietnamese.json", "r", encoding="utf-8") as f:
    vi_raw = json.load(f)
vi = {}
for ch, readings in vi_raw.items():
    if readings:
        vi[ch] = readings[0] if isinstance(readings, list) else readings
print(f"VI: {len(vi)} entries")

# 4. Mandarin pinyin
with open("kMandarin.json", "r", encoding="utf-8") as f:
    py_raw = json.load(f)
py = {}
for ch, reading in py_raw.items():
    if reading:
        py[ch] = reading if isinstance(reading, str) else reading[0]
print(f"PY: {len(py)} entries")

# Write compact JS
out = "window.UNIHAN_READINGS={\n"
out += "jp:" + json.dumps(jp, ensure_ascii=False, separators=(",",":")) + ",\n"
out += "kr:" + json.dumps(kr, ensure_ascii=False, separators=(",",":")) + ",\n"
out += "vi:" + json.dumps(vi, ensure_ascii=False, separators=(",",":")) + ",\n"
out += "pinyin:" + json.dumps(py, ensure_ascii=False, separators=(",",":")) + "\n"
out += "};\n"

with open("readings.js", "w", encoding="utf-8") as f:
    f.write(out)

sz = os.path.getsize("readings.js")
print(f"readings.js: {sz} bytes ({sz/1024:.0f} KB)")

# Spot checks
test_chars = {"一": "jp/kr/pinyin", "人": "jp/kr/pinyin", "変": "jp", "平": "jp/pinyin", "假": "jp/pinyin", "名": "jp/pinyin"}
print("\nSpot checks:")
for ch in test_chars:
    print(f"  {ch}: jp={jp.get(ch,'?')} kr={kr.get(ch,'?')} vi={vi.get(ch,'?')} py={py.get(ch,'?')}")
