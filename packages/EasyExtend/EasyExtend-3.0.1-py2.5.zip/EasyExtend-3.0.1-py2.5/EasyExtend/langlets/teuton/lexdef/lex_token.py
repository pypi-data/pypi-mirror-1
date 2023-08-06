# -*- coding: iso-8859-1 -*-
# You might create here a new LexerToken object and set or overwrite
# properties of the BaseLexerToken object defined in lexertoken.py

LANGLET_OFFSET = 38912

from EasyExtend.lexertoken import NewLexerToken

LexerToken = NewLexerToken(LANGLET_OFFSET)
LexerToken.abstract.A_UMLAUT = LANGLET_OFFSET+20
LexerToken.litset.LS_A_UMLAUT = set(['\xe4', '\xf6', '\xfc', '\xc4', '\xd6', '\xdc', '\xdf', '\x84', '\x8e', '\x94', '\x99', '\x81', '\x9a', '\xe1'])
LexerToken.abstract.A_ue = LANGLET_OFFSET+21
LexerToken.litset.LS_A_ue = set(['\x81', '\xfc'])
