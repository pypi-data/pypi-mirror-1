# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

#
#  Import mechanism for library packages
#
#
#  Terminology:
#
#      A file with with specified source file extension is "langletsource".
#      A file with a source extension is "source".
#      A file with a compiled extension is "compiled".
#      A file is "accepted" when accept_module returns self.
#
#  Conventions:
#      Use the prefix 'mpth_' when a dotted module path A.B. .. .M is mentioned.
#      Use the prefix 'fpth_' when an operating system path A/B/../M.ext is mentioned.
#
#  Strategy:
#     Compilation:
#         let f be a module_path returned by find_module.
#
#         If f is source, compile f.
#         If f is compiled return f.
#
#     Search:
#         let f1,f2 be module paths and s1 = stat(f1)[-2], s2 = stat(f1)[-2].
#
#         if f1 is source and compile is enforced, return f1.
#         elif f1 is source and s2 < s1, return f1
#         else return f2
#


import sys
import EasyExtend.eecompiler as eecompiler
import EasyExtend.exotools as exotools
from EasyExtend.util.path import path
import os
import imp
import zipimport

import ihooks

class LangletHooks(ihooks.Hooks):
    def __init__(self, langlet):
        ihooks.Hooks.__init__(self)
        self.langlet = langlet
        self._search_suffixes()

    def _search_suffixes(self):
        self.suffixes = list(ihooks.Hooks.get_suffixes(self))
        for (ext, code, prio) in self.suffixes:
            if self.langlet.compiled_ext == ext:
                break
        else:
            self.suffixes.insert(0,(self.langlet.compiled_ext, 'rb', 2))

        for (ext, code, prio) in self.suffixes:
            if self.langlet.source_ext == ext:
                break
        else:
            self.suffixes.insert(1,(self.langlet.source_ext, 'U', 1))

    def get_suffixes(self):
        return self.suffixes


class EEModuleLoader(ihooks.ModuleLoader):

    def is_source(self, file):
        for info in self.hooks.get_suffixes():
            if file.endswith(info[0]):
                if info[-1] == 1:
                    return True
                else:
                    return False
        return False

    def find_module_in_dir(self, name, dir, allow_packages=1):
        if dir is None:
            return self.find_builtin_module(name)
        if allow_packages:
            if dir.endswith(".egg"):
                try:
                    zipimporter = zipimport.zipimporter(dir)
                    return zipimporter.find_module(name)
                except zipimport.ZipImportError:
                    return

            fullname = self.hooks.path_join(dir, name)
            if self.hooks.path_isdir(fullname):
                # path suffix might be .py for arbitrary langlets
                suffixes = self.hooks.get_suffixes()
                suffixes.append(('.py', 'U', 2))
                stuff = self.find_module_in_dir("__init__", fullname, 0)
                # drop .py suffix again. If langlet source suffix is .py
                # it was redundant anyway
                suffixes.pop()
                if stuff:
                    f = stuff[0]
                    if f:
                        f.close()
                    return None, fullname, ('', '', ihooks.PKG_DIRECTORY)
        f = ()
        for info in self.hooks.get_suffixes():
            suff, mode, typ = info
            fullname = self.hooks.path_join(dir, name+suff)
            if self.hooks.path_isfile(fullname):
                if self.hooks.langlet.options.get("re_compile"):
                    if self.is_source(fullname):
                        f = (0, fullname, mode, info )
                        break
                dt = os.stat(fullname)[-2]
                if f:
                    if f[0] < dt:
                        f = (dt, fullname, mode, info )
                else:
                    f = (dt, fullname, mode, info )
        if f:
            try:
                fp = self.hooks.openfile(f[1], f[2])
                return fp, f[1], f[-1]
            except self.hooks.openfile_error:
                pass
        return None

    def find_module(self, name, path = None):
        if path is None:
            path = [None] + self.default_path()
        for dir in path:
            stuff = self.find_module_in_dir(name, dir)
            if stuff:
                return stuff
        return None


