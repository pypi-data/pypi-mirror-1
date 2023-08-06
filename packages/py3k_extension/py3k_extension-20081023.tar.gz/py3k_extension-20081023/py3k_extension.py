"""
################################################################################
REVISION DATE: 20081019

AUTHOR: kai zhu - kaizhu@hpc.usc.edu

HOMEPAGE: http://www-rcf.usc.edu/~kaizhu/work/py3to2/old/extension

ABSTRACT:
  this is a minimal proof-of-concept extension module for python2.6, emulating
python3.0 syntax behavior, thru usage of some backported opcodes from python3.0.

MECHANISM:
  1. upon init, py3k_extension starts up a py3k server w/ pipe io.

  2. -> received via pipe io from py3k_extension, the py3k server 1st
        natively compiles the src code into a py3k codeobj, then converts it
        to py2x format w/ the addition of the backported opcodes.

  3. <- the serialized py2x codeobj is piped back to py3k_extension,
        which unserializes it & eval/exec it as normal.

in theory, this mechanism should transparently implement any bytecode-level py3k
language feature.  performance and robustness should b minimally impacted, since
the compiled code is directly run as native 2.x++ bytecode.

BACKWARD COMPATIBILITY:
  since this is a standalone extension module which doesn't modify python's
source code in any way, there shouldn't b any backward compatibility issues as
long as the module is not imported

################################################################################

LIMITATIONS:
  as a minimal extension module, this module DOES NOT SUPPORT CLASSES NOR
FUNCTION KEYWORD-ONLY ARGUMENTS, for the sake of simplicty
  
PY3K FEATURES TESTED TO WORK:
  pep3102  Keyword-Only Arguments
  pep3104  Access to Names in Outer Scopes
  pep3112  Bytes literals in Python 3000
  pep3113  Removal of Tuple Parameter Unpacking
  pep3132  Extended Iterable Unpacking

REQUIREMENTS:
  * linux / unix (windows has io problems w/ py3k server)

BUILD/INSTALL: python setup.py build install

USAGE:
  this module provides 3 wrapper functions similar to what's in python-3.0's builtins:
  - py3k_compile(code, filename, mode, flags, dont_inherit)
  - py3k_eval(code, globals = None, locals = None)
  - py3k_exec(code, globals = None, locals = None)

EXAMPLE:
  Python 2.6 (r26:66714, Oct 19 2008, 02:49:13)
  [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>>
  >>> import py3k_extension
  created read/write pipes: (4, 5)
  py3k server starting with pipes in/out/err: 7 5 -2
  py3k server: Python 3.0rc1 (r30rc1:66499, Oct 15 2008, 15:43:09)
  py3k server: [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
  py3k server: Type "help", "copyright", "credits" or "license" for more information.
  py3k server: >>> ''
  >>>
  >>> py3k_exec( "a, *b = 1,2,3" ) # pep3132  Extended Iterable Unpacking 
  >>> print a, b
  1 [2, 3]
  >>>
################################################################################

CHANGELOG:
20081023
  created a standalone extension module w/ limited capabilities
20081019
  ported to python-2.6
  consolidate & simplify patches to 1 file: ceval.c
  created extension module builtins_py3k
  revamped import hook again
  removed unicode support & restrict source code to ascii-only
20080727
  revampled import hook
20080911
  consolidate patches to 2 files: bltinmodule.c & ceval.c
20080828
  add kwonlyargcount 'attr' to codeobj
  add __annotations__ & __kwdefaults__ attr to funcobj
  add __pseudomethod__ feature to baseobj
20080819
  pure python import hook - removed magic comment & use magic path instead
  revamped str & bytes handling
  revamped py3k .pyc file handling
20080802
  pep3135  New Super
20080717
  pep3107  Function Annotations
  pep3120  Using UTF-8 as the default source encoding
  pep3131  Supporting Non-ASCII Identifiers
20080713
  import / reload works transparently on py3k scripts using a magic comment
  added pep3102  Keyword-Only Arguments
20080709 added a py3k preparser
20080702
  rewrote py3k server's pipe io.  implemented partial bytearray & bytes class.
  wrote a few simple tests
20080630
  __build_class__ function to bltmodule.c.  tested class decorators to b working.
################################################################################
"""

