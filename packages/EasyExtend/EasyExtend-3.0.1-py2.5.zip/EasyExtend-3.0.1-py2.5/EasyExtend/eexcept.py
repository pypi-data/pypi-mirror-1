# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

#
#  Collection of exceptions used by EasyExtend
#
#  This module doesn't have to be imported directly. Instead
#  EasyExtend passes the exception classes into __builtin__.
#

class ParserError(Exception):
    def __init__(self, value, **kwd):
        self.value = value
        self.__dict__.update(**kwd)

    def __str__(self):
        return self.value

class LexerError(Exception):
    """
    Exception class for lexer errors.
    """
    def __init__(self, value, **kwd):
        self.value = value
        self.__dict__.update(**kwd)

    def __str__(self):
        return self.value

class NodeCycleError(Exception):
    """
    A node cycle N < ...<A<N might cause problems. This exception might help
    them to trace with appropriate cycle detectors.
    """


class TranslationError (Exception):
    """
    Exception class for translation failures.
    """

class TokenError(Exception):
    '''
    Exception class for tokenization failures.
    '''

class NonSelectableError(Exception):
    '''
    Exception class for nid selection failures in nfaparsing.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return self.value
        else:
            return str(self.value)

class InvalidNodeError(Exception):
    '''
    Exception class for CST checking failures.
    '''

