# -*- coding: utf-8 -*-
"""
Hepburn Romanization using Japanese passport rules
"""
from textutil_ja import kana

__all__ = ['romanize', 'reverse']

_MAP = (
    "あ", "A",
    "い", "I",
    "う", "U",
    "え", "E",
    "お", "O",
    "か", "KA",
    "き", "KI",
    "く", "KU",
    "け", "KE",
    "こ", "KO",
    "さ", "SA",
    "し", "SHI",
    "す", "SU",
    "せ", "SE",
    "そ", "SO",
    "た", "TA",
    "ち", "CHI",
    "つ", "TSU",
    "て", "TE",
    "と", "TO",
    "な", "NA",
    "に", "NI",
    "ぬ", "NU",
    "ね", "NE",
    "の", "NO",
    "は", "HA",
    "ひ", "HI",
    "ふ", "FU",
    "へ", "HE",
    "ほ", "HO",
    "ま", "MA",
    "み", "MI",
    "む", "MU",
    "め", "ME",
    "も", "MO",
    "や", "YA",
    "ゆ", "YU",
    "よ", "YO",
    "ら", "RA",
    "り", "RI",
    "る", "RU",
    "れ", "RE",
    "ろ", "RO",
    "わ", "WA",
    "ゐ", "I",
    "ゑ", "E",
    "を", "O",
    "ん", "N",
    "ぁ", "A",
    "ぃ", "I",
    "ぅ", "U",
    "ぇ", "E",
    "ぉ", "O",
    "が", "GA",
    "ぎ", "GI",
    "ぐ", "GU",
    "げ", "GE",
    "ご", "GO",
    "ざ", "ZA",
    "じ", "JI",
    "ず", "ZU",
    "ぜ", "ZE",
    "ぞ", "ZO",
    "だ", "DA",
    "ぢ", "JI",
    "づ", "ZU",
    "で", "DE",
    "ど", "DO",
    "ば", "BA",
    "び", "BI",
    "ぶ", "BU",
    "べ", "BE",
    "ぼ", "BO",
    "ぱ", "PA",
    "ぴ", "PI",
    "ぷ", "PU",
    "ぺ", "PE",
    "ぽ", "PO",
    "きゃ", "KYA",
    "きゅ", "KYU",
    "きょ", "KYO",
    "しゃ", "SHA",
    "しゅ", "SHU",
    "しょ", "SHO",
    "ちゃ", "CHA",
    "ちゅ", "CHU",
    "ちょ", "CHO",
    "ちぇ", "CHE",
    "にゃ", "NYA",
    "にゅ", "NYU",
    "にょ", "NYO",
    "ひゃ", "HYA",
    "ひゅ", "HYU",
    "ひょ", "HYO",
    "みゃ", "MYA",
    "みゅ", "MYU",
    "みょ", "MYO",
    "りゃ", "RYA",
    "りゅ", "RYU",
    "りょ", "RYO",
    "ぎゃ", "GYA",
    "ぎゅ", "GYU",
    "ぎょ", "GYO",
    "じゃ", "JA",
    "じゅ", "JU",
    "じょ", "JO",
    "びゃ", "BYA",
    "びゅ", "BYU",
    "びょ", "BYO",
    "ぴゃ", "PYA",
    "ぴゅ", "PYU",
    "ぴょ", "PYO",
)
MAP = dict((unicode(k, 'utf8'), v) for k, v in zip(_MAP[0::2], _MAP[1::2]))

def _hepburn_for(value, index):
    char = None
    hepburn = None
    if index + 1 < len(value):
        char = value[index:index+2]
        hepburn = MAP.get(char)

    if hepburn is None and index < len(value):
        char = value[index]
        hepburn = MAP.get(char)

    return char, hepburn

def romanize(value, long_vowels_h=False):
    # convert katakana to hiragana
    value = kana.to_hiragana(value)

    output = []
    last_hepburn = None
    last_char = None

    value_length = len(value)
    index = 0

    while index < value_length:
        char, hepburn = _hepburn_for(value, index)

        if char == u"ん":
            ## 1. 撥音 ヘボン式ではB/M/Pの前にNの代わりにMをおく
            next_char, next_hepburn = _hepburn_for(value, index + 1)
            if next_hepburn is not None and next_hepburn[0] in ('BMP'):
                hepburn = 'M'
            else:
                hepburn = 'N'

        elif char == u"っ":
            ## 2. 促音 子音を重ねて示す
            next_char, next_hepburn = _hepburn_for(value, index + 1)

            # チ(CHI), チャ(CHA), チュ(CHU), チョ(CHO)音に限り, その前にTを加える
            if next_hepburn is not None and next_hepburn.startswith('CH'):
                hepburn = 'T'
            else:
                hepburn = next_hepburn[0]

        elif char == u"ー":
            ## 3. 長音 ヘボン式では長音を表記しない
            hepburn = ""

        #if 0:
        #    ## Japanese Passport table doesn't have entries for ぁ-ぉ
        #    pass

        if hepburn is not None:
            if last_hepburn is not None:
                h_test = last_hepburn + hepburn
                # check last two letters
                h_test = h_test[-2:]

                if h_test in ('AA', 'II', 'UU', 'EE'):
                    # 3. 長音 ヘボン式では長音を表記しない
                    hepburn = ''

                if h_test in ('OO', 'OU'):
                    hepburn = long_vowels_h and 'H' or ''

            output.append(hepburn)

        else:
            # Can't find hepburn replacement for the given char
            pass

        last_hepburn = hepburn
        last_char = char
        index += len(char)

    return ''.join(output)

def reverse(value):
    raise NotImplementedError()
