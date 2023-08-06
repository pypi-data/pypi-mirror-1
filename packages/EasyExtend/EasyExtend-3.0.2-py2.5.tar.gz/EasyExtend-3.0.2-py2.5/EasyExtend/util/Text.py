ESCAPE     = -1

class NonAlphabetCharacter(Exception):pass

class UnknownEscapeSequence(Exception):pass

class Alphabet:
    limit  = '\xFF\xFF'
    table  = {}
    escape = None

    def chr(self,hxchr):
        '''
        conversion: hxchr -> char
                    hxchr has the form '\\x$$' where $ is a placeholder of a hexadecimal digit.
        example: char('\x00') -> '\x00'   ( ASCII )
                 char('\x00') -> '@'      ( GSM7Bit )
        '''
        if hxchr == self.escape:
            return ESCAPE
        if hxchr>self.limit:
            if hxchr[0] != self.escape:
                msg = "Character with ord = %s found. Alphabet characters have to be in range 0..%s"%(ord(hxchr[0]),ord(self.limit))
                raise NonAlphabetCharacter,msg
        try:
            return self.table[hxchr]
        except KeyError:
            return hxchr

class ASCII(Alphabet):
    limit  = '\xFF'

tGSM7Bit = {}
tGSM7Bit['\x00'] = '@'
tGSM7Bit['\x02'] = '$'
tGSM7Bit['\x11'] = '_'
tGSM7Bit['\x1B'] = ' '
tGSM7Bit['\x1b\x24'] = '^'
tGSM7Bit['\x1b\x28'] = '{'
tGSM7Bit['\x1b\x29'] = '}'
tGSM7Bit['\x1b\x40'] = '|'
tGSM7Bit['\x1b\x2F'] = '\\'
tGSM7Bit['\x1b\x3C'] = '['
tGSM7Bit['\x1b\x3E'] = ']'
tGSM7Bit['\x1b\x3D'] = '~'
tGSM7Bit['\x1b\x65'] = '\x80'


class GSM7Bit(Alphabet):
    limit  = '\x7F'
    escape = '\x1b'
    table  = tGSM7Bit



class Text(str):
    defaultAlphabet = ASCII()    # ASCII as default
    def __new__(cls,hxcr,alphabet = None):
        assert isinstance(hxcr,str)
        if not alphabet:
            alphabet = cls.defaultAlphabet
        chars = [chr(int(x+y,16)) for (x,y) in zip(hxcr[::2],hxcr[1::2])]
        translation = []
        ESC_DELAY = False
        _c = ''
        for c in chars:
            if ESC_DELAY:
                _c = alphabet.chr(alphabet.escape+c)
                if alphabet.escape+c == _c:
                    raise UnknownEscapeSequence,alphabet.escape+c
                ESC_DELAY = False
            else:
                _c = alphabet.chr(c)
                if _c == ESCAPE:
                    ESC_DELAY = True
                    continue
            translation.append(_c)
        return str(''.join(translation))


