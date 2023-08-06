# -*- coding: utf-8 -*-
import re
from textutil_ja import kana

__all__ = ['romanize', 'reverse']

def romanize(value):
    value = kana.to_katakana(value)

    def step1(matcher):
        return KANA_TO_ROMAJI_MAP[matcher.group(1)]
    value = RE_KANA_TWO.sub(step1, value)
    value = RE_KANA_ONE.sub(step1, value)

    ## ッta -> tta
    def step2(matcher):
        char = matcher.group(1)
        return u'%s%s' % (char, char)
    value = RE_CONSONANTS.sub(step2, value)

    ## oー -> oo
    def step3(matcher):
        vowel = matcher.group(1)
        return u'%s%s' % (vowel, vowel)
    value = RE_VOWELS.sub(step3, value)

    return value

def reverse(value):
    value = value.lower()

    ## step 1; tta -> ッta
    def step1(matcher):
        return u"ッ%s" % matcher.group(1)
    value = RE_CONSONANTS_REVERSE.sub(step1, value)

    ##
    def step2(matcher):
        return ROMAJI_TO_KANA_MAP[matcher.group(1)]
    value = RE_ROMAJI_THREE.sub(step2, value)
    value = RE_ROMAJI_TWO.sub(step2, value)
    value = RE_ROMAJI_ONE.sub(step2, value)

    ## step 3
    def step3(matcher):
        return u'%sン' % matcher.group(1)
    value = RE_N.sub(step3, value)

    return kana.to_hiragana(value)

_KANA_TO_ROMAJI_MAP = u"""
  ア   a       イ   i       ウ   u       エ   e       オ   o
  ァ   xa      ィ   xi      ゥ   xu      ェ   xe      ォ   xo
  カ   ka      キ   ki      ク   ku      ケ   ke      コ   ko
  ガ   ga      ギ   gi      グ   gu      ゲ   ge      ゴ   go
  キャ kya                  キュ kyu                  キョ kyo
  サ   sa      シ   shi     ス   su      セ   se      ソ   so
  ザ   za      ジ   ji      ズ   zu      ゼ   ze      ゾ   zo
  シャ sha                  シュ shu                  ショ sho
  ジャ ja                   ジュ ju                   ジョ jo
  タ   ta      チ   chi     ツ   tsu     テ   te      ト   to
               ティ ti      トゥ tu
  ダ   da      ディ di      ドゥ du      デ   de      ド   do
               ヂ   dhi     ヅ   dhu
  チャ cha                  チュ chu     チェ che     チョ cho
  ヂャ dha                  ヂュ dhu     ヂェ dhe     ヂョ dho
  ナ   na      ニ   ni      ヌ   nu      ネ   ne      ノ   no
  ハ   ha      ヒ   hi      フ   fu      ヘ   he      ホ   ho
  ヒャ hya                  ヒュ hyu                  ヒョ hyo
  バ   ba      ビ   bi      ブ   bu      ベ   be      ボ   bo
  ビャ bya                  ビュ byu                  ビョ byo
  パ   pa      ピ   pi      プ   pu      ペ   pe      ポ   po
  ピャ pya                  ピュ pyu                  ピョ pyo
  ファ fa      フィ fi                   フェ fe      フォ fo
  マ   ma      ミ   mi      ム   mu      メ   me      モ   mo
  ヤ   ya                   ユ   yu      イェ ye      ヨ   yo
  ャ   xya                  ュ   xyu                  ョ   xyo
  ラ   ra      リ   ri      ル   ru      レ   re      ロ   ro
  ワ   wa      ヰ   wi                   ヱ   we      ヲ   wo
  ウァ wa      ウィ wi                   ウェ we      ウォ wo
  ヴァ va      ヴィ vi      ヴ   vu      ヴェ ve      ヴォ vo
  ン   n
""".split()

