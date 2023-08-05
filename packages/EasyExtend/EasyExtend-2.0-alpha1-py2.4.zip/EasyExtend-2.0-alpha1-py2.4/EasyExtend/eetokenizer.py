"""
eetokenize merges the stdlibs tokenize.py module with the modules parser/StdTokenizer.py and
parser/TokenUtils.py
"""

import string, re
import eetokpattern
from eexcept import*


class StopTokenizing(Exception): pass

def printtoken(type, token, (srow, scol), (erow, ecol), line): # for testing
    print "%d,%d-%d,%d:\t%s\t%s" % \
        (srow, scol, erow, ecol, tok_name[type], repr(token))


class LineList:
    """Class LineList
    Implements a readline-style interface to a string.
    """
    def __init__ (self, inString):
        """LineList.__init__()
        """
        self.index = 0
        self.lineList = inString.splitlines()

    def __call__ (self):
        """LineList.__call__()
        """
        retVal = ''
        if self.index < len(self.lineList):
            retVal = self.lineList[self.index] + "\n"
            self.index += 1
        return retVal

class StdTokenizer(object):
    def __init__ (self, token, typ=None, use_comment=True):
        if hasattr(token, "gettoken"):
            self.__dict__.update(token.gettoken())
        else:
            self.__dict__.update(eetokpattern.gettoken(token))
        self.token = token
        if hasattr(self.token, "line_transformer") and typ not in ("grammar",):
            self.transformer = self.token.line_transformer
        else:
            self.transformer = lambda x: x  # identity
        self.use_comment = use_comment


    def tokenize_file (self, filename):
        self.filename = filename
        rl = open(filename).readline
        self.tokenGenerator = self.generate_tokens(rl)

    def tokenize_string (self, inString):
        self.filename = "<string>"
        self.tokenGenerator = self.generate_tokens(LineList(inString))

    def tokenize_input(self, readline):
        self.filename = "<input>"
        self.tokenGenerator = self.generate_tokens(readline)

    def next_token(self):
        retVal = None
        while True:
            (token_type, name, (lineno, startCol), endPos, crntLine) = self.tokenGenerator.next()
            # Drop tokens unique to tokenize
            if token_type in ( self.token.COMMENT, self.token.NL):
                if not self.use_comment:
                    continue
            elif token_type == self.token.NL:
                continue
            elif token_type == self.token.OP:
                token_type = self.token.TOKEN_MAP[name]
            elif token_type == self.token.FAT:
                token_type = self.token.FAT_TOKEN
            retVal = (token_type, name, lineno, (startCol, endPos[1]))
            return retVal

    def tokenized(self):
        tokens = []
        while True:
            try:
                tok = self.next_token()
                if tok is None:
                    return tokens
                tokens.append(tok)
            except StopIteration:
                return tokens


    def generate_tokens(self, readline):
        """
        The generate_tokens() generator requires one argment, readline, which
        must be a callable object which provides the same interface as the
        readline() method of built-in file objects. Each call to the function
        should return one line of input as a string.

        The generator produces 5-tuples with these members: the token type; the
        token string; a 2-tuple (srow, scol) of ints specifying the row and
        column where the token begins in the source; a 2-tuple (erow, ecol) of
        ints specifying the row and column where the token ends in the source;
        and the line on which the token was found. The line passed is the
        logical line; continuation lines are included.
        """
        tabsize = 8
        lnum = parenlev = continued = 0
        namechars, numchars = string.ascii_letters + '_', '0123456789'
        contstr, needcont = '', 0
        contline = None
        indents = [0]
        # accelarate access
        single_quoted = self.single_quoted
        triple_quoted = self.triple_quoted
        pseudoprog = self.pseudoprog
        endprogs   = self.endprogs
        linecomment= self.linecomment
        multiline  = self.multiline
        ERRORTOKEN = self.token.ERRORTOKEN
        STRING     = self.token.STRING
        NL         = self.token.NL
        COMMENT    = self.token.COMMENT
        INDENT     = self.token.INDENT
        DEDENT     = self.token.DEDENT
        NUMBER     = self.token.NUMBER
        NAME       = self.token.NAME
        endprogs   = self.endprogs
        INITIAL    = self.INITIAL
        FINAL      = self.FINAL
        pFunny     = self.pFunny
        FAT        = self.token.FAT
        OP         = self.token.OP
        NEWLINE    = self.token.NEWLINE
        ENDMARKER  = self.token.ENDMARKER
        TOKEN      = STRING

        while 1:                           # loop over lines in stream
            line = self.transformer(readline())
            lnum = lnum + 1
            pos, max = 0, len(line)

            if contstr:                    # continued string
                if not line:
                    raise TokenError, ("EOF in multi-line string", strstart)
                endmatch = endprog.match(line)
                if endmatch:
                    pos = end = endmatch.end(0)
                    yield (TOKEN, contstr + line[:end],
                               strstart, (lnum, end), contline + line)
                    contstr, needcont = '', 0
                    TOKEN    = STRING
                    contline = None
                elif needcont and line[-2:] != '\\\n' and line[-3:] != '\\\r\n':
                    yield (ERRORTOKEN, contstr + line,
                               strstart, (lnum, len(line)), contline)
                    contstr = ''
                    contline = None
                    continue
                else:
                    contstr = contstr + line
                    contline = contline + line
                    continue

            elif parenlev == 0 and not continued:  # new statement
                if not line: break
                column = 0
                while pos < max:                   # measure leading whitespace
                    if line[pos] == ' ': column = column + 1
                    elif line[pos] == '\t': column = (column/tabsize + 1)*tabsize
                    elif line[pos] == '\f': column = 0
                    else: break
                    pos = pos + 1
                if pos == max: break
                if line[pos] == linecomment:
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    yield (COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    yield (NL, line[nl_pos:],
                           (lnum, nl_pos), (lnum, len(line)), line)
                    continue
                elif line[pos] in '\r\n':
                    yield ((NL, COMMENT)[line[pos] == '#'], line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                    continue
                if column > indents[-1]:           # count indents or dedents
                    indents.append(column)
                    yield (INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
                while column < indents[-1]:
                    indents = indents[:-1]
                    yield (DEDENT, '', (lnum, pos), (lnum, pos), line)

            else:                                  # continued statement
                if not line:
                    raise TokenError, ("EOF in multi-line statement", (lnum, 0))
                continued = 0

            while pos < max:
                pseudomatch = pseudoprog.match(line, pos)
                if pseudomatch:                              # scan for tokens
                    start, end = pseudomatch.span(1)
                    spos, epos, pos = (lnum, start), (lnum, end), end
                    tok, initial = line[start:end], line[start]
                    if pseudomatch.groupdict().get("fat_token"):  # matches arbitrary user defined regexps as token
                        yield (FAT, tok, spos, epos, line)
                    elif initial in numchars or \
                       (initial == '.' and tok != '.'):      # ordinary number
                        yield (NUMBER, tok, spos, epos, line)
                    elif initial in '\r\n':
                        yield (parenlev > 0 and NL or NEWLINE,
                                   tok, spos, epos, line)
                    elif initial == linecomment[0] and tok[:len(linecomment)] == linecomment:
                        yield (COMMENT, tok, spos, epos, line)
                    elif tok in triple_quoted:
                        endprog = endprogs[tok]
                        endmatch = endprog.match(line, pos)
                        if endmatch:                           # all on one line
                            pos = endmatch.end(0)
                            tok = line[start:pos]
                            yield (STRING, tok, spos, (lnum, pos), line)
                        else:
                            strstart = (lnum, start)           # multiple lines
                            contstr = line[start:]
                            contline = line
                            break

                    elif tok in multiline:
                        endprog = multiline[tok]
                        endmatch = endprog.match(line, pos)
                        if endmatch:                           # all on one line
                            pos = endmatch.end(0)
                            tok = line[start:pos]
                            yield (COMMENT, tok, spos, (lnum, pos), line)
                        else:
                            strstart = (lnum, start)           # multiple lines
                            contstr = line[start:]
                            contline = line
                            TOKEN = COMMENT
                            break
                    elif initial in single_quoted or \
                        tok[:2] in single_quoted or \
                        tok[:3] in single_quoted:
                        if tok[-1] == '\n':                  # continued string
                            strstart = (lnum, start)
                            endprog = (endprogs[initial] or endprogs[tok[1]] or
                                       endprogs[tok[2]])
                            contstr, needcont = line[start:], 1
                            contline = line
                            break
                        else:                                  # ordinary string
                            yield (STRING, tok, spos, epos, line)
                    elif initial in namechars:                 # ordinary name
                        yield (NAME, tok, spos, epos, line)
                    elif initial == '\\' and self.token.NoContStr is False:    # continued stmt
                        yield (self.token.BACKSLASH, tok, spos, epos, line)
                        continued = 1
                    else:
                        if INITIAL.match(initial):
                            if len(tok)>1 and pFunny.match(tok):
                                pass
                            else:
                                parenlev = parenlev + 1
                        elif FINAL.match(initial):
                            if len(tok)>1 and pFunny.match(tok):
                                pass
                            else:
                                parenlev = parenlev - 1
                        yield (OP, tok, spos, epos, line)
                else:
                    yield (ERRORTOKEN, line[pos],
                               (lnum, pos), (lnum, pos+1), line)
                    pos = pos + 1

        for indent in indents[1:]:                 # pop remaining indent levels
            yield (DEDENT, '', (lnum, 0), (lnum, 0), '')
        yield (ENDMARKER, '', (lnum, 0), (lnum, 0), '')


