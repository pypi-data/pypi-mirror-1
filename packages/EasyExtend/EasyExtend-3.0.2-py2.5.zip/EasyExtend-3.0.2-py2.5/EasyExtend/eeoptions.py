import EasyExtend.eecommon as eecommon
import os

class EEShow(object):
    '''
    EEShow is an abstract base class. It provides
    '''

    @classmethod
    def show_tokenstream(cls, langlet, tokenstream):
        class Report:
            Line = " %-6s|"
            Columns = " %-8s|"
            TokenValue = " %-20s|"
            TokenId = " %-13s|"
            TokenIdName = " %-14s|"

            def __init__(self):
                self.items = {"Line":" ",
                              "Columns":" ",
                              "TokenValue":" ",
                              "TokenId":" ",
                              "TokenIdName":" "}

            def insert(self, name, value):
                self.items[name] = value

            def write(self):
                print "".join([Report.Line%self.items["Line"],
                        Report.Columns%self.items["Columns"],
                        Report.TokenValue%self.items["TokenValue"],
                        Report.TokenIdName%self.items["TokenIdName"],
                        Report.TokenId%self.items["TokenId"]]
                        )

        print "----------------------------------------------------------------------."
        print " Line  | Columns | Token Value         | Token Name    | Token Id     |"
        print "-------+---------+---------------------+---------------+--------------+"

        for item in tokenstream:
            r = Report()
            try:
                tid = item[0]
                r.insert("TokenId", str(tid)+" -- "+str(tid%512))
                r.insert("TokenIdName", langlet.token.tok_name[tid])
            except KeyError:
                pass
            if item[1] == "\n":
                r.insert("TokenValue","'\\n'")
            elif item[1] == "\t":
                r.insert("TokenValue","'\\t'")
            elif item[1] == "\r":
                r.insert("TokenValue","'\\r'")
            elif item[1] == "\\\n":
                r.insert("TokenValue","'\\'")
            else:
                r.insert("TokenValue",r"'%s'"%item[1])
            if isinstance(item[2], tuple):
                r.insert("Line",item[2][0])
                r.insert("Columns",str(item[2][1])+"-"+str(item[3][1]))
            else:
                r.insert("Line",item[2])
                r.insert("Columns",str(item[3][0])+"-"+str(item[3][1]))
            r.write()
        print "----------------------------------------------------------------------'"


    def maybe_show_token(self, source, filename = None):
        """
        Used to show token-stream created by tokenizer. Call depends on show_token option -t.
        @param source: source string to be tokenized
        @param filename: if filename is available the source is read from a file.
        """
        if self.options.get("show_token"):
            show_scan = self.options.get("show_scan")
            self.options["show_scan"] = False
            import cst2source
            if filename:
                source = file(filename).read()
            deb_tokenizer   = eecommon.load_tokenizer(self.langlet)
            tokenized = deb_tokenizer.tokenize_string(source)
            print "[token>"
            self.show_tokenstream(self.langlet, tokenized)
            print "<token]"
            print
            self.options["show_scan"] = show_scan



    def maybe_show_cst_before(self, cst):
        """
        Used to show CST created by the parser *before* transformation. Call depends on show_cst_before option -b.
        @param cst: cst to be printed.
        """
        if self.options.get("show_cst_before"):
            short_form = not self.options.get("full_cst")
            marked = []
            marked_nodes = self.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print "[cst-before>"
            self.langlet.pprint(cst, mark = marked, stop = False, short_form = short_form)
            print "<cst-before]"

    def maybe_show_cst_after(self, cst):
        """
        Used to show CST created by the parser *after* transformation. Call depends on show_cst_after option -a.
        @param cst: cst to be printed.
        """
        if self.options.get("show_cst_after"):
            short_form = not self.options.get("full_cst")
            marked = []
            marked_nodes = self.options.get("show_marked_node")
            if marked_nodes:
                marked = marked_nodes.split(",")
            print "[cst-after>"
            self.langlet.pprint(cst, mark = marked+["> MAX_PY_SYMBOL"], stop = False, short_form = short_form)
            print "<cst-after]"


    def maybe_show_python(self, cst):
        """
        Used to show Python source code generated transformed cst. Call depends on show_token option -p.
        @param cst: cst to be unparsed.
        """
        if self.options.get("show_python"):
            print "[python-source>"
            if isinstance(cst, basestring):
                print cst
            else:
                print self.langlet.unparse(cst)
            print "<python-source]"

    def maybe_grammar_check(self, cst):
        """
        Used to show Python source code generated transformed cst. Call depends on show_token option -p.
        @param cst: cst to be unparsed.
        """
        if self.options.get("cst_validation"):
            from csttools import check_node
            import EasyExtend.langlets.zero.langlet as zero
            print "[cst-validation-test>"
            check_node(cst, zero)
            print "<cst-validation-test]"

    def maybe_show_scan(self, scan):
        """
        show unfiltered token stream passed to the lexical post processor
        @param scan: list of token
        """
        if self.options.get("show_scan"):
            import pprint
            print "[show-unfiltered-scan>"
            pprint.pprint(scan)
            print "<show-unfiltered-scan]"