_ROMAJI_TO_KANA_MAP = u"""  a    ア      i    イ      u    ウ      e    エ      o    オ
  xa   ァ      xi   ィ      xu   ゥ      xe   ェ      xo   ォ
  ka   カ      ki   キ      ku   ク      ke   ケ      ko   コ
  ga   ガ      gi   ギ      gu   グ      ge   ゲ      go   ゴ
  kya  キャ                 kyu キュ                  kyo  キョ
  sa   サ      shi  シ      su   ス      se   セ      so   ソ
               si   シ
  za   ザ      ji   ジ      zu   ズ      ze   ゼ      zo   ゾ
               zi   ジ
  sha  シャ                 shu  シュ                 sho  ショ
  sya  シャ                 syu  シュ                 syo  ショ
  ta   タ      chi  チ      tsu  ツ      te   テ      to   ト
                            xtu  ッ
               ti   ティ    tu   トゥ
  da   ダ      di   ディ    du   ドゥ    de   デ      do   ド
               dhi  ヂ      dhu  ヅ
  cha  チャ                 chu  チュ    che  チェ    cho  チョ
  tya  チャ                 tyu  チュ    tye  チェ    tyo  チョ
  dha  ヂャ                 dhu  ヂュ    dhe  ヂェ    dho  ヂョ
  dya  ヂャ                 tyu  ヂュ    tye  ヂェ    tyo  ヂョ
  na   ナ      ni   ニ      nu   ヌ      ne   ネ      no   ノ
  ha   ハ      hi   ヒ      fu   フ      he   ヘ      ho   ホ
                            hu   フ
  hya  ヒャ                 hyu  ヒュ                 hyo  ヒョ
  ba   バ      bi   ビ      bu   ブ      be   ベ      bo   ボ
  bya  ビャ                 byu  ビュ                 byo  ビョ
  pa   パ      pi   ピ      pu   プ      pe   ペ      po   ポ
  pya  ピャ                 pyu  ピュ                 pyo  ピョ
  fa   ファ    fi   フィ                 fe   フェ    fo   フォ
  ma   マ      mi   ミ      mu   ム      me   メ      mo   モ
  ya   ヤ                   yu   ユ      ye   イェ    yo   ヨ
  xya  ャ                   xyu  ュ                   xyo  ョ
  ra   ラ      ri   リ      ru   ル      re   レ      ro   ロ
  la   ラ      li   リ      lu   ル      le   レ      lo   ロ
  wa   ワ                                             wo   ヲ
               wi   ウィ                 we   ウェ
  va   ヴァ    vi   ヴィ    vu   ヴ      ve   ヴェ    vo   ヴォ
""".split()

KANA_TO_ROMAJI_MAP = dict((k, v.upper()) for k, v in zip(_KANA_TO_ROMAJI_MAP[0::2], _KANA_TO_ROMAJI_MAP[1::2]))
ROMAJI_TO_KANA_MAP = dict((k, v.upper()) for k, v in zip(_ROMAJI_TO_KANA_MAP[0::2], _ROMAJI_TO_KANA_MAP[1::2]))

RE_KANA_TWO = re.compile(u'(%s)' % u'|'.join(x for x in KANA_TO_ROMAJI_MAP.keys() if len(x) == 2))
RE_KANA_ONE = re.compile(u'(%s)' % u'|'.join(x for x in KANA_TO_ROMAJI_MAP.keys() if len(x) == 1))

RE_ROMAJI_THREE = re.compile(u'(%s)' % u'|'.join(x for x in ROMAJI_TO_KANA_MAP.keys() if len(x) == 3))
RE_ROMAJI_TWO = re.compile(u'(%s)' % u'|'.join(x for x in ROMAJI_TO_KANA_MAP.keys() if len(x) == 2))
RE_ROMAJI_ONE = re.compile(u'(%s)' % u'|'.join(x for x in ROMAJI_TO_KANA_MAP.keys() if len(x) == 1))

RE_VOWELS = re.compile(u'([AIUEO])ー')

# note the absense of n and m
RE_CONSONANTS = re.compile(u"ッ([BCDFGHJKLPQRSTVWXYZ])")
RE_CONSONANTS_REVERSE = re.compile(r"([BCDFGHJKLPQRSTVWXYZ])\1", re.I)

RE_N = re.compile(u'([ァ-ン])[mn]')
