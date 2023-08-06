'''
Module used to unparse a parse tree and recreate source. For files not being transformed
the Unparser shall unparse the cst into the exact shape of the parsed source ( however indentation
size may vary ). For modified csts or new cst fragments some autoformatting heuristics are applied [1].
Additional heuristics are necessary for combining exact reconstruction with autoformatting.

[1] These heuristics is subject to further refinements.

Usage ::

    >>> from cst2source import Unparser
    >>> unparse = Unparser()
    >>> import parser
    >>> tree = parser.suite("def f():\n  pass  # unparse this fragment").tolist()
    >>> print unparse(tree)

    def f():
        pass  # unparse this fragment

'''
__all__ = ["SourceCode", "Unparser"]
# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import re
import symbol as py_symbol
import token as py_token
from csttools import find_node, cstnode, add_info
import keyword


S_INDENT = " "*4
NOT_DEFINED = -1
ON_NEWLINE  = -1

class SourceCode:
    def __init__(self,source):
        self.source    = [s+"\n" for s in source.split("\n")]
        self.next_line = self.gen_source()

    def write(self,s):
        self.source.append(s)

    def gen_source(self):
        for s in self.source:
            yield s
        while 1:
            yield ""

    def readline(self):
        return self.next_line.next()

    def truncate(self, k):
        self.source[-1] = self.source[-1][:-k]


class NodeHandler(object):
    class State(object):
        def __init__(self, other = None):
            if other:
                self.__dict__.update(other.__dict__)
            else:
                self.indent_level = 0
                self.nospace      = True
                self.last_printed = ""
                self.last_node    = None
                self.line    = 0
                self.spaces  = 0
                self.last_pnid = 0

    def __init__(self, other = None, **kwd):
        self.output = SourceCode("")
        if other:
            self.__dict__.update(other.__dict__)
        else:
            self.state = self.State()
            self.__dict__.update(kwd)

    def handle_ENDMARKER(self, node):
        pass

    def has_addinfo(self, node):
        if isinstance(node, cstnode) and hasattr(node, "info"):
            return True
        else:
            return False

    def _indent(self, modify=0):
        self.output.write(S_INDENT * (self.state.indent_level+modify))

    def _get_spaces(self, node, last_node):
        def get_line_and_column(node):
            if self.has_addinfo(node):
                return node.info.lineno, node.info.column
            elif last_node and isinstance(node[-1], add_info):
                return node[-1].lineno, node[-1].column
            else:
                return None, None
        this_line, this_column = get_line_and_column(node)
        if this_line is None:
            return NOT_DEFINED, NOT_DEFINED
        last_line, last_column = get_line_and_column(last_node)
        if last_line is None:
            return NOT_DEFINED, NOT_DEFINED
        if this_line!=last_line:
            return ON_NEWLINE, this_column[0]
        else:
            return this_line, this_column[0] - last_column[1]

    def write_and_align(self, text, indent=False):
        assert isinstance(text, str), text
        if self.state.nospace:
            if text in ("def", "class"):
                self.output.write("\n")
                if indent:
                    self._indent()
            self.output.write(text)
            self.state.nospace = False
        else:
            last = self.state.last_printed
            if last == '.':
                self.output.write(text)
            elif last in ';:,':
                self.output.write(" "+text)
            elif last in ')]}':
                if text[0] in '([{.:}])':
                    self.output.write(text)
                else:
                    self.output.write(" "+text)
            elif last in '([{':
                if text[0] in '([{':
                    self.output.write(text)
                else:
                    self.output.write(" "+text)
            elif last[0].isalnum():
                if text in '.,:;':
                    self.output.write(text)
                elif text in '([{' and last not in keyword.kwlist:
                    self.output.write(text)
                else:
                    self.output.write(" "+text)
            else:
                self.output.write(" "+text)

__DEBUG__ = False

