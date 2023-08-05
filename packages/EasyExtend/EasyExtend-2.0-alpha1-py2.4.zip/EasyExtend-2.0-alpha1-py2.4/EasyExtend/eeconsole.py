'''
Command compiler and console that executes fiber specific commands.
'''

# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import EasyExtend
import eecommon
from   eexcept import*
from   EasyExtend.parser.DFAParser import DFAParser
from   eetokenizer import StdTokenizer
from   csttools import split_file_input, projection
import cst2source
import sys
import traceback
import __main__

PyCF_DONT_IMPLY_DEDENT = 0x200   # ??? some undocumented compiler flag with unkown functionality but effect.

class ConsoleBase(object):
    def write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subclass may
        replace this with a different implementation.

        """
        sys.stderr.write(data)

    def input(self, prompt):
        """
        Wraps raw_input. Override this method in subclasses to customize input behaviour.
        @param prompt: prompt to be printed at input.
        """
        return raw_input(prompt)

    def reset(self):
        self.parseTree   = None
        self.line_buffer = []

    def at_exit(self):
        raise NotImplementedError

    def try_parse(self):
        raise NotImplementedError

    def compile_cst(self):
        raise NotImplementedError

    def interact(self):
        '''
        Interactive loop.
        This implementation uses two flags for determining if more user input has to be expected.
        - more: true if command is incomplete. Otherwise false.
        - guess_more: true if command is incomplete or complete but still expects an empty line
          to be passed for statement-termination.
        The guess_more flag is introduced instead of hypothetical line break trailers and maybe_compile
        cruft of the stdlibs implementation ( codeop.py ).
        '''
        more = False
        guess_more = False
        self.reset()
        while 1:
            try:
                if more or guess_more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.input(prompt)
                    self.line_buffer.append(line)
                    try:
                        if line:
                            self.parseTree = self.try_parse()
                        else:
                            guess_more = False
                        if not self.parseTree:
                            if line:
                                more = True
                            else:
                                self.line_buffer = []
                            continue
                        elif more:
                             guess_more = True
                             more = False
                             continue
                        if not more and not guess_more:
                            code = self.compile_cst(self.parseTree)
                            self.runcode(code)
                            self.reset()
                    except (EOFError, KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        self.reset()
                        more = guess_more = False
                        self.showtraceback()
                except EOFError:
                    self.write("\n")
                    break
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.reset()
                more = guess_more = False
        self.at_exit()

    def runcode(self, code):
        """
        Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        (copied from code.py)
        """
        try:
            exec code in self.locals
        except SystemExit:
            try:
                self.at_exit()
            finally:
                raise
        except:
            self.showtraceback()

    def showtraceback(self):
        '''
        (Copied from code.py)
        '''
        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            list = traceback.format_list(tblist)
            if list:
                list.insert(0, "Traceback (most recent call last):\n")
            list[len(list):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None
        map(sys.stderr.write, list)


class EEConsole(ConsoleBase, eecommon.EEShow):
    '''
    Console object used to handle user input.

    This console object is to some extend a redesign of the InteractiveConsole object of the stdlib.

        - tryParse, compile_cst and runcode are clearly separated from each other and can be adapted
          in subclasses.
        - the interact method is removed from cruft of codeop.py
        - some EE specifific methods are added used show CSTs, token streams and unparsed Python code
    '''
    def __init__(self, fiber, name, locals=None, globals = None, use_new_prompt = True):
        if locals is None:
            locals = __main__.__dict__
        self.locals  = locals
        self.grammar  = fiber.PyGrammar.grammarObj
        self.fiber = fiber
        self.console_name = name
        if use_new_prompt:
            self.at_start()
        self.line_buffer = []
        self.terminates  = True
        # debug options
        self.options  = fiber.options
        self._compiled = {}


    def at_start(self):
        '''
        Method used at console start. Select right prompt and print header.
        '''
        if hasattr(self.fiber, "prompt"):
            sys.ps1 = self.prompt = self.fiber.prompt
        else:
            sys.ps1 = self.prompt = ">>> "
        sys.ps2 = "."*(len(self.prompt)-1)+" "
        if hasattr(self.fiber, "docs"):
            docs = self.fiber.docs
        else:
            docs = ""

        py_vers = " Running on Python %s"%sys.version
        if docs:
            fiber_doc = " Fiber documentation: %s"%docs
        else:
            fiber_doc = " Fiber documentation: not yet available."
        self._header_len =  max(len(py_vers),len(fiber_doc))+2
        print "_"*self._header_len
        print
        print " %s"% self.console_name
        print
        print py_vers
        if docs:
            print fiber_doc
        print "_"*self._header_len
        print

    def at_exit(self):
        "reset default prompt"
        sys.ps1 = ">>> "
        sys.ps2 = "... "
        print "_"*self._header_len
        print

    def compile_cst(self, parseTree):
        """
        Transforms fiber expr/statement into one or more Python
        statements. Compile and execute those statements.
        @param parseTree: fiber cst
        """
        self.maybe_show_cst_before(parseTree)
        if hasattr(self.fiber, "InteractiveTransformer"):
            transformer = self.fiber.InteractiveTransformer(self.fiber, locals = self.locals)
        else:
            transformer = self.fiber.FiberTransformer(self.fiber)
        transformer.run(parseTree)
        projection(parseTree)
        transformer.terminate()
        self.maybe_show_cst_after(parseTree)
        sources = []
        for tree in split_file_input(parseTree):
            sources.append(self.fiber.unparse(tree))
        for src in sources:
            self.maybe_show_python(src)
            if not self._compiled.get(src):
                _code = compile(src,"<input>","single", PyCF_DONT_IMPLY_DEDENT)
                self._compiled[src] = _code
        for src in sources[:-1]:
            self.runcode(self._compiled[src])
        return self._compiled[sources[-1]]


    def try_parse(self):
        '''
        Parses eventually incomplete fiber statement.
        Following actions are possible:
        1) Complete fiber statement could be parsed. Parse tree is returned.
        2) Fiber statement incomplete. Needs more user input. Nothing is returned.
        3) Syntax error detected within fiber statement. SyntaxError exception is raised.
        '''
        source = '\n'.join(self.line_buffer)
        if source in ("quit",":quit"):  # special commands for console. "quit" is standard in 2.5
            try:
                self.at_exit()
            finally:
                raise SystemExit
        try:
            # show token if 'show_token' option available
            self.maybe_show_token(source)
            # create parse tree using the fibers grammar and tokenizer
            tokenizer   = StdTokenizer(self.fiber.token)
            tokenizer.tokenize_input(cst2source.SourceCode(source).readline)
        except TokenError:
            return
            cls, msg, tb = sys.exc_info()
            raise ParserError, msg, tb
        dfa_parser = DFAParser(self.fiber, **self.options)
        try:
            if dfa_parser.check_start_symbol(self.grammar, self.fiber.symbol.file_input):
                parseTree = dfa_parser.parsetok(tokenizer, self.grammar, self.fiber.symbol.file_input)
            elif dfa_parser.check_start_symbol(self.grammar, self.fiber.symbol.single_input):
                parseTree = dfa_parser.parsetok(tokenizer, self.grammar, self.fiber.symbol.single_input)
            else:
                raise SyntaxError, "No correct start-symbol available. Check symbol.py of your fiber definion."
            return parseTree
        except SyntaxError, err:
            # hack - don't know better how to capture a SyntaxError caused by an incomplete command
            #        that doesn't terminate command execution
            if err.args[0].endswith("unexpected ''") or err.args[0].endswith("expected (not '')"):
                return None
            else:
                cls, msg, tb = sys.exc_info()
                raise SyntaxError, msg, tb
        except TokenError, err:
            return
