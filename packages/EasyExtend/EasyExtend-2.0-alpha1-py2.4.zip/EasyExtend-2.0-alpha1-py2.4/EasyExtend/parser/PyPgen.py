#! /usr/bin/env python
# ______________________________________________________________________
"""Module PyPgen

Python implementation of the Python distribution parser generator, pgen.

XXX This now assumes that everything in the common/python directory of the
Basil project is in the Python module path.

$Id: PyPgen.py,v 1.2 2003/10/02 17:37:17 jriehl Exp $
"""
# ______________________________________________________________________
# Module imports


import PgenParser
import EasyExtend.eetokenizer
import string


__DEBUG__ = 0
__BASIL__ = 0

if __DEBUG__:
    import pprint

# ______________________________________________________________________

class PyPgen:
    """Class PyPgen
    """
    # ____________________________________________________________
    def __init__ (self, fiber):
        """PyPgen.__init__
        """
        self.fiber  = fiber
        self.token  = fiber.token
        self.tokenizer = EasyExtend.eetokenizer.StdTokenizer(self.token)
        self.nfaGrammar = self.dfaGrammar = None
        self.nfa = None
        self.crntType = self.token.NT_OFFSET
        self.PgenParser = PgenParser.Parser(fiber)

    # ____________________________________________________________
    def addLabel (self, labelList, tokType, tokName):
        """PyPgen.addLabel
        """
        # XXX
        #labelIndex = 0
        #for labelType, labelName in labelList:
        #    if (labelType == tokType) and (labelName == tokName):
        #        return labelIndex
        #    labelIndex += 1
        labelTup = (tokType, tokName)
        if labelTup in labelList:
            return labelList.index(labelTup)
        labelIndex = len(labelList)
        labelList.append(labelTup)
        return labelIndex

    # ____________________________________________________________
    def handleStart (self, ast):
        """PyPgen.handleStart()
        """
        self.nfaGrammar = [[],[(self.token.ENDMARKER, "EMPTY")]]
        self.crntType = self.token.NT_OFFSET
        type, children = ast
        assert type == self.PgenParser.MSTART
        for child in children:
            if child[0] == self.PgenParser.RULE:
                self.handleRule(child)
        return self.nfaGrammar

    # ____________________________________________________________
    def handleRule (self, ast):
        """PyPgen.handleRule()

        NFA := [ type : Int, name : String, [ STATE ], start : Int, finish : Int ]
        STATE := [ ARC ]
        ARC := ( labelIndex : Int, stateIndex : Int )
        """
        # Build the NFA shell.
        self.nfa = [self.crntType, None, [], -1, -1]
        self.crntType += 1
        # Work on the AST node
        type, children = ast
        assert type == self.PgenParser.RULE
        name, colon, rhs, newline = children
        assert name[0][0] == self.token.NAME, "Malformed pgen parse tree"
        self.nfa[1] = name[0][1]
        if (self.token.NAME, name[0][1]) not in self.nfaGrammar[1]:
            self.nfaGrammar[1].append((self.token.NAME, name[0][1]))
        assert colon[0][0] == self.token.COLON, "Malformed pgen parse tree"
        start, finish = self.handleRhs(rhs)
        self.nfa[3] = start
        self.nfa[4] = finish
        assert newline[0][0] == self.token.NEWLINE, "Malformed pgen parse tree"
        # Append the NFA to the grammar.
        self.nfaGrammar[0].append(self.nfa)

    # ____________________________________________________________
    def handleRhs (self, ast):
        """PyPgen.handleRhs()
        """
        type, children = ast
        assert type == self.PgenParser.RHS
        start, finish = self.handleAlt(children[0])
        if len(children) > 1:
            cStart = start
            cFinish = finish
            start = len(self.nfa[2])
            self.nfa[2].append([(self.token.ENDMARKER, cStart)])
            finish = len(self.nfa[2])
            self.nfa[2].append([])
            self.nfa[2][cFinish].append((self.token.ENDMARKER, finish))
            for child in children[2:]:
                if child[0] == self.PgenParser.ALT:
                    cStart, cFinish = self.handleAlt(child)
                    self.nfa[2][start].append((self.token.ENDMARKER, cStart))
                    self.nfa[2][cFinish].append((self.token.ENDMARKER, finish))
        return start, finish

    # ____________________________________________________________
    def handleAlt (self, ast):
        """PyPgen.handleAlt()
        """
        type, children = ast
        assert type == self.PgenParser.ALT
        start, finish = self.handleItem(children[0])
        if len(children) > 1:
            for child in children[1:]:
                cStart, cFinish = self.handleItem(child)
                self.nfa[2][finish].append((self.token.ENDMARKER, cStart))
                finish = cFinish
        return start, finish

    # ____________________________________________________________
    def handleItem (self, ast):
        """PyPgen.handleItem()
        """
        nodeType, children = ast
        assert nodeType == self.PgenParser.ITEM
        if children[0][0] == self.PgenParser.ATOM:
            start, finish = self.handleAtom(children[0])
            if len(children) > 1:
                # Short out the child NFA
                self.nfa[2][finish].append((self.token.ENDMARKER, start))
                if children[1][0][0] == self.token.STAR:
                    finish = start
                else:
                    assert children[1][0][0] == self.token.PLUS
        else:
            assert children[0][0][0] == self.token.LSQB
            start = len(self.nfa[2])
            finish = start + 1
            self.nfa[2].append([(self.token.ENDMARKER, finish)])
            self.nfa[2].append([])
            cStart, cFinish = self.handleRhs(children[1])
            self.nfa[2][start].append((self.token.ENDMARKER, cStart))
            self.nfa[2][cFinish].append((self.token.ENDMARKER, finish))
            assert (len(children) == 3) and (children[2][0][0] == self.token.RSQB)
        return start, finish

    # ____________________________________________________________
    def handleAtom (self, ast):
        """PyPgen.handleAtom()
        """
        nodeType, children = ast
        assert nodeType == self.PgenParser.ATOM
        assert type(children[0][0]) == type(())
        tokType, tokName, lineno, add_info = children[0][0]
        if tokType == self.token.LPAR:
            start, finish = self.handleRhs(children[1])
            assert (len(children) == 3) and (children[2][0][0] == self.token.RPAR)
        elif tokType in (self.token.STRING, self.token.NAME):
            start = len(self.nfa[2])
            finish = start + 1
            labelIndex = self.addLabel(self.nfaGrammar[1], tokType, tokName)
            self.nfa[2].append([(labelIndex, finish)])
            self.nfa[2].append([])
        else:
            assert 1 == 0, "Malformed pgen parse tree."
        return start, finish

    # ____________________________________________________________
    def generateDfaGrammar (self, nfaGrammar):
        """PyPgen.makeDfaGrammar()
        See notes in basil.lang.python.DFAParser for output schema.
        """
        dfas = []
        for nfa in nfaGrammar[0]:
            dfas.append(self.nfaToDfa(nfa))
        return [dfas, self.nfaGrammar[1], dfas[0][0], 0]

    # ____________________________________________________________
    def addClosure (self, stateList, nfa, istate):
        stateList[istate] = True
        arcs = nfa[2][istate]
        for label, arrow in arcs:
            if label == self.token.ENDMARKER:
                self.addClosure(stateList, nfa, arrow)

    # ____________________________________________________________
    def nfaToDfa (self, nfa):
        """PyPgen.nfaToDfa()
        """
        tempStates = []
        # tempState := [ stateList : List of Boolean,
        #                arcList : List of tempArc ]
        crntTempState = [[False] * len(nfa[2]), [], False]
        self.addClosure(crntTempState[0], nfa, nfa[3])
        crntTempState[2] = crntTempState[0][nfa[4]]
        if crntTempState[2]:
            print ("PyPgen: Warning, nonterminal '%s' may produce empty." %
                   (nfa[1]))
        tempStates.append(crntTempState)
        index = 0
        while index < len(tempStates):
            crntTempState = tempStates[index]
            for componentState in range(0, len(nfa[2])):
                if not crntTempState[0][componentState]:
                    continue
                nfaArcs = nfa[2][componentState]
                for label, nfaArrow in nfaArcs:
                    if label == self.token.ENDMARKER:
                        continue
                    foundTempArc = False
                    for tempArc in crntTempState[1]:
                        if tempArc[0] == label:
                            foundTempArc = True
                            break
                    if not foundTempArc:
                        tempArc = [label, -1, [False] * len(nfa[2])]
                        crntTempState[1].append(tempArc)
                    self.addClosure(tempArc[2], nfa, nfaArrow)
            for arcIndex in range(0, len(crntTempState[1])):
                label, arrow, targetStateList = crntTempState[1][arcIndex]
                targetFound = False
                arrow = 0
                for destTempState in tempStates:
                    if targetStateList == destTempState[0]:
                        targetFound = True
                        break
                    arrow += 1
                if not targetFound:
                    assert arrow == len(tempStates)
                    tempState = [targetStateList[:], [],
                                 targetStateList[nfa[4]]]
                    tempStates.append(tempState)
                # Write arrow value back to the arc
                crntTempState[1][arcIndex][1] = arrow
            index += 1
        tempStates = self.simplifyTempDfa(nfa, tempStates)
        return self.tempDfaToDfa(nfa, tempStates)

    # ____________________________________________________________
    def sameState (self, s1, s2):
        """PyPgen.sameState()
        """
        if (len(s1[1]) != len(s2[1])) or (s1[2] != s2[2]):
            return False
        for arcIndex in range(0, len(s1[1])):
            arc1 = s1[1][arcIndex]
            arc2 = s2[1][arcIndex]
            if arc1[:-1] != arc2[:-1]:
                return False
        return True

    # ____________________________________________________________
    def simplifyTempDfa (self, nfa, tempStates):
        """PyPgen.simplifyDfa()
        """
        if __DEBUG__:
            print "_" * 70
            pprint.pprint(nfa)
            pprint.pprint(tempStates)
        changes = True
        deletedStates = []
        while changes:
            changes = False
            for i in range(1, len(tempStates)):
                if i in deletedStates:
                    continue
                for j in range(0, i):
                    if j in deletedStates:
                        continue
                    if self.sameState(tempStates[i], tempStates[j]):
                        deletedStates.append(i)
                        for k in range(0, len(tempStates)):
                            if k in deletedStates:
                                continue
                            for arc in tempStates[k][1]:
                                if arc[1] == i:
                                    arc[1] = j
                        changes = True
                        break
        for stateIndex in deletedStates:
            tempStates[stateIndex] = None
        if __DEBUG__:
            pprint.pprint(tempStates)
        return tempStates

    # ____________________________________________________________
    def tempDfaToDfa (self, nfa, tempStates):
        """PyPgen.tempDfaToDfa()
        """
        dfaStates = []
        dfa = [nfa[0], nfa[1], 0, dfaStates, None]
        stateMap = {}
        tempIndex = 0
        for tempState in tempStates:
            if None != tempState:
                stateMap[tempIndex] = len(dfaStates)
                dfaStates.append(([], (0,0,()), 0))
            tempIndex += 1
        for tempIndex in stateMap.keys():
            stateList, tempArcs, accepting = tempStates[tempIndex]
            dfaStateIndex = stateMap[tempIndex]
            dfaState = dfaStates[dfaStateIndex]
            for tempArc in tempArcs:
                dfaState[0].append((tempArc[0], stateMap[tempArc[1]]))
            if accepting:
                dfaState[0].append((self.token.ENDMARKER, dfaStateIndex))
        return dfa

    # ____________________________________________________________
    def translateLabels (self, grammar):
        """PyPgen.translateLabels()
        """
        tokenNames = self.token.tok_name.values()
        labelList = grammar[1]
        for labelIndex in range(0, len(labelList)):
            type, name = labelList[labelIndex]
            if type == self.token.NAME:
                isNonTerminal = False
                for dfa in grammar[0]:
                    if dfa[1] == name:
                        labelList[labelIndex] = (dfa[0], None)
                        isNonTerminal = True
                        break
                if not isNonTerminal:
                    if name in tokenNames:
                        labelList[labelIndex] = (getattr(self.token, name), None)
                    else:
                        print "Can't translate NAME label '%s'" % name
            elif type == self.token.STRING:
                assert name[0] == name[-1]
                sname = name[1:-1]
                if (sname[0] in string.letters) or (sname[0] == "_"):
                    labelList[labelIndex] = (self.token.NAME, sname)
                elif self.token.TOKEN_MAP.has_key(sname):
                    labelList[labelIndex] = (self.token.TOKEN_MAP[sname],
                                             None)
                else:
                    print "Can't translate STRING label %s" % name
        return grammar

    # ____________________________________________________________
    def calcFirstSet (self, grammar, dfa):
        """PyPgen.calcFirstSet()
        """
        if dfa[4] == -1L:
            print "Left-recursion for '%s'" % dfa[1]
            return
        if dfa[4] != None:
            print "Re-calculating FIRST set for '%s' ???" % dfa[1]
        dfa[4] = -1L
        symbols = []
        result = 0L # XXX Can I get this arb. size stuff to translate to C?
        state = dfa[3][dfa[2]]
        for arc in state[0]:
            sym = arc[0]
            if sym not in symbols:
                symbols.append(sym)
                type = grammar[1][sym][0]
                if (type >= self.token.NT_OFFSET):
                    # Nonterminal
                    ddfa = grammar[0][type - self.token.NT_OFFSET]
                    if ddfa[4] == -1L:
                        print "Left recursion below '%s'" % dfa[1]
                    else:
                        if ddfa[4] == None:
                            self.calcFirstSet(grammar, ddfa)
                        result |= ddfa[4]
                else:
                    result |= (1L << sym)
        dfa[4] = result

    # ____________________________________________________________
    def generateFirstSets (self, grammar):
        """PyPgen.generateFirstSets()
        """
        dfas = grammar[0]
        index = 0
        while index < len(dfas):
            dfa = dfas[index]
            if None == dfa[4]:
                self.calcFirstSet(grammar, dfa)
            index += 1
        for dfa in dfas:
            set = dfa[4]
            resultStr = ''
            while set > 0L:
                crntBits = set & 0xff
                resultStr += chr(crntBits)
                set >>= 8
            properSize = ((len(grammar[1]) / 8) + 1)
            if len(resultStr) < properSize:
                resultStr += ('\x00' * (properSize - len(resultStr)))
            dfa[4] = resultStr
        return grammar

    # ______________________________________________________________________
    def createGrammar(self, cst):
        nfaGrammar = self.handleStart(cst)
        grammar = self.generateDfaGrammar(nfaGrammar)
        self.translateLabels(grammar)
        self.generateFirstSets(grammar)
        grammar[0] = map(tuple, grammar[0])
        return tuple(grammar)