import optparse

def record_rec_seen(option, opt_str, value, parser):
    if parser.rargs:
        v = parser.rargs[0] # consume the value
        if v.startswith("-"):
            setattr(parser.values, option.dest, "rec")
            return
        if v !="enum" and not os.sep in v and not v.startswith("+") and not v.endswith("+"):
            raise optparse.OptionValueError("value of --rec must be one of 'enum', '+<suffix>', '<prefix>+' or a filename of the form %s<filename>"%os.sep)
        setattr(parser.values, option.dest, v)
        del parser.rargs[:]
    else:
        setattr(parser.values, option.dest, "stdname")  # use stdname as default
                                                        # when option is set
def getoptions():
    opt = optparse.OptionParser()
    opt.add_option("-b","--show_cst_before" ,dest="show_cst_before" ,help="show CST before transformation", action="store_true" )
    opt.add_option("-a","--show_cst_after" ,dest="show_cst_after" ,help="show CST after transformation",action="store_true")
    opt.add_option("-m","--show_marked_node" ,dest="show_marked_node" ,help="mark one or more different kind of nodes in CST",action="store", type = "string")
    opt.add_option("-t","--show_token",dest="show_token", help="show filtered token stream passed to the parser", action="store_true" )
    opt.add_option("--show-scan",dest="show_scan", help="show unfiltered token stream passed to the lexical post processor", action="store_true" )
    opt.add_option("-p","--show_python",dest="show_python", help="show translated Python code", action="store_true" )
    opt.add_option("-v","--cst-validation",dest="cst_validation", help="CST validation against Python grammar", action="store_true" )
    opt.add_option("--re-compile",dest="re_compile", help="re compilation module even if *.pyc is newer than source", action="store_true" )
    opt.add_option("--re-compile-all",dest="re_compile_all", help="re compilation all modules even if *.pyc is newer than source", action="store_true" )
    opt.add_option("--parse-only",dest="parse_only", help="terminate after parsing file", action="store_true" )
    opt.add_option("--full-cst",dest="full_cst", help="display complete CST", action="store_true" )
    opt.add_option("--rec", dest = "recording", help="use recording console to record interactive session", action="callback", callback=record_rec_seen)
    opt.add_option("--rep",dest="session", help="replays an interactive session", action="store", type = "string" )
    opt.add_option("--dbg-lexer",dest="debug_lexer", help="displays debug information for lexer run", action="store_true" )
    opt.add_option("--dbg-parser",dest="debug_parser", help="displays debug information for parser run", action="store_true" )
    opt.add_option("--dbg-import",dest="debug_importer", help="displays debug information for importer run", action="store_true" )
    opt.add_option("--small-expansion",dest="small_expansion", help="expands NFA not fully which might take very long", action="store_true" )
    opt.add_option("--build-nfa",dest="build_nfa", help="(re)builds lex_nfa and parse_nfa files", action="store_true" )
    return opt



