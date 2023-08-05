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
from util.path import path
import sys
import os
import traceback
import __main__
import re

PyCF_DONT_IMPLY_DEDENT = 0x200   # ??? some undocumented compiler flag with unkown functionality but effect.

class User:
    '''
    Used to mediate or simulate user actions
    '''
    def get_input(self, prompt):
        return raw_input(prompt)

class ConsoleBase(object):
    def write(self, data):
        sys.stdout.write(data)

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
                    line = self.user.get_input(prompt)
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
                                self.reset()
                            continue
                        elif more:
                             guess_more = True
                             more = False
                             continue
                        if not more and not guess_more:
                            code = self.compile_cst(self.parseTree)
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
            except SystemExit:
                self.at_exit()
                break

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
            lst = traceback.format_list(tblist)
            if lst:
                lst.insert(0, "Traceback (most recent call last):\n")
            lst[len(lst):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None
        self.write("".join(lst))


class EEConsole(ConsoleBase, eecommon.EEShow):
    '''
    Console object used to handle user input.

    This console object is to some extend a redesign of the InteractiveConsole object of the stdlib.

        - tryParse, compile_cst and runcode are clearly separated from each other and can be adapted
          in subclasses.
        - the interact method is removed from cruft of codeop.py
        - some EE specifific methods are added used show CSTs, token streams and unparsed Python code
    '''
    def __init__(self, fiber,
                       name,
                       locals = None,
                       globals = None,
                       use_new_prompt   = True,
                       source_filter = lambda x:x,
                       **kwd):
        self.user = User()
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
        self.source_filter = source_filter


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

        py_vers = " On Python %s"%sys.version
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
        if hasattr(self,"additional_header_info"):
            print
            print  self.additional_header_info
            print
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
            src = self.fiber.unparse(tree)
            src = self.source_filter(src)
            sources.append(self.fiber.unparse(tree))
        try:
            for src in sources:
                if not self._compiled.get(src):
                    _code = compile(src,"<input>","single", PyCF_DONT_IMPLY_DEDENT)
                    self._compiled[src] = _code
        finally:
            self.maybe_show_python("\n".join(sources))
        for src in sources:
            self.runcode(self._compiled[src])


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


class EERecordedConsole(EEConsole):

    class dual_io:
        '''
        Wraps a standard interface and extend it
        by a report which is usually a text-log.
        '''
        def __init__(self, rep, std):
            self.report  = rep
            self.std     = std

        def write(self,s):
            self.std.write(s)
            self.report.write(s)

        def readline(self,*size):
            return self.std.readline(*size)

        def flush(self):
            return self.std.flush()

    class RecordedUser(User):
        def __init__(self, report):
            self.report = report

        def get_input(self, prompt):
            text = raw_input(prompt)
            self.report.write(text+"\n")
            return text


    def __init__(self, fiber, name, *args, **kwd):
        self.report = self.acquire_session_report(fiber,name,kwd.get("recording"))
        self.additional_header_info = " Creates session report " + path(self.report.name).basename()
        super(EERecordedConsole, self).__init__(fiber, name, *args, **kwd)
        self.user = self.RecordedUser(self.report)

    def _set_dual_IO(self):
        global sys
        sys.stdout   = self.dual_io(self.report,sys.stdout)
        sys.stdin    = self.dual_io(self.report,sys.stdin)
        sys.stderr   = self.dual_io(self.report,sys.stderr)

    def _clear_dual_IO(self):
        global sys
        try:
            sys.stdout = sys.stdout.std
            sys.stdin  = sys.stdin.std
            sys.stderr = sys.stderr.std
        except AttributeError:   # no report object
            pass

    def at_start(self):
        self._set_dual_IO()
        super(EERecordedConsole, self).at_start()

    def at_exit(self):
        super(EERecordedConsole, self).at_exit()
        self._clear_dual_IO()
        self.report.close()

    def acquire_session_report(self, fiber, console_name, recording_option):
        pth = path(fiber.__file__).dirname()+os.sep+"fibercon"
        if recording_option == "enum":
            k = str(len(pth.files("*.eerp"))+1)
            f = pth+os.sep+console_name+"_"+k+".eerp"
            return file(f,"w")
        elif recording_option.startswith("+"):
            f = pth+os.sep+console_name+"_"+recording_option[1:]+".eerp"
            return file(f,"w")
        elif recording_option.endswith("+"):
            f = pth+os.sep+recording_option[:-1]+"_"+console_name+".eerp"
            return file(f,"w")
        elif recording_option == "stdname":
            f = pth+os.sep+console_name+".eerp"
            return file(f,"w")
        elif recording_option.startswith(os.sep):
            f = pth+recording_option
            return file(f,"w")
        else:
            raise ValueError("Invalid recording option: '%s'"%recording_option)


class EEReplayConsole(EEConsole):

    class recorded_out:
        '''
        Wraps a standard interface and extend it
        by a report which is usually a text-log.
        '''
        def __init__(self, std, console):
            self.console = console
            self.std     = std

        def write(self,s):
            self.std.write(s)
            self.console.last_output.set(s)
            self.console.line_count+=s.count("\n")
            __main__.__dict__["__"] = str(self.console.last_output)

        def readline(self,*size):
            return self.std.readline(*size)

        def flush(self):
            return self.std.flush()

    class ReplayedUser(User):
        def __init__(self, session_protocol):
            self.session_protocol = session_protocol
            self.get_input = self.get_input_from_protocol

        def get_input_from_protocol(self, prompt):
            try:
                prefix, user_input = self.session_protocol.next()
                if prefix.startswith("?!"):
                    self.get_input = self.get_raw_user_input
                    return user_input
                elif prefix.startswith("?"):
                    self.get_input = self.get_raw_user_input
                    return self.get_raw_user_input(prefix[1:])
                else:
                    return user_input
            except StopIteration:
                raise SystemExit


        def get_raw_user_input(self, prompt):
            text = raw_input(prompt)
            if text.strip() == "!":
                self.get_input = self.get_input_from_protocol
                return self.get_input_from_protocol(prompt)
            return text

    class LastOutput(object):
        def __init__(self, s):
            self.items = []

        def _get_s(self):
            return self.select()

        s = property(_get_s)

        def set(self, s):
            if len(self.items)==3:
                del self.items[0]
            self.items.append(s)

        def select(self):
            items = [item for item in self.items[:-1] if item.strip()]
            if items:
                return items[-1]
            else:
                return ""

        def __str__(self):
            return self.select()

        def __repr__(self):
            return self.select()


    def __init__(self, fiber, name, *args, **kwd):
        self.last_output   = self.LastOutput("")
        self.line_count    = 0
        self.recorded_session = self.find_recorded_session(fiber,name,kwd.get("session"))
        self.additional_header_info = " Replay session " + path(self.recorded_session.name).basename()
        super(EEReplayConsole, self).__init__(fiber, name, *args, **kwd)
        self.prefix_pattern = self.prepare_prefix()
        self.user = self.ReplayedUser(self.session_protocol())


    def prepare_prefix(self):
        prompt1 = sys.ps1.rstrip()
        prompt2 = sys.ps2.rstrip()
        return re.compile('(?:\\?\\!?)?(?:'+re.escape(prompt1)+"\\ ?|"+re.escape(prompt2)+'\\ ?)')

    def split_prefix(self, line):
        m = self.prefix_pattern.match(line)
        if m:
            prefix = m.group()
            print line,
            text = line[len(prefix):].rstrip()
            return prefix, text
        else:
            if line.startswith("#"):
                print line,
            return None, line

    def at_start(self):
        self._set_recorded_output()
        super(EEReplayConsole, self).at_start()

    def at_exit(self):
        super(EEReplayConsole, self).at_exit()
        self._clear_recorded_output()

    def _set_recorded_output(self):
        global sys
        __main__.__dict__["__"] = self.last_output
        sys.stdout   = self.recorded_out(sys.stdout, self)
        sys.stdin    = self.recorded_out(sys.stdin, self)
        sys.stderr   = self.recorded_out(sys.stderr, self)

    def _clear_recorded_output(self):
        global sys
        try:
            sys.stdout = sys.stdout.std
            sys.stdin  = sys.stdin.std
            sys.stderr = sys.stderr.std
        except AttributeError:   # no report object
            pass

    def session_protocol(self):
        while True:
            line = self.recorded_session.next()
            prefix, user_input = self.split_prefix(line)
            if prefix:
                yield prefix, user_input
            else:
                continue

    def find_recorded_session(self, fiber, console_name, session):
        pth = path(fiber.__file__).dirname()+os.sep+"fibercon"
        if os.sep in session:
            return file(session)
        else:
            if session.isdigit():
                f = pth+os.sep+console_name+"_"+session+".eerp"
                if f.isfile():
                    return file(f)
            elif session == '_':
                f = pth+os.sep+console_name+".eerp"
                if f.isfile():
                    return file(f)
            elif session.startswith("+"):
                f = pth+os.sep+console_name+"_"+session[1:]+".eerp"
                if f.isfile():
                    return file(f)
            elif session.endswith("+"):
                f = pth+os.sep+session[:-1]+"_"+console_name+".eerp"
                if f.isfile():
                    return file(f)
            else:
                f = pth+os.sep+session
                if f.isfile():
                    return file(f)
        raise ValueError("Invalid session: '%s'"% session)


def raises(exc, func, *args, **kwd):
    '''
    Turns a side effect into a boolean value.
    @param exc: exception class. function is expected to raise an exception of this class.
    @param func: function to raise an exception.
    @param args: optional arguments of func.
    @param kwd: optional keyword areguments of func.
    @returns: True if exception 'exc' is raised, False otherwise.
    '''
    try:
        func(*args, **kwd)
    except exc:
        return True
    else:
        return False

__main__.__dict__["raises"] = raises

class EEReplayConsoleTest(EEReplayConsole):

    def __init__(self, fiber, name, *args, **kwd):
        super(EEReplayConsoleTest, self).__init__(fiber, name, *args, **kwd)
        self.assertions = []

    class Assertion:
        def __init__(self):
            self.Line = 0
            self.Status = "OK"
            self.Text = ""
            try:
                self.last_exc = sys.last_value
            except AttributeError:
                self.last_exc = None


    def print_result(self):
        print
        print "--------------------."
        print "Recorded assertions |"
        print "--------------------------------------------------------------------------------------------------"
        print "Status |eerp ln|repl ln| Assertion"
        print "-------+-------+-------+--------------------------------------------------------------------------"
        form_status = "%-7s|"
        form_line   = " %-6s|"
        form_assert = " %s"
        res = []
        for a in self.assertions:
            res.append(form_status % a.Status)
            res.append(form_line % a.SrcLine)
            res.append(form_line % a.DestLine)
            res.append(form_assert % a.Text)
            res.append("\n")
        text = "".join(res)
        print text[:-1]
        print "-------+-------+-------+--------------------------------------------------------------------------"

    def session_protocol(self):
        _assertion = None
        i = 0
        while True:
            line = self.recorded_session.next()
            i+=1
            prefix, user_input = self.split_prefix(line)
            if prefix:
                if prefix.startswith("?!") or not prefix.startswith("?"):
                    if user_input.lstrip().startswith("assert"):
                        _assertion = self.Assertion()
                        _assertion.SrcLine = i
                        _assertion.DestLine = self.line_count
                        _assertion.Text = user_input
                        self.assertions.append(_assertion)

                yield prefix, user_input

                if _assertion:
                    try:
                        if sys.last_value == _assertion.last_exc:
                            _assertion.Status = "OK"
                        else:
                            _assertion.Status = "ERROR"
                    except AttributeError:
                        if _assertion.last_exc:
                            _assertion.Status = "ERROR"
                        else:
                            _assertion.Status = "OK"

                _assertion = None
            else:
                continue

    def at_exit(self):
        super(EEReplayConsoleTest, self).at_exit()
        if self.assertions:
            self.print_result()

class EERecordedReplayConsole(EERecordedConsole, EEReplayConsole):
    def __init__(self, *args, **kwd):
        super(EERecordedConsole, self).__init__(*args, **kwd)
        super(EEReplayConsole, self).__init__(*args, **kwd)
        self.user = ReplayedRecordedUser(self.session_protocol, self.report)

    class ReplayedRecordedUser(User):
        def __init__(self, session_protocol, report):
            self.session_protocol = session_protocol
            self.get_input = self.get_input_from_protocol

        def get_input_from_protocol(self, prompt):
            try:
                prefix, user_input = self.session_protocol.next()
                if prefix.startswith("?"):
                    self.get_input = self.get_raw_user_input
                    self.report.write(prefix)
                    return self.get_raw_user_input(prefix[1:])
                self.report.write(prefix+user_input+"\n")
                return user_input
            except StopIteration:
                raise SystemExit

        def get_raw_user_input(self, prompt):
            text = raw_input(prompt)
            self.report.write(text+"\n")
            if text.strip() == "!":
                self.get_input = self.get_input_from_protocol
                return self.get_input_from_protocol(prompt)
            return text


    def __init__(self, fiber, name, *args, **kwd):
        self.report = open(path(fiber.__file__).dirname()+os.sep+"fibercon"+os.sep+"con_"+name+".eerp","w")
        self.recorded_session = file(self.fiber.options["session"])
        super(EERecordingConsole, self).__init__(fiber, name, *args, **kwd)
        self.user = self.ReplayedRecordedUser(self.report)