class Importer(object):
    no_import = set(["langlet.py", "conf.py", "__init__.py", ])

    def __init__(self, langlet):
        '''
        Adapted importer.
        @param langlet: langlet module object
        '''
        self.langlet      = langlet
        self.eec          = self.langlet_compiler()
        self.options      = langlet.options
        self.fpth_langlet = self.langlet_path()
        self.fpth_mod     = None
        self.loader       = self.module_loader()
        self.dbg          = langlet.options.get("debug_importer")


    def pre_filter(self, fpth_mod):
        if not path(fpth_mod).ext == u".py":
            return True
        fpth_dir = path(fpth_mod.lower()).dirname()
        if fpth_dir.basename() in ("lexdef", "parsedef", "EasyExtend"):
            return False
        if fpth_mod.basename() not in self.__class__.no_import:
            return True
        return True

    def langlet_path(self):
        return path(self.langlet.__file__).dirname()

    def langlet_compiler(self):
        return eecompiler.EECompiler(self.langlet)

    def module_loader(self):
        return EEModuleLoader(hooks = LangletHooks(self.langlet))

    def is_langletmodule(self, fpth_m):
        return fpth_m.endswith(self.langlet.source_ext) or fpth_m.endswith(self.langlet.compiled_ext)

    def register_importer(self):
        pth = str(self.fpth_langlet)
        if pth not in sys.path:
            sys.path.append(pth)
        sys.path_importer_cache.clear()
        if self not in sys.meta_path:
            sys.meta_path.append(self)

    def accept_module(self, fpth_mod):
        '''
        Method used to determine if a langlet accepts module for langlet-specific import.
        @param fpth_mod: a path object specifying the complete module path.
        '''
        if not self.is_langletmodule(fpth_mod):
            return
        #if self.langlet.source_ext == '.py':
        #    return
        if self.dbg:
            sys.stdout.write("dbg-importer: accept_module:`%s`\n"%fpth_mod)
        return self

    def find_module(self, mpth_mod, mpth_pack = None):
        if mpth_pack and ".egg" in mpth_pack[0]:  # TODO - enable zipimport of langlet modules
            return
        package = ""
        idx = mpth_mod.rfind(".")  # maybe dotted package name ?
        if self.dbg:
            sys.stdout.write("dbg-importer: find_module: input: `%s`\n"%mpth_mod)
        if idx>0:
            package, mpth_mod = mpth_mod[:idx], mpth_mod[idx+1:]
            mpth_pack = sys.modules[package].__path__
        moduledata  = self.loader.find_module(mpth_mod, mpth_pack)
        if isinstance(moduledata, zipimport.zipimporter):
            if self.dbg:
                sys.stdout.write("dbg-importer: find_module: zipimport: `%s`\n"%mpth_mod)
            moduledata.load_module(mpth_mod)
            return
        if not moduledata:
            if self.dbg:
                sys.stdout.write("dbg-importer: find_module: no-data: `%s`, `%s`, `%s`\n"%(mpth_mod, package, mpth_pack))
            if mpth_pack:
                raise ImportError("No module named %s found at %s."%(mpth_mod, mpth_pack))
            else:
                raise ImportError("No module named %s found."%mpth_mod)
        if self.dbg:
            sys.stdout.write("dbg-importer: find_module: moduledata: `%s`\n"%(moduledata[1:],))
        self.fpth_mod = path(moduledata[1])
        self.mpth_mod = mpth_mod
        # sys.stdout.write("DEBUG import_path: %s, module: %s\n"%(self.mpth_mod, self.fpth_mod))
        if self.pre_filter(self.fpth_mod):
            mod_obj = self.accept_module(self.fpth_mod)
            return mod_obj


    def load_module(self, fullname):
        mod = self.fpth_mod
        # sys.stdout.write("DEBUG load_module: %s\n"%mod)
        if self.loader.is_source(mod):
            if self.dbg:
                sys.stdout.write("dbg-importer: %s\n"%("-"*(len(mod)+30),))
                sys.stdout.write("dbg-importer: load_module: compile source: `%s`\n"%mod)
                sys.stdout.write("dbg-importer: %s\n"%("-"*(len(mod)+30),))
            self.eec.compile_file( mod )
            compiled_module_path = mod.stripext()+self.langlet.compiled_ext
        else:
            compiled_module_path = mod
        try:
            if self.langlet.exospace.wired:  # TODO: not in use yet
                self.langlet.exospace.dump(fullname, compiled_module_path)
                exotools.move_to_archive(compiled_module_path)
                return self.load_zipped_module(fullname, compiled_module_path)
            else:
                if self.dbg:
                    sys.stdout.write("dbg-importer: load_module: load compiled: `%s`\n\n"%compiled_module_path)
                f = open(compiled_module_path, "rb")
                m_compiled = imp.load_compiled( fullname, compiled_module_path, f )
                return m_compiled
        except AttributeError:
            if self.dbg:
                sys.stdout.write("dbg-importer: load_module: load compiled: `%s`\n\n"%compiled_module_path)
            f = open(compiled_module_path, "rb")
            return imp.load_compiled( fullname, compiled_module_path, f )


def import_from_langlet(langlet, fullname):
    '''
    Function used to import a module of an arbitrary langlet.

    Rationale::
        suppose you want to import a module ipconverter.gal from a Python program.
        This is easy when ipconverter.gal has been compiled already and you have the *.pyc
        file accordingly. However this may not be the case and you have to compile the
        *.gal file separately. This compilation is done on import but you can't import files
        with *.gal extensions from Python!

        The solution to this problem is to import ipconverter.gal from the gallery langlet:

            import EasyExtend.langlets.gallery as langlet
            import_from_langlet(langlet, "<module-path-to-ipconverter>.ipconverter")

    @param langlet: langlet you want to import module from
    @param fullname: a module path
    @return: the compiled and imported module
    '''
    importer = Importer(langlet)
    importer.find_module(fullname)
    return importer.load_module(fullname)

