# -*- coding: utf-8 -*-
import unicodedata

__all__ = ['to_katakana', 'to_hiragana', 'to_han', 'to_zen', 'get_kana_row']

def to_katakana(value):
    if not isinstance(value, unicode):
        value = unicode(value)
    return value.translate(HIRAGANA_TO_KATAKANA)

def to_hiragana(value):
    if not isinstance(value, unicode):
        value = unicode(value)

    for kata, hira in KATAKANA_TO_HIRAGANA_EXCEPTIONS:
        value = value.replace(kata, hira)

    return value.translate(KATAKANA_TO_HIRAGANA)

def to_zen(value):
    """
    Convert hankaku-katakana to zenkaku katakana
    """
    if not isinstance(value, unicode):
        value = unicode(value)
    return unicodedata.normalize('NFKC', value)

def to_han(value):
    """
    Convert zenkaku-katakana to hankaku katakana
    """
    if not isinstance(value, unicode):
        value = unicode(value)
    return value.translate(ZEN_TO_HAN_TABLE)

def _get_kana_row():
    _KANA_LIST = (
        (u"あ", u"ァアィイゥウェエォオヴ"),
        (u"か", u"カガキギクグケゲコゴヵヶ"),
        (u"さ", u"サザシジスズセゼソゾ"),
        (u"た", u"タダチヂッツヅテデトド"),
        (u"な", u"ナニヌネノ"),
        (u"は", u"ハバパヒビピフブプヘベペホボポ"),
        (u"ま", u"マミムメモ"),
        (u"や", u"ャヤュユョヨ"),
        (u"ら", u"ラリルレロ"),
        (u"わ", u"ヮワヰヱヲン"),
    )

    table = {}
    for v, chars in _KANA_LIST:
        for char in chars:
            table[char] = v

    def get_kana_row(value):
        if not isinstance(value, unicode):
            value = unicode(value)
        char = to_katakana(value[0])
        return table.get(char)
    return get_kana_row
get_kana_row = _get_kana_row()

HIRAGANA_TO_KATAKANA = dict((k, v) for k, v in zip(range(ord(u"ぁ"), ord(u"ん")+1),
                                                   range(ord(u"ァ"), ord(u"ン")+1),
                                                   ))
KATAKANA_TO_HIRAGANA = dict((v, k) for k, v in HIRAGANA_TO_KATAKANA.items())

# special rules
KATAKANA_TO_HIRAGANA_EXCEPTIONS = [
    (u"ヴァ", u"ば"),
    (u"ヴィ", u"び"),
    (u"ヴェ", u"べ"),
    (u"ヴォ", u"ぼ"),
    (u"ヴ",   u"ブ"),
]

KATAKANA_LIST = (
    (u'ァ', u'ｧ'),
    (u'ア', u'ｱ'),
    (u'ィ', u'ｨ'),
    (u'イ', u'ｲ'),
    (u'ゥ', u'ｩ'),
    (u'ウ', u'ｳ'),
    (u'ェ', u'ｪ'),
    (u'エ', u'ｴ'),
    (u'ォ', u'ｫ'),
    (u'オ', u'ｵ'),
    (u'カ', u'ｶ'),
    (u'ガ', u'ｶﾞ'),
    (u'キ', u'ｷ'),
    (u'ギ', u'ｷﾞ'),
    (u'ク', u'ｸ'),
    (u'グ', u'ｸﾞ'),
    (u'ケ', u'ｹ'),
    (u'ゲ', u'ｹﾞ'),
    (u'コ', u'ｺ'),
    (u'ゴ', u'ｺﾞ'),
    (u'サ', u'ｻ'),
    (u'ザ', u'ｻﾞ'),
    (u'シ', u'ｼ'),
    (u'ジ', u'ｼﾞ'),
    (u'ス', u'ｽ'),
    (u'ズ', u'ｽﾞ'),
    (u'セ', u'ｾ'),
    (u'ゼ', u'ｾﾞ'),
    (u'ソ', u'ｿ'),
    (u'ゾ', u'ｿﾞ'),
    (u'タ', u'ﾀ'),
    (u'ダ', u'ﾀﾞ'),
    (u'チ', u'ﾁ'),
    (u'ヂ', u'ﾁﾞ'),
    (u'ッ', u'ｯ'),
    (u'ツ', u'ﾂ'),
    (u'ヅ', u'ﾂﾞ'),
    (u'テ', u'ﾃ'),
    (u'デ', u'ﾃﾞ'),
    (u'ト', u'ﾄ'),
    (u'ド', u'ﾄﾞ'),
    (u'ナ', u'ﾅ'),
    (u'ニ', u'ﾆ'),
    (u'ヌ', u'ﾇ'),
    (u'ネ', u'ﾈ'),
    (u'ノ', u'ﾉ'),
    (u'ハ', u'ﾊ'),
    (u'バ', u'ﾊﾞ'),
    (u'パ', u'ﾊﾟ'),
    (u'ヒ', u'ﾋ'),
    (u'ビ', u'ﾋﾞ'),
    (u'ピ', u'ﾋﾟ'),
    (u'フ', u'ﾌ'),
    (u'ブ', u'ﾌﾞ'),
    (u'プ', u'ﾌﾟ'),
    (u'ヘ', u'ﾍ'),
    (u'ベ', u'ﾍﾞ'),
    (u'ペ', u'ﾍﾟ'),
    (u'ホ', u'ﾎ'),
    (u'ボ', u'ﾎﾞ'),
    (u'ポ', u'ﾎﾟ'),
    (u'マ', u'ﾏ'),
    (u'ミ', u'ﾐ'),
    (u'ム', u'ﾑ'),
    (u'メ', u'ﾒ'),
    (u'モ', u'ﾓ'),
    (u'ャ', u'ｬ'),
    (u'ヤ', u'ﾔ'),
    (u'ュ', u'ｭ'),
    (u'ユ', u'ﾕ'),
    (u'ョ', u'ｮ'),
    (u'ヨ', u'ﾖ'),
    (u'ラ', u'ﾗ'),
    (u'リ', u'ﾘ'),
    (u'ル', u'ﾙ'),
    (u'レ', u'ﾚ'),
    (u'ロ', u'ﾛ'),
    (u'ヮ', u'ﾜ'),
    (u'ワ', u'ﾜ'),
    (u'ヲ', u'ｦ'),
    (u'ン', u'ﾝ'),
    (u'ー', u'ｰ'),
    (u'、', u'､'),
    (u'。', u'｡'),
    (u'・', u'･'),
)

ZEN_TO_HAN_TABLE = dict((ord(z), h) for z, h in KATAKANA_LIST)
HAN_TO_ZEN_TABLE = dict((h, z) for z, h in KATAKANA_LIST)

