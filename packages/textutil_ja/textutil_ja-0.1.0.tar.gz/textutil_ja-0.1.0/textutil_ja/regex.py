# -*- coding: utf-8 -*-
import re

__all__ = ['hiragana', 'katakana']

hiragana = re.compile(u'([ぁ-ん][ぁ-んー]*)')
katakana = re.compile(u'([ァ-ンｧ-ﾝ][ァ-ンｧ-ﾝﾟﾞｰー]*)')
