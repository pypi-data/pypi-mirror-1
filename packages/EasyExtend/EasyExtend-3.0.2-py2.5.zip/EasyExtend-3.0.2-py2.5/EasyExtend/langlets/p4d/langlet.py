from conf import*                  # langlet specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from evalutil import*
from p4dbase import*
from bytelet import*
from EasyExtend.langlets.p4d.parsedef.parse_nfa import keywords
import EasyExtend.langlets.p4d.lexdef.lex_symbol as lex_symbol
import pprint as py_pprint

Hex.format = Hex.F_0x

class SpecialElement(Exception):
    pass


class LangletImporter(eeimporter.Importer):
    '''
    Defines langlet specific import behaviour.
    '''

class LangletTokenizer(eetokenizer.Tokenizer):
    '''
    Defines langlet specific token stream processor.
    '''
    @post
    def NAME(self, pos, tok, stream):
        name = tok[1]
        if name[-1] == '-':
            col_begin, col_end = tok[-1]
            self.add_token([lex_symbol.NAME, name[:-1], tok[2][0], (col_begin, col_end-1)], stream)
            self.add_token([lex_symbol.MINUS, '-', tok[2][0], (col_end-1, col_end)], stream)
        else:
            self.default(pos, tok, stream)

class LangletTransformer(Transformer):
    '''
    Defines langlet specific CST transformations.
    '''
    @transform
    def subscript(self, node):
        sub = node[1:]
        for i, item in enumerate(sub):
            if is_node(item, token.DOUBLECOLON):
                del sub[i]
                sub.insert(i, [token.COLON, ':', item[-1]])
                sub.insert(i, [token.COLON, ':', item[-1]])
                break

    @transform
    def NAME(self, node):
        name = node[1]
        if '-' in name:
            chain = self.node_stack(node)
            nd, chain = chain.up()
            nid = nd[0]
            if nid in (symbol.p4d_attr_access, symbol.p4d_name, symbol.p4d_accessor):
                return
            elif nid == symbol.atom:
                difference = ' - '.join(name.split('-'))
                chain = self.node_stack(node)
                nd, chain = chain.up()  # power
                nd, chain = chain.up()  # factor
                nd, chain = chain.up()  # term
                nd, chain = chain.up()  # arith_expr
                txt = unparse(nd)
                txt = txt.replace(name, difference)
                return find_node(self.langlet.parse(txt), symbol.arith_expr)
            else:
                raise SyntaxError("invalid syntax. No hyphenation permitted in Python names.")
        elif '::' in name:
            chain = self.node_stack(node)
            _trailer, chain = chain.up() # trailer
            if _trailer[0]!=symbol.trailer:
                raise SyntaxError("invalid use of accessor symbol '::'")
            nd, chain = chain.up() # power
            prefix, local_name = name.split("::")
            accessor = cstnode([symbol.p4d_accessor, [token.DOUBLECOLON, '::'], [token.NAME, local_name]])
            id_trailer = id(_trailer)
            for i, item in enumerate(nd):
                if id(item) == id_trailer:
                    del nd[i]
                    nd.insert(i,[symbol.trailer, accessor])
                    nd.insert(i, trailer(".", Name(prefix)))
                    break
            self.mark_node(nd)
            return nd

    @transform
    def SPECNUM(self, node):
        binnum = find_node(node, token.Binnumber)
        if binnum:
            return atomize(CST_CallFunc("Bin",[Number(binnum[1][2:])]))
        else:
            hexnum = String(' '.join([item[1][2:] for item in find_all(node, token.Hexnumber)]))
            return atomize(CST_CallFunc("Hex", [hexnum]))

    @transform
    def p4d_attr_access(self, node):
        "p4d_attr_access: '@' ( NAME | '*')"
        _name = find_node(node, token.NAME)
        if _name:
            return CST_CallFunc("attribute", [String(_name[1])])
        else:
            return CST_CallFunc("attributes", [])

    @transform
    def p4d_accessor(self, node):
        "p4d_accessor: '.' p4d_attr_access | '::' NAME | '.' '(' ['.'] test ')'"
        _attr = find_node(node, symbol.p4d_attr_access, level = 1)
        if _attr:
            self.unmark_node(_attr)
            _call = self.p4d_attr_access(_attr)
            name  = find_node(_call, token.NAME)[1]
            return trailer(".", name), find_node(_call, symbol.trailer)
        elif find_node(node, token.LPAR, level = 1):
            # .(@x == A)  ==> lambda this: this.attribute("x") == str(A)
            # .(x == A)   ==> lambda this: any(x.text() == A for x in this.x)
            # .(X op Y)   ==> lambda this: T(X) op T(Y)
            # .(x.X == A) ==> lambda this: any(x.X == A for x in this.x)
            # .(x::y == A) ==> lambda this: any(item.text() == A for item in this.children("x:y"))
            # .(@x::y == A) ==> lambda this: this.attribute("x:y") == str(A)
            if is_node(node[3], token.DOT):
                _test = find_node(node, symbol.test)  # child node
                _test[:] = find_node(self.langlet.parse("_."+unparse(_test)), symbol.test)
                filter_type = 3
            else:
                filter_type = 2  # this node
            body = find_node(node, symbol.test)
            self.unmark_node(body, token.NAME)
            _not_tests = find_all(body, py_symbol.not_test, level = 3)
            for nt in _not_tests:
                _comparison = find_node(nt, py_symbol.comparison)
                n = len(_comparison)
                if n>4:
                    raise SyntaxError("Invalid filter `.(%s)`"%unparse(_comparison))
                _expr_1 = _comparison[1]
                if find_node(_expr_1, token.DOUBLECOLON):
                    _pow = find_node(_expr_1, symbol.power)
                    for i,item in enumerate(_pow):
                        if isinstance(item, list):
                            if find_node(item,token.DOUBLECOLON):
                                _name = find_node(_pow[i-1], token.NAME)
                                _name[1] = _name[1]+':'+find_node(item, token.NAME)[1]
                                del _pow[i]
                                break
                self.run(_expr_1)
                name = find_node(_expr_1, token.NAME)[1]
                if n>2:
                    s_comp   = unparse(_comparison[2])
                    s_expr_2 = unparse(_comparison[3])
                s_expr_1 = unparse(_expr_1)
                if name == "attribute":
                    filter_type = 1  # attribute
                    if n == 4:
                        _expr = find_node(self.langlet.parse("(this.%s %s str(%s))"%(s_expr_1, s_comp, s_expr_2)), symbol.expr)
                    else:
                        _expr = find_node(self.langlet.parse("(this.%s)"%(s_expr_1,)), symbol.expr)
                else:
                    if s_expr_1 == name:
                        if n == 4:
                            if name != '_':
                                _expr = find_node(self.langlet.parse("(this.text() %s %s and this.tag == '%s')"%(s_comp, s_expr_2, name)), symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(this.text() %s %s)"%(s_comp, s_expr_2)), symbol.expr)
                        else:
                            _expr = find_node(self.langlet.parse("(this.tag == '%s')"%(name,)), symbol.expr)
                    else:
                        s_expr_1 = s_expr_1.replace(name, "this", 1)
                        if n == 4:
                            if name !='_':
                                _expr = find_node(self.langlet.parse("(%s %s %s and this.tag == '%s')"%(s_expr_1, s_comp, s_expr_2, name)), symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(%s %s %s)"%(s_expr_1, s_comp, s_expr_2)), symbol.expr)
                        else:
                            if name !='_':
                                _expr = find_node(self.langlet.parse("(%s and this.tag == '%s')"%(s_expr_1, name)), symbol.expr)
                            else:
                                _expr = find_node(self.langlet.parse("(%s)"%(s_expr_1,)), symbol.expr)
                del _comparison[1:]
                _comparison.append(_expr)
                _inner = CST_Lambda(body, ["this"])
            _lambda = CST_Lambda(CST_Tuple(filter_type, _inner),[])
            return trailer(".", "search"), trailer("(", arglist(argument(any_test(_lambda))),")")
        elif find_node(node, token.DOUBLECOLON):
            # .X :: Y
            locname = find_node(node, token.NAME)[1]
            chain = self.node_stack(node)
            nd, chain = chain.up() # trailer
            nd, chain = chain.up() # power
            j = 1000
            for i, item in enumerate(nd[1:]):
                if find_node(item, token.DOUBLECOLON):
                    break
                if find_node(item, symbol.arglist):
                    j = i

            if j == i-1:
                _str = find_node(nd, token.STRING)
                _str[1] = "'"+_str[1][1:-1]+":"+locname+"'"
                del nd[i+1]
            else:
                prefix  = find_node(nd[i], token.NAME)[1]
                nd[i]   = trailer(".", "child")
                nd[i+1] = trailer("(", arglist(argument(any_test(String(prefix+":"+locname)))),")")
            return nd


    @transform #_dbg("sn")
    def p4d_compound_stmt(self, node):
        "p4d_compound_stmt: ['elm' | NAME '='] p4d_element ':' p4d_suite"
        self.unmark_node(node)
        # transform this into a comma separated list of items if two or more entries are found
        # otherwise return just this entry
        chain = self.node_stack(node)
        _name = find_node(node, token.NAME, level = 1)
        obj_name = (_name[1] if _name else None)
        p4d_node = self.build_p4d_compound_stmt(node)
        S = self.p4d_string(p4d_node)
        if p4d_node.tag.startswith("bl:"):
            tagwrapper = any_test(CST_CallFunc("Bytelet",[CST_CallFunc("mapeval",[ [token.STRING,S], CST_CallFunc("globals",[]),CST_CallFunc("locals",[])])]))
        elif p4d_node.tag.startswith("bl-schema:"):
            tagwrapper = any_test(CST_CallFunc("ByteletSchema",[CST_CallFunc("mapeval",[ [token.STRING,S], CST_CallFunc("globals",[]),CST_CallFunc("locals",[])])]))
        else:
            tagwrapper = any_test(CST_CallFunc("P4D",[CST_CallFunc("mapeval",[ [token.STRING,S], CST_CallFunc("globals",[]),CST_CallFunc("locals",[])])]))
        if not obj_name:
            return any_stmt(tagwrapper)
        else:
            if obj_name == 'elm':
                name_fragments = find_all(find_node(node, symbol.p4d_name), token.NAME)
                if len(name_fragments) == 1:
                    obj_name = name_fragments[0][1]
                else:
                    prefix, obj_name = name_fragments[0][1],name_fragments[1][1]
                if obj_name in keywords:
                    raise SyntaxError("invalid syntax. Keyword cannot be used as name. Use explicit assignment instead.")
                if '-' in obj_name:
                    raise SyntaxError("invalid syntax. Hyphened name cannot be used as Python name. Use explicit assignment instead.")
            return any_stmt(CST_Assign(obj_name, tagwrapper))

    def p4d_string(self, p4dnode):
        return "'"+str(p4dnode)+"'"

    def build_p4d_compound_stmt(self, node, xmlnode = None):
        "p4d_compound_stmt: [NAME '='] p4d_element ':' p4d_suite"
        element = self.build_p4d_element(find_node(node, symbol.p4d_element))
        nodes    = self.build_p4d_suite(find_node(node, symbol.p4d_suite), element)
        if xmlnode:
            xmlnode.children.extend(nodes)
        else:
            xmlnode = nodes[0]
        return xmlnode

    def build_p4d_name(self, node):
        "p4d_name: NAME (':' NAME)*"
        return ":".join([name[1] for name in find_all(node, token.NAME) ])

    def build_p4d_element(self, node):
        "p4d_element: p4d_name ['(' [p4d_attribute_list] ')']"
        tag = self.build_p4d_name(find_node(node, symbol.p4d_name))
        xmlnode = P4DNode(tag, attrs = {})
        _attrlist = find_node(node, symbol.p4d_attribute_list)
        if _attrlist:
            _attributes = find_all(_attrlist, symbol.p4d_attribute, level = 1)
            attrs = {}
            for attr in _attributes:
                attr_name, attr_value = self.build_p4d_attribute(attr)
                attrs[attr_name] = attr_value
            xmlnode.attrs.update(attrs)
        return xmlnode

    def build_p4d_attribute(self, node):
        "p4d_attribute: p4d_name '=' ['&'] test"
        attr_name  = self.build_p4d_name(find_node(node, symbol.p4d_name))
        n_value    = find_node(node, symbol.test)
        if find_node(node, token.AMPER, level = 1):
            attr_value = "evaltostr_%s"%unparse(n_value)
        elif is_supersimple(n_value):
            S = find_node(n_value, token.STRING)
            if S:
                attr_value = S[1][1:-1]
            else:
                S = find_node(n_value, token.NUMBER)
                if S:
                    attr_value = "evaltostr_%s"%unparse(n_value)
                else:
                    _specnum = find_node(n_value, symbol.SPECNUM)
                    if _specnum:
                        attr_value = "evaltoobj_%s"%unparse(self.SPECNUM(_specnum))
                    else:
                        raise SyntaxError("P4D attribute value `%s` must be prefixed with &-operator for evaluation."%unparse(n_value))
        else:
            raise SyntaxError("P4D attribute value of `%s` must be prefixed with &-operator for evaluation."%unparse(node))
        return attr_name, attr_value

    def build_p4d_simple_stmt(self, node):
        "p4d_simple_stmt: (p4d_element | p4d_expr) NEWLINE"
        _p4d_element = find_node(node, symbol.p4d_element, level = 1)
        if _p4d_element:
            return self.build_p4d_element(_p4d_element)
        else:
            return self.build_p4d_expr(find_node(node, symbol.p4d_expr))

    def build_p4d_stmt(self, node, xmlnode):
        "p4d_stmt: p4d_simple_stmt | p4d_compound_stmt"
        if is_node(node[1], symbol.p4d_simple_stmt):
            res = self.build_p4d_simple_stmt(node[1])
            if isinstance(res, P4DNode):
                xmlnode.children.append(res)
                return [xmlnode]
            elif res.startswith("evaltoobj_"):
                xmlnode.children.append(res)
                return [xmlnode]
            else:
                xmlnode.text = res
                return [xmlnode]
        else:
            xmlnode = self.build_p4d_compound_stmt(node[1], xmlnode)
            return [xmlnode]

    def build_p4d_suite(self, node, xmlnode):
        "p4d_suite: p4d_simple_stmt | NEWLINE INDENT p4d_stmt+ DEDENT"
        if is_node(node[1], symbol.p4d_simple_stmt):
            return self.build_p4d_stmt([symbol.stmt, node[1]], xmlnode)
        else:
            nodes = []
            _stmts = find_all(node, symbol.p4d_stmt, level = 1)
            for _stmt in _stmts:
                self.build_p4d_stmt(_stmt, xmlnode)
            return [xmlnode]

    def build_p4d_expr(self, node):
        "p4d_expr: '&' test | '(' [ p4d_expr (',' p4d_expr)] ')' | STRING | NUMBER | SPECNUM | P4D_Comment"
        _test = find_node(node, symbol.test, level = 1)
        if _test:
            return "evaltoobj_"+unparse(_test)
        _expr_list = find_all([symbol.p4d_simple_stmt]+node[1:], symbol.p4d_expr, level = 1)
        if _expr_list:
            return "evaltoobj_"+str([self.build_p4d_expr(item) for item in _expr_list])
        p4d_comment = find_node(node, token.P4D_Comment, level = 1)
        if p4d_comment:
            comment = unparse(node)[2:-2]
            if comment[0] == '*' and comment[-1] == '*':
                comment = "restringify_"+hide_bad_chars(comment[1:-1])
                p4d_node = P4DNode("**")
            else:
                p4d_node = P4DNode("*")
                comment = "restringify_"+hide_bad_chars(comment)
            p4d_node.text = comment
            return p4d_node
        _str = find_node(node, token.STRING, level = 1)
        if _str:
            return "restringify_"+hide_bad_chars(node[1][1])
        _specnum = find_node(node, symbol.SPECNUM,level=1)
        if _specnum:
            return "evaltoobj_%s"%unparse(self.SPECNUM(_specnum))
        _number = find_node(node, token.NUMBER,level=1)
        if _number:
            return "evaltonum_"+node[1][1]
        raise TypeError("no P4D object content or attribute: `%s`."%unparse(node))

class InteractiveTransformer(LangletTransformer):
    def p4d_string(self, p4dnode):
        return str(p4dnode)


__publish__ = ["mapeval", "P4DNode", "P4D", "P4DList", "P4DName", "P4DNamespace", "P4DAccessError", "P4DContentList", "Bytelet", "ByteletSchema", "LEN", "Hex", "Bin", "VAL", "RAWLEN"]


