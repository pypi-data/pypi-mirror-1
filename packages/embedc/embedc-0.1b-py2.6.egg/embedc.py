import inspect
import os
import sys
import parser
from ctypes import *
import _ctypes
import stat
import tempfile
import subprocess
import platform
import re

# GLOBALS
#
# Dictionary with list of files that have been "compiled"
processed = {}

# Dictionary that holds pointers to function names in a DLL/SO 
# corresponding to source file/line number
savefunc = {}

# hash of CDLL objects for each source file
mylib = {}

# other global variables are scattered through the code where they are need. 
# In addition, there is some initilization at the end

#
# class deletes temporary DLL/SO files. Unfortunately, ctypes has functions 
# for loading DLL/SOs, but not for unloading them. Thus deletion must 
# occur at program termination.
#
class AutoCleanup:
    def __init__(self):
        self.files = []
        self.unloadlib = []
    def add(self, file):
        self.files.append(file)
    def unload(self, dll):
        self.unloadlib.append(dll)
    def __del__(self):
        for file in self.files:
            try:
                os.remove(file)
            except:
                continue
        del self.files
        for dll in self.unloadlib:
            try:
                _unload_library(dll)
            except:
                continue
        del self.unloadlib
        
_cleanup = AutoCleanup()

def _unload_library(tdll):
    if windows:
        cdll.kernel32.FreeLibrary(tdll._handle)
    else:
        libdl = CDLL("libdl.so")
        libdl.dlclose(tdll._handle)

#
# this class and _savelocals function access internal Python objects to 
# save the local variables. This code is delicate. If the structure changes
# it could crash python
#        
class _CPyFrame(Structure):
    pass   
_CPyFrame._fields_ = [
                 ("refcount", c_int),
                 ("p_objtype", c_void_p),
                 ("size", c_int),
                 ("p_back", POINTER(_CPyFrame))
                ]
                
def _is_CPyFrame_bad(frameptr):
    if frameptr is None or frameptr == 0:
        raise SaveLocalsError("PyEval_GetFrame() frame pointer is NULL")       
    try:
        if frameptr[0].refcount > 10 or frameptr[0].refcount < 1:
            raise SaveLocalsError("PyEval_GetFrame() refcount too large or small (count=%d)" % frameptr[0].refcount)
    except:
        raise SaveLocalsError("PyEval_GetFrame() frame is invalid or empty")
    if frameptr[0].size > 50 or frameptr[0].size < 0:
        raise SaveLocalsError("PyEval_GetFrame() frame is too large or small, possibly invalid (size=%d)" % frameptr[0].size)
    return False

class SaveLocalsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
def _savelocals(frame, testmode=0):
    if frame is None:
        raise SaveLocalsError("Frame passed to _savelocals is None")
    # count frames we have to go back, up to 10 levels
    found = -1
    testframe = inspect.currentframe()
    for i in range(10):
        testframe = testframe.f_back
        if testframe is frame:
            found = i+1
            break
    # if we haven't found our frame, there's a big problem but for now
    # we don't deal with it
    if found<0:
        raise SaveLocalsError("Could not find context frame while saving local variables")
    else:
        # get current frame into our structure
        try:
            if testmode == 1: api = pythonapi.PyEval_GetFrameXYZ
            api = pythonapi.PyEval_GetFrame
        except AttributeError:
            raise SaveLocalsError("Could not find PyEval_GetFrame() function")
            
        api.restype = POINTER(_CPyFrame)
        frameptr = api()
        if testmode == 2: frameptr = None
        if testmode >= 3:
            frameptr = [_CPyFrame()]
            if testmode == 4: frameptr[0].refcount = 50000
            if testmode == 5: 
                frameptr[0].refcount = 1
                frameptr[0].size = 10000
        
        # now some sanity checks to prevent a hard crash in case the structure has changed
        _is_CPyFrame_bad(frameptr)

        # now loop as many times as we have to go back
        for i in range(found):
            frameptr = frameptr[0].p_back
            _is_CPyFrame_bad(frameptr)
        pythonapi.PyFrame_LocalsToFast(frameptr, 0)
    return True

