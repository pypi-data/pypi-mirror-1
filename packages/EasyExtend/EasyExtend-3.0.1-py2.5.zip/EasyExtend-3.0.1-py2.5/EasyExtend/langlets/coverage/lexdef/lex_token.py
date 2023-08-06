# You might create here a new LexerToken object and set or overwrite
# properties of the BaseLexerToken object defined in lexertoken.py

LANGLET_OFFSET = 3072

from EasyExtend.lexertoken import NewLexerToken

LexerToken = NewLexerToken(LANGLET_OFFSET)
