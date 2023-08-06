'''
Command compiler and console that executes Langlet specific commands.
'''

# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import EasyExtend
import eecommon
import eeoptions
from   eexcept import*
from   EasyExtend.trail.nfaparser import TokenStream, NFAParser
from   csttools import split_file_input, projection
import cst2source
from util.path import path
import sys
import os
import traceback
import re
import __main__
__main__.__dict__["__"] = __main__


COMPILER_FLAGS = PyCF_DONT_IMPLY_DEDENT = 0x200   # ??? some undocumented compiler flag with unkown functionality but effect.

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
        self.nl_count = 2
        self.parse_error = (None, None)

    def at_exit(self):
        raise NotImplementedError

    def try_parse(self):
        raise NotImplementedError

    def compile_cst(self, cst):
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
        self.at_start()
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
                                self.nl_count -=1
                                if self.nl_count == 0:
                                    exc, msg = self.parse_error
                                    self.reset()
                                    more = False
                                    if exc:
                                        raise exc, msg
                                elif not more:
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

    def at_start(self):
        raise NotImplementedError

class EEConsole(ConsoleBase, eeoptions.EEShow):
    '''
    Console object used to handle user input.

    This console object is to some extend a redesign of the InteractiveConsole object of the stdlib.

        - tryParse, compile_cst and runcode are clearly separated from each other and can be adapted
          in subclasses.
        - the interact method is removed from cruft of codeop.py
        - some EE specifific methods are added used show CSTs, token streams and unparsed Python code
    '''
    def __init__(self, langlet,
                       name,
                       locals = None,
                       globals = None,
                       use_new_prompt   = True,
                       source_filter = lambda x:x,
                       **kwd):
        self.user = User()
        self.locals  = __main__.__dict__ if locals is None else locals
        self.langlet = langlet
        self.console_name = name
        self.use_new_prompt = use_new_prompt
        self.line_buffer = []
        self.terminates  = True
        # debug options
        self.options  = langlet.options
        self._compiled = {}
        self.source_filter = source_filter
        self.parse_error = None


    def at_start(self):
        '''
        Method used at console start. Select right prompt and print header.
        '''
        if not self.use_new_prompt:
            return
        if hasattr(self.langlet, "prompt"):
            sys.ps1 = self.prompt = self.langlet.prompt
        else:
            sys.ps1 = self.prompt = ">>> "
        sys.ps2 = "."*(len(self.prompt)-1)+" "
        if hasattr(self.langlet, "docs"):
            docs = self.langlet.docs
        else:
            docs = ""

        py_vers = " On Python %s"%sys.version
        if docs:
            langlet_doc = " Langlet documentation: %s"%docs
        else:
            langlet_doc = " Langlet documentation: not yet available."
        self._header_len =  max(len(py_vers),len(langlet_doc))+2
        print "_"*self._header_len
        print
        print " %s"% self.console_name
        print
        print py_vers
        if docs:
            print langlet_doc
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
        Transforms langlet expr/statement into one or more Python
        statements. Compile and execute those statements.
        @param parseTree: langlet cst
        """
        self.maybe_show_cst_before(parseTree)
        if hasattr(self.langlet, "InteractiveTransformer"):
            transformer = self.langlet.InteractiveTransformer(self.langlet, locals = self.locals)
        else:
            transformer = self.langlet.LangletTransformer(self.langlet)
        transformer.run(parseTree)
        projection(parseTree)
        transformer.terminate()
        self.maybe_show_cst_after(parseTree)
        self.maybe_grammar_check(parseTree)
        sources = []
        for tree in split_file_input(parseTree):
            src = self.langlet.unparse(tree)
            src = self.source_filter(src)
            sources.append(self.langlet.unparse(tree))
        try:
            if self.options.get("parse_only"):
                return # parsed
            for src in sources:
                if not self._compiled.get(src):
                    _code = compile(src,"<input>","single", COMPILER_FLAGS)
                    self._compiled[src] = _code
        finally:
            self.maybe_show_python("\n".join(sources))
        for src in sources:
            self.runcode(self._compiled[src])


    def try_parse(self):
        '''
        Parses eventually incomplete langlet statement.
        Following actions are possible:
        1) Complete langlet statement could be parsed. Parse tree is returned.
        2) Langlet statement incomplete. Needs more user input. Nothing is returned.
        3) Syntax error detected within langlet statement. SyntaxError exception is raised.
        '''
        self.parse_error = (None, None)
        source = '\n'.join(self.line_buffer)+"\n"
        if source in ("quit\n",":quit\n"):  # special commands for console. "quit" is standard in 2.5
            raise SystemExit
        try:
            self.maybe_show_token(source)
            tokenizer = eecommon.load_tokenizer(self.langlet)
            stream    = tokenizer.tokenize_string(source)
            tokstream = TokenStream(stream)
            tokstream.position = 0
        except LexerError, err:
            if err.token[1] in ('\n', ''):
                self.parse_error = (LexerError, err)
                return
            raise
        nfaparser = NFAParser(self.langlet)
        try:
            parseTree = nfaparser.parse(tokstream)
            return parseTree
        except ParserError, err:
            # TODO: this shall be corrected in the presence of individual token
            #       definitions or deactivation of INDENT / DEDENT
            self.parse_error = (ParserError, err)
            tid = err.token[0] % 512
            if tid in (0,4): # NEWLINE or ENDMARKER
                return
            elif tid in (6,) and err.token[1] == '': # DEDENT
                return
            else:
                cls, msg, tb = sys.exc_info()
                raise ParserError, msg, tb
        except TokenError, err:
            return

####################################################################################
#
#  Enhanced console functionality: recording + replay
#
####################################################################################

class LastOutput(object):
    '''
    Stores last output. Used mostly for test purposes.
    '''
    def __init__(self):
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


class EERecordedConsole(EEConsole):
    '''
    EEConsole extension used to record user input.
    '''
    class dual_io:
        '''
        Wraps a standard interface and extend it by a report which is usually a text-log.
        '''
        def __init__(self, console, rep, std):
            self.console = console
            self.report  = rep
            self.std     = std

        def write(self,s):
            self.std.write(s)
            self.report.write(s)
            self.console.last_output.set(s)
            self.console.line_count+=s.count("\n")
            __main__.__ = str(self.console.last_output)

        def readline(self,*size):
            return self.std.readline(*size)

        def flush(self):
            return self.std.flush()

    class RecordedUser(User):
        '''
        Logs all user input and writes it into a report.
        '''
        def __init__(self, report):
            self.report = report

        def get_input(self, prompt):
            text = raw_input(prompt)
            self.report.write(text+"\n")
            return text


    def __init__(self, langlet, name, *args, **kwd):
        super(EERecordedConsole, self).__init__(langlet, name, *args, **kwd)
        self.last_output   = LastOutput()
        self.line_count    = 0
        self.report = self.acquire_session_report(langlet,name,kwd.get("recording"))
        self.additional_header_info = " Creates session report " + path(self.report.name).basename()
        self.user = self.RecordedUser(self.report)

    def _set_dual_IO(self):
        '''
        Replaces sys.stdxxx files by dual_io counterparts.
        '''
        global sys
        sys.stdout   = self.dual_io(self, self.report,sys.stdout)
        sys.stdin    = self.dual_io(self, self.report,sys.stdin)
        sys.stderr   = self.dual_io(self, self.report,sys.stderr)

    def _clear_dual_IO(self):
        '''
        Unwraps dual_io.
        '''
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

    def acquire_session_report(self, langlet, console_name, recording_option):
        pth = path(langlet.__file__).dirname()+os.sep+"reports"
        if recording_option == "enum":
            k = str(len(pth.files("*.ees"))+1)
            f = pth+os.sep+console_name+"_"+k+".ees"
            return file(f,"w")
        elif recording_option.startswith("+"):
            f = pth+os.sep+console_name+"_"+recording_option[1:]+".ees"
            return file(f,"w")
        elif recording_option.endswith("+"):
            f = pth+os.sep+recording_option[:-1]+"_"+console_name+".ees"
            return file(f,"w")
        elif recording_option == "stdname":
            f = pth+os.sep+console_name+".ees"
            return file(f,"w")
        elif recording_option.startswith(os.sep):
            f = pth+recording_option
            return file(f,"w")
        else:
            raise ValueError("Invalid recording option: '%s'"%recording_option)


class EEReplayConsole(EEConsole):

    class recorded_out:
        '''
        Wraps a standard interface and extend it by a report which is usually a text-log.
        '''
        def __init__(self, std, console):
            self.console = console
            self.std     = std

        def write(self,s):
            self.std.write(s)
            self.console.last_output.set(s)
            self.console.line_count+=s.count("\n")
            __main__.__ = str(self.console.last_output)


        def readline(self,*size):
            return self.std.readline(*size)

        def flush(self):
            return self.std.flush()

    class ReplayedUser(User):
        '''
        A ReplayedUser is used to switch between a user input mode and a mode
        where data is read from a session protocol.
        '''
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
                    if user_input:
                        return self.get_raw_user_input(prefix[1:])
                    else:
                        return self.get_raw_user_input(prefix[1:]+" ")
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


    def session(self, file):
        '''
        Line generator. Lines are read from file and file gets closed.
        This way the file can be used within a RecordedReplayedSession which derives
        from a ReplayedSession.
        '''
        lines = file.readlines()
        file.close()
        yield None
        for line in lines:
            yield line


    def __init__(self, langlet, name, *args, **kwd):
        super(EEReplayConsole, self).__init__(langlet, name, *args, **kwd)
        self.last_output   = LastOutput()
        self.line_count    = 0
        self.ees_file     = self.find_recorded_session(langlet,name,kwd.get("session"))
        self.recorded_session = self.session(self.ees_file)
        self.recorded_session.next() # closes report file
        self.additional_header_info = " Replay session " + path(self.ees_file.name).basename()
        self.user = self.ReplayedUser(self.session_protocol())


    def _prepare_prefix(self):
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
        self.prefix_pattern = self._prepare_prefix()


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

    def find_recorded_session(self, langlet, console_name, session):
        pth = path(langlet.__file__).dirname()+os.sep+"reports"
        if os.sep in session:
            return file(session)
        else:
            if session.isdigit():
                f = pth+os.sep+console_name+"_"+session+".ees"
                if f.isfile():
                    return file(f)
            elif session == '_':
                f = pth+os.sep+console_name+".ees"
                if f.isfile():
                    return file(f)
            elif session.startswith("+"):
                f = pth+os.sep+console_name+"_"+session[1:]+".ees"
                if f.isfile():
                    return file(f)
            elif session.endswith("+"):
                f = pth+os.sep+session[:-1]+"_"+console_name+".ees"
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

    def __init__(self, langlet, name, *args, **kwd):
        super(EEReplayConsoleTest, self).__init__(langlet, name, *args, **kwd)
        self.assert_stmts = ["assert"]
        self.assertions   = []
        _assert = langlet.options.get("assert", "assert")
        self.assert_stmt = _assert

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
        print "Status |ees ln |repl ln| Assertion"
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
                    if user_input.lstrip().startswith(self.assert_stmt):
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
        if self.assertions:
            self.print_result()
        super(EEReplayConsoleTest, self).at_exit()


class EERecordedReplayConsole(EEReplayConsoleTest):
    def __init__(self, langlet, name, *args, **kwd):
        super(EERecordedReplayConsole, self).__init__(langlet, name, *args, **kwd)
        self.additional_header_info = " Reuses session report " + path(self.ees_file.name).basename()
        self.user = self.RecordedReplayedUser(self)
        self.user.report = file(self.ees_file.name,"w")
        self.check_prefix_split = False

    def at_exit(self):
        super(EERecordedReplayConsole, self).at_exit()
        self._clear_recorded_output()
        self.user.report.close()

    class RecordedReplayedUser(EEReplayConsole.ReplayedUser):

        def __init__(self, console):
            self.console = console
            EEReplayConsole.ReplayedUser.__init__(self, console.session_protocol())

        def get_raw_user_input(self, prompt):
            text = raw_input(prompt)
            if text.strip() == "!":
                self.get_input = self.get_input_from_protocol
                self.console.check_prefix_split = True
                return self.get_input_from_protocol(prompt)
            self.console.user.report.write(text+"\n")
            return text

    class recorded_out(EEReplayConsole.recorded_out):
        '''
        Wraps a standard interface and extend it
        by a report which is usually a text-log.
        '''

        def write(self,s):
            self.std.write(s)
            if not self.console.check_prefix_split:
                self.console.user.report.write(s)
            else:
                self.console.check_prefix_split = False
                m = self.console.prefix_pattern.match(s)
                if m:
                    prefix = m.group()
                    text = s[len(prefix):].strip()
                    self.console.user.report.write(text+"\n")
            self.console.last_output.set(s)
            self.console.line_count+=s.count("\n")
            __main__.__dict__["__"] = str(self.console.last_output)