class NodeHandler_Exact(NodeHandler):
    def __init__(self, **kwd):
        super(NodeHandler_Exact, self).__init__(**kwd)
        self.nh_autoform = NodeHandler_AutoFormat(self)

    def handle(self, node, **kwargs):
        """Writes a node's equivalent source code to the output object.

        @raise TypeError: If the node's type is unknown.
        """
        pnid = node[0]%512
        name = find_node(node, self.token.NAME)  # keeping the next NAME token
        if name:
            if not self.has_addinfo(name):
                self.nh_autoform.state = self.state
                indent_level = self.state.indent_level
                #if self.state.last_pnid not in (py_token.NEWLINE, py_token.INDENT, py_token.DEDENT, 53, 54):
                #    self.output.write("")
                self.nh_autoform.handle(node)
                self.state = self.nh_autoform.state
                #self.state.indent_level = indent_level # restore indent level
                return

        if pnid>=256:
            for sub in node[1:]:
                if isinstance(sub, (list, tuple)):
                    self.handle(sub)
        else:
            self.state.line, self.spaces = self._get_spaces(node, self.state.last_node)
            if __DEBUG__:
                if self.has_addinfo(node):
                    print self.spaces, node, node.info
                else:
                    print self.spaces, node

            name = py_token.tok_name.get(pnid)
            if name and hasattr(self, "handle_"+name):
                method = getattr(self, "handle_"+name)
                method(node, **kwargs)
            else:
                self.handle_token_value(node)
            self.state.last_node = node
            self.state.last_pnid = pnid

    def handle_special(self, node):
        if self.has_addinfo(node):
            info = node.info
            if info.comment:
                self.state.last_node = node
                for n in info.comment:
                    self.handle(n)

    def handle_NL(self, node):
        self.output.write("\n")

    def handle_COMMENT(self, node):
        text = node[1]
        self.output.write(self.spaces*" "+text)

    def handle_BACKSLASH(self, node):
        return self.handle_COMMENT(node)

    def handle_NEWLINE(self, node):
        self.state.nospace = True
        self.output.write("\n")
        self.handle_special(node)
        self._indent()

    def handle_INDENT(self, node):
        self.output.write(S_INDENT)
        self.state.indent_level+=1
        self.state.last_node = node

    def handle_DEDENT(self, node):
        self.state.indent_level-=1
        self.output.truncate(len(S_INDENT))
        self.state.last_node = node

    def handle_token_value(self, node):
        text = node[1]
        if self.state.line == ON_NEWLINE and self.state.last_pnid == py_token.NEWLINE:
            self.output.write(text)
        elif self.spaces == -1 and self.state.last_node:
            if self.has_addinfo(node):
                self.output.write(text)
            else:
                self.write_and_align(text)
        else:
            self.output.write(self.spaces*" "+node[1])
        self.handle_special(node)
        self.state.last_node = node


class NodeHandler_AutoFormat(NodeHandler):

    def handle(self, node, *args, **kwargs):
        """Writes a node's equivalent source code to the output object.

        @raise TypeError: If the node's type is unknown.
        """
        n_id = node[0]
        pnid = n_id%512
        if pnid>=256:
            for sub in node[1:]:
                if isinstance(sub, list):
                    self.handle(sub)
        else:
            if __DEBUG__:
                print node
            name = py_token.tok_name.get(pnid)
            if name and hasattr(self, "handle_"+name):
                method = getattr(self, "handle_"+name)
                method(node, **kwargs)
            else:
                text = node[1]
                try:
                    self.write_and_align(text, indent = True)
                except AssertionError:
                    print node
                    raise
                self.state.last_printed = text
            self.state.last_node = node

    def handle_NEWLINE(self, node):
        self.state.nospace = True
        self.output.write("\n")
        self._indent()

    def handle_INDENT(self, node):
        self.state.indent_level+=1
        self.output.write(S_INDENT)

    def handle_DEDENT(self, node):
        self.state.indent_level-=1
        self.output.truncate(len(S_INDENT))

class Unparser(object):
    def __init__(self, symbol=py_symbol, token=py_token, offset = 0, handler_type = NodeHandler_AutoFormat):
        self.token = token
        self.offset= offset
        self.symbol= symbol
        self.handler_type = handler_type

    def __call__(self, tree):
        out = SourceCode("")
        assert isinstance(tree, (list, tuple)), "Wrong node type %s of node %s"%(type(tree), tree)
        handler = self.handler_type(output = out,
                                    symbol = self.symbol,
                                    token = self.token,
                                    offset = self.offset)
        handler.handle(tree)
        handler.has_addinfo(tree)
        out = "".join(out.source).lstrip('\n')
        return out