class CodeFragment:
    funcname = "func"
    sourcecode = [""]
    arguments = []
    variables = []
    rettype = ""
    prefunc = []
    postfunc = []
    lineno = 0
    gcc = ""
    inline = False
        
    def type2c(self, t):
        if t == "string" or t == "str":
            typ = "char*"
        elif t == "ustring" or t == "ustr":
            typ = "wchar_t*"
        else:
            typ = "%s" % t
        return typ
        
    def write_func(self, fpo, pfuncname=""):
        if pfuncname != "":
            funcname = pfuncname
        arglist = []
        for i in range(len(self.arguments)):
            arglist.append(self.type2c(
                self.arguments[i])+" "+self.variables[i])
        fpo.write("\n".join(self.prefunc))
        fpo.write("\nextern \"C\" {\n")
        if self.inline:
            fpo.write("%s %s(%s) {" % 
                (self.type2c(self.rettype), self.funcname, ",".join(arglist)))
        fpo.write("\n".join(self.sourcecode))
        if self.inline:
            fpo.write("}\n")
            fpo.write("void %s_post() {\n" % self.funcname)
            fpo.write("\n".join(self.postfunc))
            fpo.write("}\n")
        fpo.write("}  //extern C\n")
        fpo.write("\n")
        return self.funcname

    def _clean_up_import_line(self, line):
        line = re.sub(r'\[\]', '*', line)
        line = re.sub(r'\&\s+', ' &', line)
        line = re.sub(r'\s+\*', '* ', line)
        line = re.sub(r'\*\&', '* &', line)
        return line
        
    def parse_embed_code(self, plineno, source, pinline):
        self.importall = False
        self.arguments = []
        self.variables = []
        self.sourcecode = [""]
        self.prefunc = [
            "#include <string.h>",
            "#include <stdio.h>",
            "#include <stdlib.h>"]
        self.postfunc = []
        self.rettype = "int"
        self.gcc = ""
        self.inline = pinline
        self.lineno = plineno
        
        importspec = False
        
        for line in source:
            try:
                directive = line.strip().split()[0]
            except IndexError:
                continue
            
            if directive.startswith("#"):
                self.prefunc.append(line)
                continue
            if directive == "GLOBAL":
                exp = line.replace("GLOBAL","", 1)
                self.prefunc.append(exp)
                continue
            if directive == "CC":
                self.gcc = line.replace("CC","", 1)
                continue
            if directive == "IMPORTALL":
                self.importall = True
                continue
            if directive == "IMPORT":
                importspec = True
                (cmd, type, var) = self._clean_up_import_line(line).split()
                self.arguments.append(type)
                self.variables.append(var.replace(";",""))
                continue
            if directive == "RETURN":
                line = re.sub(r'\s*RETURN\s+', '', line)
                (rtype, stxt, exp) = line.partition(' ')
                self.rettype = rtype.strip()
                self.sourcecode.append("return %s;" % exp.strip())
                continue
            if directive == "POST":
                exp = line.replace("POST","", 1)
                self.postfunc.append(exp)
                continue
            self.sourcecode.append(line)
            
        # if there's no IMPORT line, import all variables
        if importspec == False and self.importall == False:
            self.importall = True
            
        return True

        
class CodeFile:
    def need_reload(self, file):
        s1 = os.stat(file)
        dll = _get_dll_name(file)
        try:
            s2 = os.stat(dll)
        except:
            return True
        if s1.st_mtime > s2.st_mtime:
            return True
        return False

    def parse_file(self, file):
        funcnum = 0
        newer = self.need_reload(file)
        comp = EmbedCompile()
        gcc = ""
        if newer:
            fpo = open("%s.cpp" % file, "w")
            fpo.write("//%s\n" % file)
        for code in self.parse_file_next(file):
            funcnum+=1
            code.funcname = "func_%d" % funcnum
            savefunc[(file, code.lineno)] = code
            gcc = code.gcc
            if newer:
                code.write_func(fpo)
        if newer:
            fpo.close()
            comp.compile(file, gcc)
        global mylib
        if file not in mylib:
            self._load_file_into_library(file)
            
    def _load_file_into_library(self, file):
            dll = _get_dll_name(file)
            cdll.LoadLibrary(dll)
            mylib[file] = CDLL(dll)
            _cleanup.unload(mylib[file])

    def parse_file_next(self, file):
        fp = open(file, "r")
        lineno=0
        infunc = False
        inline = False
        for line in fp:
            lineno += 1
            if line.find("inline_c_precompile(\"\"\"")>=0:
                infunc = True
                inline = True
                funcx = []
                continue
            if line.find("embed_c_precompile(\"\"\"")>=0:
                infunc = True
                inline = False
                funcx = []
                continue
            if infunc:
                if line.find("\"\"\"")>=0:
                    code = CodeFragment()
                    code.parse_embed_code(lineno, funcx, inline)
                    yield code
                    infunc = False
                    inline = False
                else:
                    funcx.append(line.rstrip())

