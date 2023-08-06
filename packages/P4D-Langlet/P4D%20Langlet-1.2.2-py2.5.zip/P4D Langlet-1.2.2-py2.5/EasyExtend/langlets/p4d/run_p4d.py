import EasyExtend
import EasyExtend.eecommon as eecommon
from EasyExtend.util.path import path

def convert2p4d(langlet, input_file):
    if langlet.options["flex"]:
        import EasyExtend.eeimporter as eeimporter
        flexutils = eeimporter.import_from_langlet(langlet, "EasyExtend.langlets.p4d.flexutils")
        flexutils.convert2p4d(langlet, input_file)
    else:
        out, ext = input_file.splitext()
        out = out+".p4d"
        if ext in (".htm", ".html"):
            p4d_str = langlet.P4D.from_html(open(input_file).read()).p4dstr()
        else:
            p4d_str = langlet.P4D.from_xml(open(input_file).read()).p4dstr()
        open(out,"w").write("elm "+p4d_str)

def runflex(langlet, input_file):
    import EasyExtend.eeimporter as eeimporter
    flexutils = eeimporter.import_from_langlet(langlet, "EasyExtend.langlets.p4d.flexutils")
    flexutils.runflex(langlet, input_file)

def autorun():
    import lexdef
    need_lex_nfa, need_parse_nfa = eecommon.load_symbols(lexdef.__file__)
    exec "from conf import*"
    (options,args) = opt.parse_args()
    import langlet
    langlet.options  = options.__dict__
    eecommon.load_nfas(langlet, need_lex_nfa, need_parse_nfa)
    if langlet.options["p4d_kwd"]:
        langlet.P4D.prefix_kwd = True
    if langlet.options["xml2p4d"]:
        f = path(args[-1])
        if not f.isfile():
            import os
            if f[0] == '*':
                ext = f.splitext()[1]
                for fl in path(os.getcwd()).listdir():
                    if fl.ext == ext:
                        convert2p4d(langlet, fl)
                return
            else:
                f = path(os.getcwd()).joinpath(f)
        convert2p4d(langlet, f)
        return
    elif langlet.options["flex"]:
        f = path(os.getcwd()).joinpath(path(args[-1]))
        runflex(langlet, f)
        return

    elif args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, langlet)
    else:
        console = EasyExtend.create_console(langlet_name, langlet)
        console.interact()

if __name__ == '__main__':
    autorun()
