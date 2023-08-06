import EasyExtend
import EasyExtend.eecommon as eecommon


if __name__ == '__main__':
    import lexdef
    need_lex_nfa, need_parse_nfa = eecommon.load_symbols(lexdef.__file__)
    from conf import*
    (options,args) = opt.parse_args()
    import langlet
    langlet.options  = options.__dict__
    eecommon.load_nfas(langlet, need_lex_nfa, need_parse_nfa)
    if args:
        langlet.options["start_module"] = args[-1]
        py_module = args[-1]
        EasyExtend.run_module(py_module, langlet)
    else:
        console = EasyExtend.create_console(langlet_name, langlet)
        console.interact()