######## init
from __future__ import print_function
import __future__, os, sys
def x(): pass # emacs python-mode.el bug

DEBUG = 0 # set to 0 to suppress printing debug info
PYVERSION = "py2x" if sys.version_info[0] <= 2 else "py3k" # figure out if script is run under py2x or py3k interpreter

if PYVERSION == "py2x":
  import __builtin__
  sys.modules["builtins"] = builtins = __builtin__
  def add2builtins(fnc, fname = None): setattr(builtins, fname if fname else fnc.__name__, fnc); return fnc
else: import builtins, imp; builtins.reload = imp.reload

######## codetree
import dis, opcode, types
class codetree(object):
  opname_py2x = ["STOP_CODE", "POP_TOP", "ROT_TWO", "ROT_THREE", "DUP_TOP", "ROT_FOUR", "<6>", "<7>", "<8>", "NOP", "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", "UNARY_CONVERT", "<14>", "UNARY_INVERT", "<16>", "<17>", "LIST_APPEND", "BINARY_POWER", "BINARY_MULTIPLY", "BINARY_DIVIDE", "BINARY_MODULO", "BINARY_ADD", "BINARY_SUBTRACT", "BINARY_SUBSCR", "BINARY_FLOOR_DIVIDE", "BINARY_TRUE_DIVIDE", "INPLACE_FLOOR_DIVIDE", "INPLACE_TRUE_DIVIDE", "SLICE+0", "SLICE+1", "SLICE+2", "SLICE+3", "<34>", "<35>", "<36>", "<37>", "<38>", "<39>", "STORE_SLICE+0", "STORE_SLICE+1", "STORE_SLICE+2", "STORE_SLICE+3", "<44>", "<45>", "<46>", "<47>", "<48>", "<49>", "DELETE_SLICE+0", "DELETE_SLICE+1", "DELETE_SLICE+2", "DELETE_SLICE+3", "STORE_MAP", "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_MULTIPLY", "INPLACE_DIVIDE", "INPLACE_MODULO", "STORE_SUBSCR", "DELETE_SUBSCR", "BINARY_LSHIFT", "BINARY_RSHIFT", "BINARY_AND", "BINARY_XOR", "BINARY_OR", "INPLACE_POWER", "GET_ITER", "<69>", "PRINT_EXPR", "PRINT_ITEM", "PRINT_NEWLINE", "PRINT_ITEM_TO", "PRINT_NEWLINE_TO", "INPLACE_LSHIFT", "INPLACE_RSHIFT", "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "BREAK_LOOP", "WITH_CLEANUP", "LOAD_LOCALS", "RETURN_VALUE", "IMPORT_STAR", "EXEC_STMT", "YIELD_VALUE", "POP_BLOCK", "END_FINALLY", "BUILD_CLASS", "STORE_NAME", "DELETE_NAME", "UNPACK_SEQUENCE", "FOR_ITER", "<94>", "STORE_ATTR", "DELETE_ATTR", "STORE_GLOBAL", "DELETE_GLOBAL", "DUP_TOPX", "LOAD_CONST", "LOAD_NAME", "BUILD_TUPLE", "BUILD_LIST", "BUILD_MAP", "LOAD_ATTR", "COMPARE_OP", "IMPORT_NAME", "IMPORT_FROM", "<109>", "JUMP_FORWARD", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "JUMP_ABSOLUTE", "<114>", "<115>", "LOAD_GLOBAL", "<117>", "<118>", "CONTINUE_LOOP", "SETUP_LOOP", "SETUP_EXCEPT", "SETUP_FINALLY", "<123>", "LOAD_FAST", "STORE_FAST", "DELETE_FAST", "<127>", "<128>", "<129>", "RAISE_VARARGS", "CALL_FUNCTION", "MAKE_FUNCTION", "BUILD_SLICE", "MAKE_CLOSURE", "LOAD_CLOSURE", "LOAD_DEREF", "STORE_DEREF", "<138>", "<139>", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW", "EXTENDED_ARG", "<144>", "<145>", "<146>", "<147>", "<148>", "<149>", "<150>", "<151>", "<152>", "<153>", "<154>", "<155>", "<156>", "<157>", "<158>", "<159>", "<160>", "<161>", "<162>", "<163>", "<164>", "<165>", "<166>", "<167>", "<168>", "<169>", "<170>", "<171>", "<172>", "<173>", "<174>", "<175>", "<176>", "<177>", "<178>", "<179>", "<180>", "<181>", "<182>", "<183>", "<184>", "<185>", "<186>", "<187>", "<188>", "<189>", "<190>", "<191>", "<192>", "<193>", "<194>", "<195>", "<196>", "<197>", "<198>", "<199>", "<200>", "<201>", "<202>", "<203>", "<204>", "<205>", "<206>", "<207>", "<208>", "<209>", "<210>", "<211>", "<212>", "<213>", "<214>", "<215>", "<216>", "<217>", "<218>", "<219>", "<220>", "<221>", "<222>", "<223>", "<224>", "<225>", "<226>", "<227>", "<228>", "<229>", "<230>", "<231>", "<232>", "<233>", "<234>", "<235>", "<236>", "<237>", "<238>", "<239>", "<240>", "<241>", "<242>", "<243>", "<244>", "<245>", "<246>", "<247>", "<248>", "<249>", "<250>", "<251>", "<252>", "<253>", "<254>", "<255>"]
  opname_py3k = ["STOP_CODE", "POP_TOP", "ROT_TWO", "ROT_THREE", "DUP_TOP", "ROT_FOUR", "<6>", "<7>", "<8>", "NOP", "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", "<13>", "<14>", "UNARY_INVERT", "<16>", "SET_ADD", "LIST_APPEND", "BINARY_POWER", "BINARY_MULTIPLY", "<21>", "BINARY_MODULO", "BINARY_ADD", "BINARY_SUBTRACT", "BINARY_SUBSCR", "BINARY_FLOOR_DIVIDE", "BINARY_TRUE_DIVIDE", "INPLACE_FLOOR_DIVIDE", "INPLACE_TRUE_DIVIDE", "<30>", "<31>", "<32>", "<33>", "<34>", "<35>", "<36>", "<37>", "<38>", "<39>", "<40>", "<41>", "<42>", "<43>", "<44>", "<45>", "<46>", "<47>", "<48>", "<49>", "<50>", "<51>", "<52>", "<53>", "STORE_MAP", "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_MULTIPLY", "<58>", "INPLACE_MODULO", "STORE_SUBSCR", "DELETE_SUBSCR", "BINARY_LSHIFT", "BINARY_RSHIFT", "BINARY_AND", "BINARY_XOR", "BINARY_OR", "INPLACE_POWER", "GET_ITER", "STORE_LOCALS", "PRINT_EXPR", "LOAD_BUILD_CLASS", "<72>", "<73>", "<74>", "INPLACE_LSHIFT", "INPLACE_RSHIFT", "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "BREAK_LOOP", "WITH_CLEANUP", "<82>", "RETURN_VALUE", "IMPORT_STAR", "<85>", "YIELD_VALUE", "POP_BLOCK", "END_FINALLY", "POP_EXCEPT", "STORE_NAME", "DELETE_NAME", "UNPACK_SEQUENCE", "FOR_ITER", "UNPACK_EX", "STORE_ATTR", "DELETE_ATTR", "STORE_GLOBAL", "DELETE_GLOBAL", "DUP_TOPX", "LOAD_CONST", "LOAD_NAME", "BUILD_TUPLE", "BUILD_LIST", "BUILD_SET", "BUILD_MAP", "LOAD_ATTR", "COMPARE_OP", "IMPORT_NAME", "IMPORT_FROM", "JUMP_FORWARD", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "JUMP_ABSOLUTE", "<114>", "<115>", "LOAD_GLOBAL", "<117>", "<118>", "CONTINUE_LOOP", "SETUP_LOOP", "SETUP_EXCEPT", "SETUP_FINALLY", "<123>", "LOAD_FAST", "STORE_FAST", "DELETE_FAST", "<127>", "<128>", "<129>", "RAISE_VARARGS", "CALL_FUNCTION", "MAKE_FUNCTION", "BUILD_SLICE", "MAKE_CLOSURE", "LOAD_CLOSURE", "LOAD_DEREF", "STORE_DEREF", "<138>", "<139>", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW", "EXTENDED_ARG", "<144>", "<145>", "<146>", "<147>", "<148>", "<149>", "<150>", "<151>", "<152>", "<153>", "<154>", "<155>", "<156>", "<157>", "<158>", "<159>", "<160>", "<161>", "<162>", "<163>", "<164>", "<165>", "<166>", "<167>", "<168>", "<169>", "<170>", "<171>", "<172>", "<173>", "<174>", "<175>", "<176>", "<177>", "<178>", "<179>", "<180>", "<181>", "<182>", "<183>", "<184>", "<185>", "<186>", "<187>", "<188>", "<189>", "<190>", "<191>", "<192>", "<193>", "<194>", "<195>", "<196>", "<197>", "<198>", "<199>", "<200>", "<201>", "<202>", "<203>", "<204>", "<205>", "<206>", "<207>", "<208>", "<209>", "<210>", "<211>", "<212>", "<213>", "<214>", "<215>", "<216>", "<217>", "<218>", "<219>", "<220>", "<221>", "<222>", "<223>", "<224>", "<225>", "<226>", "<227>", "<228>", "<229>", "<230>", "<231>", "<232>", "<233>", "<234>", "<235>", "<236>", "<237>", "<238>", "<239>", "<240>", "<241>", "<242>", "<243>", "<244>", "<245>", "<246>", "<247>", "<248>", "<249>", "<250>", "<251>", "<252>", "<253>", "<254>", "<255>"]
  opnew_py2x = {"SET_ADD_py3k":17, "STORE_LOCALS_py3k":69, "LOAD_BUILD_CLASS_py3k":34, "MAKE_BYTES_py3k":35, "POP_EXCEPT_py3k":36, "UNPACK_EX_py3k":94, "BUILD_SET_py3k":192} # py3k opcodes to b backported

  for i, x in enumerate(opname_py3k):
    if x + "_py3k" in opnew_py2x: opname_py3k[i] = x + "_py3k" # update opname_py3k
  for x, i in opnew_py2x.items(): opname_py2x[i] = x # update opname_py2x

  opmap_py2x = dict((x, i) for i, x in enumerate(opname_py2x) if x[0] != "<") # py2x opmap
  opmap_py3k = dict((x, i) for i, x in enumerate(opname_py3k) if x[0] != "<") # py3k opmap
  op3to2 = {} # sparse mapping of 3to2 opcodes
  for i, (op3k, op2x) in enumerate(zip(opname_py3k, opname_py2x)):
    if op3k != op2x and op3k[0] != "<": op3to2[i] = opnew_py2x.get(op3k, opmap_py2x[op3k])
  op3to2[opmap_py3k["POP_EXCEPT_py3k"]] = opmap_py2x["NOP"] # disable py3k exceptions

  if PYVERSION == "py2x":
    opcode.opname = opname_py2x; opcode.opmap = opmap_py2x; reload(dis) # update dis w/ backported opcodes
    co_args = ["co_argcount", "co_nlocals", "co_stacksize", "co_flags", "co_code", "co_consts", "co_names", "co_varnames", "co_filename", "co_name", "co_firstlineno", "co_lnotab", "co_freevars", "co_cellvars"]
  else:
    opcode.opname = opname_py3k; opcode.opmap = opmap_py3k; reload(dis) # update dis
    co_args = ["co_argcount", "co_kwonlyargcount", "co_nlocals", "co_stacksize", "co_flags", "co_code", "co_consts", "co_names", "co_varnames", "co_filename", "co_name", "co_firstlineno", "co_lnotab", "co_freevars", "co_cellvars"]
  co_constsi = co_args.index("co_consts") # co_consts index pos

  def __init__(self, code = None, depth = 0, **kwds):
    if code: # code object
      self.__dict__ = dict((x, getattr(code, x)) for x in self.co_args)
      self.co_consts = tuple(codetree(x, depth = depth + 1) if isinstance(x, types.CodeType) else x for x in code.co_consts) # recurse
    self.depth = depth; self.__dict__.update(kwds)

  def __eq__(self, x): return type(self) == type(x) and self.__dict__ == x.__dict__

  def __repr__(self): return "codetree(**%r)" % self.__dict__

  def __str__(self):
    _ =  " " * self.depth
    hsh = sorted(x for x in self.__dict__.items() if x[0] != "co_consts")
    hsh = "".join(_ + k + " =" + " " * (0x10 - len(k)) + repr(x) + ",\n" for k, x in hsh)
    consts = "".join(_ + " " + str(x) + ",\n" for x in self.co_consts)
    return "codetree(\n" + hsh + "%sco_consts = (\n" % _ + consts + "%s )" % _ + ")"

  def compile(self):
    args = [getattr(self, x) for x in self.co_args] # create list of args
    args[self.co_constsi] = tuple(x.compile() if isinstance(x, codetree) else x for x in self.co_consts)  # recurse
    return types.CodeType(*args)

  def dis(self):
    def recurse(x, _ = ""):
      if isinstance(x, types.CodeType):
        dis.dis(x); f.seek(0); yield _ + f.read().replace("\n", "\n" + _); f.seek(0); f.truncate()
        for x in x.co_consts:
          for x in recurse(x, _ + "\t"): yield x

    stdout = sys.stdout
    try: import tempfile; sys.stdout = f = tempfile.TemporaryFile(); s = "\n".join(recurse(self.compile()))
    finally: sys.stdout = stdout; f.close()
    return s

  def py3to2(self): # run only under py3k
    if self.co_kwonlyargcount: raise ValueError("codeobj.co_kwonlyargcount != 0 (pep3102  Keyword-Only Arguments not supported)")
    self = codetree(**self.__dict__) # copy self
    s = bytearray(self.co_code); HAVE_ARGUMENT = opcode.HAVE_ARGUMENT; op3to2 = self.op3to2; skip = 0
    for i, x in enumerate(s): # remap opcodes from py3k to py2x
      if skip: skip -= 1; continue
      if x >= HAVE_ARGUMENT: skip = 2
      if x in op3to2:
        if x is self.opmap_py3k["LOAD_BUILD_CLASS_py3k"]: raise ValueError("unsupported py3k opcode LOAD_BUILD_CLASS_py3k")
        s[i] = op3to2[x]
    self.co_code = bytes(s)
    self.co_consts = tuple( x.py3to2() if isinstance(x, codetree) else x for x in self.co_consts ) # recurse
    return self

  @staticmethod
  def test():
    global xxx; src = TESTCODE
    # beg base tests
    c0 = compile(src, "", "exec"); t0 = codetree(c0); print( t0 ); s0 = repr(t0) # code, tree, repr
    print( s0 )
    print( repr(eval(s0)) )
    assert t0 == eval(s0) # tree == eval(repr(tree))
    assert c0 == t0.compile() # code == codetree(code).compile()
    print( "codetree PASS base tests\n" )
    # end base tests
    if 1 and PYVERSION == "py3k": t1 = t0.py3to2(); print( t1 )