def _type2ctype(t, ev=False):
    if t == "string":
        typ = "c_char_p"
    elif t == "ustring":
        typ = "c_wchar_p"
    else:
        typ = "c_%s" % t
    if ev:
        return eval(typ)
    else:
        return typ

def inline_c_precompile(source):
    """Precompile C/C++ code and run it in-line"""
    fr = inspect.currentframe().f_back
    (lib, code) = _load_func(fr)
    return _call_func(lib, code, fr)

def inline_c(source):
    """Compile at runtime and run code in-line"""
    return _embed_or_inline_c(source, True)
    
def embed_c_precompile(source):
    """Precompile function definitions and load the code, but don't execute"""
    fr = inspect.currentframe().f_back
    (lib, source) = _load_func(fr)
    return lib

def embed_c(source):
    """Compile at runtime function definitions and load the code, but don't execute"""
    return _embed_or_inline_c(source, False)

def _embed_or_inline_c(source, inline):
    """Compile at runtime function definitions and load the code, but don't execute"""
    code = CodeFragment()
    compile = EmbedCompile()
    code.parse_embed_code(0, source.split("\n"), inline)
    fr = inspect.currentframe().f_back.f_back
    _import_all_vars(code, fr)
    (dll, func) = compile.temp_compile(code)
    tdll = cdll.LoadLibrary(dll)
    _cleanup.unload(tdll)
    if inline:
        r = _call_func(tdll, code, fr)
        return r
    return tdll

# Getting frame info is slow on Windows
def _get_source(fr):
    lineno = inspect.getframeinfo(fr)[1]
    sourcepath = os.path.abspath( inspect.getsourcefile( fr.f_code ) )
    return sourcepath, lineno
    
def _load_func(fr):
    (sourcepath, lineno) = _get_source(fr)
    _load_func_parse(sourcepath)
    lib = mylib[sourcepath]
    code = savefunc[sourcepath, lineno]
    return lib, code

def _load_func_parse(sourcepath):    
    global processed
    if sourcepath not in processed:
        CodeFile().parse_file(sourcepath)
        processed[sourcepath] = True

_ustringtype = None
        
def _isunicode(text):
    # test python 2.6 & 3.0
    global _ustringtype
    if _ustringtype is None:
        try:
            _ustringtype = unicode  # fails on 3.0+
        except NameError:
            _ustringtype = type('')
        
    if type(text) is _ustringtype:
        return True
    else:
        return False

def _is_in_list(L, value):
    try:
        i = L.index(value)
        return True
    except ValueError:
        return False

def _import_all_vars_dict(code, varlist):
    for k, v in varlist.items():
        if k.startswith("_"):
            continue
        if _is_in_list(code.variables, k):
            continue
        tt = v.__class__.__name__
        ex1 = ""
        ex2 = ""
        if tt == "list" or tt == "tuple":
            ex1 = "*"
            if len(v)>0:
                tt = v[0].__class__.__name__
            else:
                tt = "int"
        else:
            ex2 = "&"
        
        if tt == "str":
            tt = "string"
        else:
            try:
                eval("c_%s()" % tt)
            except:
                continue
        code.arguments.append(tt+ex1)
        code.variables.append(ex2+k)
        
def _import_all_vars(code, frame):        
    if code.importall:
        _import_all_vars_dict(code, frame.f_locals)
        _import_all_vars_dict(code, frame.f_globals)
        
