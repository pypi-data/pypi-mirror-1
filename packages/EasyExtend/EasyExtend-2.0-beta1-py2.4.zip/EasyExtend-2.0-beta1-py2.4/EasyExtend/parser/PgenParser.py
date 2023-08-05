#! /usr/bin/env python
# ______________________________________________________________________
"""Module PgenParser

Implements a recursive descent parser for the Python pgen parser generator
input language.

$Id: PgenParser.py,v 1.2 2003/10/02 17:37:17 jriehl Exp $
----------------------------------------------------------

ks: changes 2006/10/10
    - making parsing functions methods
    - using fiber.token instead of stdlibs token module

"""

__DEBUG__ = 0

if __DEBUG__:
    import pprint

class Parser:
    def __init__(self, fiber, tuple_style = True):
        self.fiber = fiber
        self.token = fiber.token
        self.tuple_style = tuple_style
        self.__dict__.update(self.token.Pgen.__dict__)


    def add_token(self, children, crntToken):
        if self.tuple_style:
            children.append((crntToken,[]))
        else:
            children.append(crntToken)


    def expect (self, val, tok):
        type, name, lineno, add_info = tok
        if val != type:
            if name == None:
                gotStr = self.token.tok_name[type]
            else:
                gotStr = `name`
            errStr = ("Line %d, expecting %s, got %s." %
                      (lineno, self.token.tok_name[val], gotStr))
            raise SyntaxError, errStr

    # ______________________________________________________________________

    def handleStart (self, tokenizer):
        """handleStart()
        MSTART := ( RULE | NEWLINE )* ENDMARKER
        """
        children = []
        crntToken = tokenizer.next_token()
        while self.token.ENDMARKER != crntToken[0]:
            if self.token.NEWLINE == crntToken[0]:
                self.add_token(children, crntToken)
                crntToken = None
            else:
                ruleResult, crntToken = self.handleRule(tokenizer, crntToken)
                children.append(ruleResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
        self.add_token(children, crntToken)
        return (self.MSTART, children)

    # ______________________________________________________________________

    def handleRule (self, tokenizer, crntToken = None):
        """handleRule()
        RULE := NAME COLON RHS NEWLINE
        """
        children = []
        if None == crntToken:
            crntToken = tokenizer.next_token()
        self.expect(self.token.NAME, crntToken)
        self.add_token(children, crntToken)
        crntToken = tokenizer.next_token()
        self.expect(self.token.COLON, crntToken)
        self.add_token(children, crntToken)
        rhsResult, crntToken = self.handleRhs(tokenizer)
        children.append(rhsResult)
        if None == crntToken:
            crntToken = tokenizer.next_token()
        self.expect(self.token.NEWLINE, crntToken)
        self.add_token(children, crntToken)
        result = (self.token.Pgen.RULE, children)
        if __DEBUG__:
            pprint.pprint(result)
        return result, None

    # ______________________________________________________________________

    def handleRhs (self, tokenizer, crntToken = None):
        """handleRhs()
        RHS := ALT ( VBAR ALT )*
        """
        children = []
        altResult, crntToken = self.handleAlt(tokenizer, crntToken)
        children.append(altResult)
        if None == crntToken:
            crntToken = tokenizer()
        while crntToken[0] == self.token.VBAR:
            self.add_token(children, crntToken)
            altResult, crntToken = self.handleAlt(tokenizer)
            children.append(altResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
        result = (self.token.Pgen.RHS, children)
        if __DEBUG__:
            pprint.pprint(result)
        return result, crntToken

    # ______________________________________________________________________

    def handleAlt (self, tokenizer, crntToken = None):
        """handleAlt()
        ALT := ITEM+
        """
        children = []
        itemResult, crntToken = self.handleItem(tokenizer, crntToken)
        children.append(itemResult)
        if None == crntToken:
            crntToken = tokenizer.next_token()
        while crntToken[0] in (self.token.LSQB, self.token.LPAR, self.token.NAME, self.token.STRING):
            itemResult, crntToken = self.handleItem(tokenizer, crntToken)
            children.append(itemResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
        return (self.ALT, children), crntToken

    # ______________________________________________________________________

    def handleItem (self, tokenizer, crntToken = None):
        """handleItem()
        ITEM := LSQB RHS RSQB
             | ATOM ( STAR | PLUS )?
        """
        children = []
        if None == crntToken:
            crntToken = tokenizer.next_token()
        if crntToken[0] == self.token.LSQB:
            self.add_token(children, crntToken)
            rhsResult, crntToken = self.handleRhs(tokenizer)
            children.append(rhsResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
            self.expect(self.token.RSQB, crntToken)
            self.add_token(children, crntToken)
            crntToken = None
        else:
            atomResult, crntToken = self.handleAtom(tokenizer,crntToken)
            children.append(atomResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
            if crntToken[0] in (self.token.STAR, self.token.PLUS):
                self.add_token(children, crntToken)
                crntToken = None
        return (self.ITEM, children), crntToken

    # ______________________________________________________________________

    def handleAtom (self, tokenizer, crntToken = None):
        """handleAtom()
        ATOM := LPAR RHS RPAR
              | NAME
              | STRING
        """
        children = []
        if None == crntToken:
            crntToken = tokenizer()
        tokType = crntToken[0]
        if tokType == self.token.LPAR:
            children.append((crntToken, []))
            rhsResult, crntToken = self.handleRhs(tokenizer)
            children.append(rhsResult)
            if None == crntToken:
                crntToken = tokenizer.next_token()
            self.expect(self.token.RPAR, crntToken)
            self.add_token(children, crntToken)
            #crntToken = None
        elif tokType == self.token.STRING:
            self.add_token(children, crntToken)
            #crntToken = None
        else:
            self.expect(self.token.NAME, crntToken)
            self.add_token(children, crntToken)
            # crntToken = None
        return (self.ATOM, children), None

    # ______________________________________________________________________

    def parseString (self, inString, tokenizer):
        tokenizer.tokenize_string(inString)
        return self.handleStart(tokenizer)

    # ______________________________________________________________________

    def parseFile (self, filename, tokenizer):
        tokenizer.tokenize_file(filename)
        return self.handleStart(tokenizer)




