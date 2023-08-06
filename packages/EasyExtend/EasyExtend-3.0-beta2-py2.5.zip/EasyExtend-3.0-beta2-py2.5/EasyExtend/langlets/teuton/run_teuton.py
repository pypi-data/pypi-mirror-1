import EasyExtend
import EasyExtend.eecommon as eecommon

if __name__ == '__main__':
    import lexdef
    import sys
    need_lex_nfa, need_parse_nfa = eecommon.load_symbols(lexdef.__file__)
    from conf import*
    (options,args) = opt.parse_args()
    import langlet
    langlet.replaced_by_teuton()
    sys.stdout = langlet.File(sys.stdout)
    langlet.options  = options.__dict__
    langlet.options["assert"] = "behaupte"
    eecommon.load_nfas(langlet, need_lex_nfa, need_parse_nfa)
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, langlet)
    else:
        console = EasyExtend.create_console("Teuton", langlet)
        console.interact()