def _call_func(dll, code, fr):
    f = getattr(dll, code.funcname)
    f.argtypes = []
    f.restype = _type2ctype(code.rettype, True)
    value = []
    unicodetype = []
    local = []
        
    for v in range(len(code.variables)):
        if code.variables[v].find("&") >= 0:
            ref = True
            varname = code.variables[v].replace("&","")
        else:
            ref = False
            varname = code.variables[v]

        vardata = 0
        islocal = False
        try:
            vardata = fr.f_locals[varname]
            islocal = True
        except:
            vardata = fr.f_globals[varname]

        value.append(vardata)
        local.append(islocal)
        unicodetype.append(_isunicode(vardata))
        
        if code.arguments[v].endswith("*"):
            tt = code.arguments[v].rstrip("*")
            f.argtypes.append(POINTER(_type2ctype(tt, True) * len(value[v])))
            if type(value[v]) is not _type2ctype(tt, True):
                str = "(%s * %d)(*value[v])" % (_type2ctype(tt), len(value[v]))
                value[v] = eval(str)
            continue        
        if ref:
            f.argtypes.append(_type2ctype(code.arguments[v], True))
            if type(value[v]) is not _type2ctype(code.arguments[v], True):
                value[v] = eval("byref(%s(value[v]))" % _type2ctype(code.arguments[v]))
            else:
                value[v] = byref(value[v])
            continue
        f.argtypes.append(_type2ctype(code.arguments[v], True))
        value[v] = eval("%s(value[v])" % _type2ctype(code.arguments[v]))
        
    r = f(*value)
    
    localmodify = False
    
    for v in range(len(code.variables)):
        if code.variables[v].find("&") >= 0:
            varname = code.variables[v].replace("&","")
            val = value[v]._obj.value
            if not _isunicode(val) and unicodetype[v]:
                val = val.decode('ascii')
            if local[v]:
                fr.f_locals[varname] = val
                _savelocals(fr)
            else:
                fr.f_globals[varname] = val
        if code.arguments[v].endswith("*"):
            varname = code.variables[v]
            vals = []
            for i in value[v]:
                vals.append(i)
            if local[v]:
                if not _is_tuple(fr.f_locals[varname]):
                    fr.f_locals[varname] = vals
                    _savelocals(fr)
            else:
                if not _is_tuple(fr.f_globals[varname]):
                    fr.f_globals[varname] = vals
    
    if code.rettype == "string":
        r = r.decode('ascii')
        
    f = getattr(dll, "%s_post" % code.funcname)
    if f is not None:
        f()
    return r
    
def _is_tuple(x):
    if type(x) is type(()):
        return True
    return False

def _get_dll_name(file):
    return "%s.cpp.%s" % (file, dllext)

    
class EmbedCompileError(Exception):
    def __init__(self, value, ret, gcc, options, output):
        self.value = value
        self.gcc = gcc
        self.options = options
        self.output = output
    def __str__(self):
        return repr([self.value, self.gcc, self.options, self.output])

    
class EmbedCompile:
    def testgcc(self, cmd="gcc", opt="--version"):
        try:
            (ret, output) = self.run_capture([cmd, opt])
        except:
            raise
        if ret == 0:
            return True
        raise EmbedCompileError("GCC not configured", ret, cmd, opt, output)

    def run_capture(self, command):
        (out, filepath) = tempfile.mkstemp(".log")
        try:
            p = subprocess.Popen(command, stdout=out, stderr=out)
            ret = p.wait()
        except:
            try:
                os.close(out)
                os.remove(filepath)
            except:
                pass
            raise
            
        os.close(out)
        fp = open(filepath, "r")
        output = fp.readlines()
        fp.close()
        os.remove(filepath)
        return (ret, output)

    def compile(self, file, gcc):
        cpp="%s.cpp"%file
        lib = _get_dll_name(file)
        return self.compile_file(cpp, lib, gcc, True)

    def compile_file(self, filename, lib, gcc="", wipe=False):
        parms = ["gcc", "-fPIC", "-lstdc++", "-shared", "-o", lib, filename]
        (ret, output) = self.run_capture(parms)
        if ret == 0:
            if wipe:
                os.remove(filename)
            return lib
        else:            
            raise EmbedCompileError(filename, ret, parms[0], parms, output)
        
    def temp_compile(self, code):
        (fp, filename) = tempfile.mkstemp(".cpp")
        fpo = os.fdopen(fp, "w")
        funcname = "func"
        code.write_func(fpo, funcname)
        fpo.close()
        lib = "%s.%s" % (filename, dllext)
        self.compile_file(filename, lib, code.gcc, True)
        _cleanup.add(lib)
        return lib, funcname

        
if platform.system() == "Linux":
    windows = False
    dllext = "so"
else:
    windows = True
    dllext = "dll"

EmbedCompile().testgcc()