if DEBUG:
  if 0:
    TESTCODE = "def foo(x):\n def bar(y): x\n bar(y)"
    TESTCODE = "exec('')"
    codetree.test()

if PYVERSION == "py2x":
  ######## server
  import signal, cStringIO, subprocess, traceback
  class _server(subprocess.Popen):
    class Py3kServerExc(Exception): pass
    if "server" in globals(): map(os.close, server.pipe); os.kill(server.pid, signal.SIGTERM) # kill prev server
    pipe = os.pipe(); print( "created read/write pipes: %s" % (pipe,) ) # create io pipes
    buf = cStringIO.StringIO() # stores server output

    def __init__(self):
      i, o, e = subprocess.PIPE, _server.pipe[1], subprocess.STDOUT
      subprocess.Popen.__init__(self, "python3.0 -i", stdin = i, stdout = o, stderr = e, shell = True) # start up py3k server
      print( "py3k server starting with pipes in/out/err: %i %i %i" % (
        self.stdin.fileno() if self.stdin else i,
        self.stdout.fileno() if self.stdout else o,
        self.stderr.fileno() if self.stderr else e,
        ))

      self.stdin.write("import sys; sys.ps1 = ''\n") # remove prompt
      self.stdin.write("import py3k_extension; from py3k_extension import *\n")
      self.input("''\n") # flush output

    def input(self, s, stdout = True, bufsize = 4096,
              eof = "<eof %s>" % hex(id("eof")),
              prompt = "py3k server: ",
              traceback = "\nTraceback (most recent call last):\n"):
      if not s: return ""
      buf = self.buf; self.stdin.write(s); self.stdin.write("\nx = sys.stdout.write( % r)\n" % eof) # input

      n = len(eof); buf.seek(0); buf.truncate() # reset buf
      while True: # read output stream until eof
        x = os.read(self.pipe[0], bufsize); buf.write(x) # record output
        if eof == ( x[-n:] if len(x) >= n else buf.getvalue()[-n:] ): break
      buf.seek(0); buf = buf.read()[:-n - 1]
      if stdout and buf: print( prompt + buf.replace("\n", "\n" + prompt) )

      i = ("\n" + buf).find(traceback)

      if i != -1:
        buf = ("\n" + buf)[i:]
        err = buf.split("\n")[-1]
        if ": " in err:
          err, msg = err.split(": ", 1)
          err = getattr(__builtin__, err, err)
          if issubclass(err, Exception): raise err(msg)
        raise self.Py3kServerExc( buf.replace("\n", "\n>") )
  
      return buf
  server = _server() # init

  ######## eval/exec/compile
  import _py3k_extension
  builtins.py3k_evalcode = _py3k_extension.py3k_evalcode
  builtins.py3k_eval = _py3k_extension.py3k_eval
  builtins.py3k_exec = _py3k_extension.py3k_exec

  import tempfile
  def py3k_compile(source, filename, mode, flags = 0, dont_inherit = 0, debug = None): # wrapper for py3k builtins.compile
    if type(source) is not str: raise TypeError( "py3k_compile only accepts code type %s, not %s" % (type(str), type(source)) )
    ascii = source.replace("\n", " ")
    if not "\x20" <= min(ascii) <= max(ascii) < "\x80": raise ValueError("py3k_compile only accepts ascii string code") # only ascii strings allowed

    if not filename: f = tempfile.NamedTemporaryFile(suffix = ".py", delete = None); f.write(source); f.close(); filename = f.name # create a temporaray file for debugging if filename is not specified
    server.input("code = compile(%r, %r, %r, %s, %s)" % (source, filename, mode, flags, dont_inherit)) # compile to py3k code
    s = eval( server.input("ascii( codetree(code).py3to2() )", stdout = None) ) # py3k code -> py2x code

    s = s.replace("'compile'", "'py3k_compile'")
    s = s.replace("'eval'", "'py3k_eval'")
    s = s.replace("'exec'", "'py3k_exec'")
    
    t = eval(s); code = t.compile()
    if debug: print( t ); dis.dis(code) # debug compiled code
    return code

  @add2builtins
  def py3k_evalexec(mode, code, globals, locals):
    if not isinstance(code, types.CodeType): code = py3k_compile(code, "", mode)
    x = py3k_evalcode(code, globals, locals)
    if mode == "eval": return x

  def py3k_test():
    if 1:
      print( 'pep3104  Access to Names in Outer Scopes' )
      s = 'def foo(x):\n def bar(): nonlocal x; x+=1\n bar(); return x\nassert foo(1)==2'; print( s ); py3k_exec(s); print( 'PASS\n' )
    if 1:
      print( 'pep3112  Bytes literals in Python 3000' )
      s = 'assert bytes("hello") == b"hello" == eval(repr(b"hello"))'; print( s ); py3k_exec(s); print( 'PASS\n' )
    if 1:
      print( 'pep3113  Removal of Tuple Parameter Unpacking - server should give a SyntaxError msg' )
      s = 'try: exec("def foo(a,(b,c)): pass")\nexcept SyntaxError: pass\nelse: raise Exception'; print( s ); py3k_exec(s); print( 'PASS\n' )
    if 1:
      print( 'pep3132  Extended Iterable Unpacking' )
      s = 'a,*b=1,2,3; assert a==1 and b==[2,3]'; print( s ); py3k_exec(s); print( 'PASS\n' )
