import os, sys
from Pyrex.Utils import replace_suffix
from Pyrex.Compiler.Errors import PyrexError

class CCompilerError(PyrexError):
    pass

def call(args):
    return os.spawnvp(os.P_WAIT, args[0], args)

def c_compile(c_file, verbose_flag=False, cplus=False, obj_suffix=".o"):
    out_file = replace_suffix(c_file, obj_suffix)
    version = sys.version_info[:2]
    args = [cplus and 'c++' or 'cc',
            '-I' + sys.exec_prefix + '/include/python%d.%d/' % version,
            '-fPIC', '-c', c_file, '-o', out_file]
    if verbose_flag:
        args += ['-v', '-Wall']
    #print 'Calling %r ...' % str.join(' ', args)
    status = call(args)
    if status:
        raise CCompilerError("C compiler returned status %s" % status)
    return out_file

def c_link(obj_file, verbose_flag=False, extra_objects=[], cplus=False):
    out_file = replace_suffix(obj_file, ".so")
    args = ['ld', '-shared', obj_file, '-o', out_file]
    if verbose_flag:
        args += ['-v']
    #print 'Calling %r ...' % str.join(' ', args)
    status = call(args)
    if status:
        raise CCompilerError("Linker returned status %s" % status)
    return out_file
