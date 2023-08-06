import re
_OPTION_DIRECTIVE_RE = re.compile(r'#\s*doctest:\s*([^\n\'"]*)$',re.MULTILINE)

def f():
    """
    name is the string's name, and lineno is the line number
    """

# line in a string.
_INDENT_RE = re.compile('^([ ]*)(?=\S)', re.MULTILINE)




