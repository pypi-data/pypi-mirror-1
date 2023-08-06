#include "Python.h"
#include "ceval.c" // py3k - unmodified copy from Python-2.6/Python/ceval.c







//////// py3k - backported opcodes
#define SET_ADD_py3k 17 // 17 in py3k
#define STORE_LOCALS_py3k 69 // 69 in py3k
// #define LOAD_BUILD_CLASS_py3k 34 // 71 in py3k
// #define MAKE_BYTES_py3k 35 // 85 in py3k
// #define POP_EXCEPT_py3k 36 // 89 in py3k
#define UNPACK_EX_py3k 94 // 94 in py3k
#define BUILD_SET_py3k 192 // 104 in py3k







//////// py3k - skeleton
static int unpack_iterable_py3k(PyObject *v, int argcnt, int argcntafter, PyObject **sp); // from Python-3.0/Python/bltinmodule.c

static PyObject *PyEval_EvalFrameEx_py3k(PyFrameObject *f, int throwflag);

static PyObject *PyEval_EvalCodeEx_py3k(
	PyCodeObject *co, PyObject *globals, PyObject *locals,
	PyObject **args, int argcount, PyObject **kws, int kwcount,
	PyObject **defs, int defcount, PyObject *closure);

static PyObject *py3k_evalexecglobalslocals(char *mode, PyObject *code, PyObject *globals, PyObject *locals) {
	if (locals != Py_None && !PyMapping_Check(locals)) {
		PyErr_SetString(PyExc_TypeError, "locals must b a mapping"); return NULL; }
	if (globals != Py_None && !PyDict_Check(globals)) {
		PyErr_SetString(PyExc_TypeError, "globals must b a dict"); return NULL; }
	if (globals == Py_None) {
		globals = PyEval_GetGlobals();
		if (locals == Py_None) locals = PyEval_GetLocals(); }
	else if (locals == Py_None) locals = globals;

	if (globals == NULL || locals == NULL) {
		PyErr_SetString(PyExc_TypeError,
			"eval/exec must be given globals and locals "
			"when called without a frame");
		return NULL; }

	PyObject *args = Py_BuildValue("sOOO", mode, code, globals, locals);
	PyObject *func = PyDict_GetItemString(PyEval_GetBuiltins(), "py3k_evalexec"); // get function
	if (!(func && PyCallable_Check(func))) { PyErr_SetString(PyExc_NotImplementedError, "py3k_evalexec"); return NULL; }
	PyObject *retval = PyEval_CallObject(func, args); Py_DECREF(args); return retval;
}

static PyObject *py3k_evalcode(PyObject *self, PyObject *args) {
	PyObject *code, *globals, *locals;
	if (!PyArg_UnpackTuple(args, "evalcode", 1, 3, &code, &globals, &locals)) return NULL;
	if (locals != Py_None && !PyMapping_Check(locals)) {
		PyErr_SetString(PyExc_TypeError, "locals must be a mapping");
		return NULL;
	}

	if (!PyCode_Check(code)) { PyErr_SetString(PyExc_TypeError, "arg1 <code> must b a codeobj"); return NULL; }
	if (!PyDict_Check(globals)) { PyErr_SetString(PyExc_TypeError, "arg2 <globals> must b a dict"); return NULL; }
	if (!PyMapping_Check(locals)) { PyErr_SetString(PyExc_TypeError, "arg3 <locals> must b a mapping"); return NULL; }
	return PyEval_EvalCodeEx_py3k(
		(PyCodeObject *) code, globals, locals,
		NULL, 0, NULL, 0,
		NULL, 0, NULL);
}

PyDoc_STRVAR(evalcode_doc,
"py3k_evalcode(code, globals, locals) -> value\n\
\n\
like eval except code must b a codeobj\n");

static PyObject *py3k_eval(PyObject *self, PyObject *args) {
	PyObject *code, *globals = Py_None, *locals = Py_None;
	if (!PyArg_UnpackTuple(args, "eval", 1, 3, &code, &globals, &locals)) return NULL;
	return py3k_evalexecglobalslocals("eval", code, globals, locals);
}

PyDoc_STRVAR(eval_doc,
"eval(source[, globals[, locals]]) -> value\n\
\n\
Evaluate the source in the context of globals and locals.\n\
The source may be a string representing a Python expression\n\
or a code object as returned by compile().\n\
The globals must be a dictionary and locals can be any mapping,\n\
defaulting to the current globals and locals.\n\
If only globals is given, locals defaults to it.\n");

static PyObject *py3k_exec(PyObject *self, PyObject *args) {
	PyObject *code, *globals = Py_None, *locals = Py_None;
	if (!PyArg_UnpackTuple(args, "exec", 1, 3, &code, &globals, &locals)) return NULL;
	if ( py3k_evalexecglobalslocals("exec", code, globals, locals) == NULL ) return NULL;
	Py_RETURN_NONE;
}

PyDoc_STRVAR(exec_doc,
"exec(object[, globals[, locals]])\n\
\n\
Read and execute code from a object, which can be a string, a code\n\
object or a file object.\n\
The globals and locals are dictionaries, defaulting to the current\n\
globals and locals.  If only globals is given, locals defaults to it.");

static PyMethodDef py3k_methods[] = {
	{"py3k_evalcode",	(PyCFunction)py3k_evalcode,	METH_VARARGS,	evalcode_doc},
	{"py3k_eval",		(PyCFunction)py3k_eval,		METH_VARARGS,	eval_doc},
	{"py3k_exec",		(PyCFunction)py3k_exec,		METH_VARARGS,	exec_doc},
	{NULL}				/* Sentinel */
};

PyObject *init_py3k_extension(void) { return Py_InitModule("_py3k_extension", py3k_methods); }







//////// py3k - flesh for the skeleton
static int
unpack_iterable_py3k(PyObject *v, int argcnt, int argcntafter, PyObject **sp)
{
	int i = 0, j = 0;
	Py_ssize_t ll = 0;
	PyObject *it;  /* iter(v) */
	PyObject *w;
	PyObject *l = NULL; /* variable list */

	assert(v != NULL);

	it = PyObject_GetIter(v);
	if (it == NULL)
		goto Error;

	for (; i < argcnt; i++) {
		w = PyIter_Next(it);
		if (w == NULL) {
			/* Iterator done, via error or exhaustion. */
			if (!PyErr_Occurred()) {
				PyErr_Format(PyExc_ValueError,
					"need more than %d value%s to unpack",
					i, i == 1 ? "" : "s");
			}
			goto Error;
		}
		*--sp = w;
	}

	if (argcntafter == -1) {
		/* We better have exhausted the iterator now. */
		w = PyIter_Next(it);
		if (w == NULL) {
			if (PyErr_Occurred())
				goto Error;
			Py_DECREF(it);
			return 1;
		}
		Py_DECREF(w);
		PyErr_SetString(PyExc_ValueError, "too many values to unpack");
		goto Error;
	}

	l = PySequence_List(it);
	if (l == NULL)
		goto Error;
	*--sp = l;
	i++;

	ll = PyList_GET_SIZE(l);
	if (ll < argcntafter) {
		PyErr_Format(PyExc_ValueError, "need more than %zd values to unpack",
			     argcnt + ll);
		goto Error;
	}

	/* Pop the "after-variable" args off the list. */
	for (j = argcntafter; j > 0; j--, i++) {
		*--sp = PyList_GET_ITEM(l, ll - j);
	}
	/* Resize the list. */
	Py_SIZE(l) = ll - argcntafter;
	Py_DECREF(it);
	return 1;

Error:
	for (; i > 0; i--, sp++)
		Py_DECREF(*sp);
	Py_XDECREF(it);
	return 0;
}

static PyObject *
PyEval_EvalFrameEx_py3k(PyFrameObject *f, int throwflag)
{
#ifdef DXPAIRS
	int lastopcode = 0;
#endif
	register PyObject **stack_pointer;  /* Next free slot in value stack */
	register unsigned char *next_instr;
	register int opcode;	/* Current opcode */
	register int oparg;	/* Current opcode argument, if any */
	register enum why_code why; /* Reason for block stack unwind */
	register int err;	/* Error status -- nonzero if error */
	register PyObject *x;	/* Result object -- NULL if error */
	register PyObject *v;	/* Temporary objects popped off stack */
	register PyObject *w;
	register PyObject *u;
	register PyObject *t;
	register PyObject *stream = NULL;    /* for PRINT opcodes */
	register PyObject **fastlocals, **freevars;
	PyObject *retval = NULL;	/* Return value */
	PyThreadState *tstate = PyThreadState_GET();
	PyCodeObject *co;

	/* when tracing we set things up so that

	       not (instr_lb <= current_bytecode_offset < instr_ub)

	   is true when the line being executed has changed.  The
	   initial values are such as to make this false the first
	   time it is tested. */
	int instr_ub = -1, instr_lb = 0, instr_prev = -1;

	unsigned char *first_instr;
	PyObject *names;
	PyObject *consts;
#if defined(Py_DEBUG) || defined(LLTRACE)
	/* Make it easier to find out where we are with a debugger */
	char *filename;
#endif

/* Tuple access macros */

#ifndef Py_DEBUG
#define GETITEM(v, i) PyTuple_GET_ITEM((PyTupleObject *)(v), (i))
#else
#define GETITEM(v, i) PyTuple_GetItem((v), (i))
#endif

#ifdef WITH_TSC
/* Use Pentium timestamp counter to mark certain events:
   inst0 -- beginning of switch statement for opcode dispatch
   inst1 -- end of switch statement (may be skipped)
   loop0 -- the top of the mainloop
   loop1 -- place where control returns again to top of mainloop
	    (may be skipped)
   intr1 -- beginning of long interruption
   intr2 -- end of long interruption

   Many opcodes call out to helper C functions.  In some cases, the
   time in those functions should be counted towards the time for the
   opcode, but not in all cases.  For example, a CALL_FUNCTION opcode
   calls another Python function; there's no point in charge all the
   bytecode executed by the called function to the caller.

   It's hard to make a useful judgement statically.  In the presence
   of operator overloading, it's impossible to tell if a call will
   execute new Python code or not.

   It's a case-by-case judgement.  I'll use intr1 for the following
   cases:

   EXEC_STMT
   IMPORT_STAR
   IMPORT_FROM
   CALL_FUNCTION (and friends)

 */
	uint64 inst0, inst1, loop0, loop1, intr0 = 0, intr1 = 0;
	int ticked = 0;

	READ_TIMESTAMP(inst0);
	READ_TIMESTAMP(inst1);
	READ_TIMESTAMP(loop0);
	READ_TIMESTAMP(loop1);

	/* shut up the compiler */
	opcode = 0;
#endif

/* Code access macros */

#define INSTR_OFFSET()	((int)(next_instr - first_instr))
#define NEXTOP()	(*next_instr++)
#define NEXTARG()	(next_instr += 2, (next_instr[-1]<<8) + next_instr[-2])
#define PEEKARG()	((next_instr[2]<<8) + next_instr[1])
#define JUMPTO(x)	(next_instr = first_instr + (x))
#define JUMPBY(x)	(next_instr += (x))

/* OpCode prediction macros
	Some opcodes tend to come in pairs thus making it possible to
	predict the second code when the first is run.  For example,
	COMPARE_OP is often followed by JUMP_IF_FALSE or JUMP_IF_TRUE.  And,
	those opcodes are often followed by a POP_TOP.

	Verifying the prediction costs a single high-speed test of a register
	variable against a constant.  If the pairing was good, then the
	processor's own internal branch predication has a high likelihood of
	success, resulting in a nearly zero-overhead transition to the
	next opcode.  A successful prediction saves a trip through the eval-loop
	including its two unpredictable branches, the HAS_ARG test and the
	switch-case.  Combined with the processor's internal branch prediction,
	a successful PREDICT has the effect of making the two opcodes run as if
	they were a single new opcode with the bodies combined.

    If collecting opcode statistics, your choices are to either keep the
	predictions turned-on and interpret the results as if some opcodes
	had been combined or turn-off predictions so that the opcode frequency
	counter updates for both opcodes.
*/

#ifdef DYNAMIC_EXECUTION_PROFILE
#define PREDICT(op)		if (0) goto PRED_##op
#else
#define PREDICT(op)		if (*next_instr == op) goto PRED_##op
#endif

#define PREDICTED(op)		PRED_##op: next_instr++
#define PREDICTED_WITH_ARG(op)	PRED_##op: oparg = PEEKARG(); next_instr += 3

/* Stack manipulation macros */

/* The stack can grow at most MAXINT deep, as co_nlocals and
   co_stacksize are ints. */
#define STACK_LEVEL()	((int)(stack_pointer - f->f_valuestack))
#define EMPTY()		(STACK_LEVEL() == 0)
#define TOP()		(stack_pointer[-1])
#define SECOND()	(stack_pointer[-2])
#define THIRD() 	(stack_pointer[-3])
#define FOURTH()	(stack_pointer[-4])
#define SET_TOP(v)	(stack_pointer[-1] = (v))
#define SET_SECOND(v)	(stack_pointer[-2] = (v))
#define SET_THIRD(v)	(stack_pointer[-3] = (v))
#define SET_FOURTH(v)	(stack_pointer[-4] = (v))
#define BASIC_STACKADJ(n)	(stack_pointer += n)
#define BASIC_PUSH(v)	(*stack_pointer++ = (v))
#define BASIC_POP()	(*--stack_pointer)

#ifdef LLTRACE
#define PUSH(v)		{ (void)(BASIC_PUSH(v), \
			       lltrace && prtrace(TOP(), "push")); \
			       assert(STACK_LEVEL() <= co->co_stacksize); }
#define POP()		((void)(lltrace && prtrace(TOP(), "pop")), \
			 BASIC_POP())
#define STACKADJ(n)	{ (void)(BASIC_STACKADJ(n), \
			       lltrace && prtrace(TOP(), "stackadj")); \
			       assert(STACK_LEVEL() <= co->co_stacksize); }
#define EXT_POP(STACK_POINTER) ((void)(lltrace && \
				prtrace((STACK_POINTER)[-1], "ext_pop")), \
				*--(STACK_POINTER))
#else
#define PUSH(v)		BASIC_PUSH(v)
#define POP()		BASIC_POP()
#define STACKADJ(n)	BASIC_STACKADJ(n)
#define EXT_POP(STACK_POINTER) (*--(STACK_POINTER))
#endif

/* Local variable macros */

#define GETLOCAL(i)	(fastlocals[i])

/* The SETLOCAL() macro must not DECREF the local variable in-place and
   then store the new value; it must copy the old value to a temporary
   value, then store the new value, and then DECREF the temporary value.
   This is because it is possible that during the DECREF the frame is
   accessed by other code (e.g. a __del__ method or gc.collect()) and the
   variable would be pointing to already-freed memory. */
#define SETLOCAL(i, value)	do { PyObject *tmp = GETLOCAL(i); \
				     GETLOCAL(i) = value; \
				     Py_XDECREF(tmp); } while (0)

/* Start of code */

	if (f == NULL)
		return NULL;

	/* push frame */
	if (Py_EnterRecursiveCall(""))
		return NULL;

	tstate->frame = f;

	if (tstate->use_tracing) {
		if (tstate->c_tracefunc != NULL) {
			/* tstate->c_tracefunc, if defined, is a
			   function that will be called on *every* entry
			   to a code block.  Its return value, if not
			   None, is a function that will be called at
			   the start of each executed line of code.
			   (Actually, the function must return itself
			   in order to continue tracing.)  The trace
			   functions are called with three arguments:
			   a pointer to the current frame, a string
			   indicating why the function is called, and
			   an argument which depends on the situation.
			   The global trace function is also called
			   whenever an exception is detected. */
			if (call_trace_protected(tstate->c_tracefunc,
						 tstate->c_traceobj,
						 f, PyTrace_CALL, Py_None)) {
				/* Trace function raised an error */
				goto exit_eval_frame;
			}
		}
		if (tstate->c_profilefunc != NULL) {
			/* Similar for c_profilefunc, except it needn't
			   return itself and isn't called for "line" events */
			if (call_trace_protected(tstate->c_profilefunc,
						 tstate->c_profileobj,
						 f, PyTrace_CALL, Py_None)) {
				/* Profile function raised an error */
				goto exit_eval_frame;
			}
		}
	}

	co = f->f_code;
	names = co->co_names;
	consts = co->co_consts;
	fastlocals = f->f_localsplus;
	freevars = f->f_localsplus + co->co_nlocals;
	first_instr = (unsigned char*) PyString_AS_STRING(co->co_code);
	/* An explanation is in order for the next line.

	   f->f_lasti now refers to the index of the last instruction
	   executed.  You might think this was obvious from the name, but
	   this wasn't always true before 2.3!  PyFrame_New now sets
	   f->f_lasti to -1 (i.e. the index *before* the first instruction)
	   and YIELD_VALUE doesn't fiddle with f_lasti any more.  So this
	   does work.  Promise.

	   When the PREDICT() macros are enabled, some opcode pairs follow in
	   direct succession without updating f->f_lasti.  A successful
	   prediction effectively links the two codes together as if they
	   were a single new opcode; accordingly,f->f_lasti will point to
	   the first code in the pair (for instance, GET_ITER followed by
	   FOR_ITER is effectively a single opcode and f->f_lasti will point
	   at to the beginning of the combined pair.)
	*/
	next_instr = first_instr + f->f_lasti + 1;
	stack_pointer = f->f_stacktop;
	assert(stack_pointer != NULL);
	f->f_stacktop = NULL;	/* remains NULL unless yield suspends frame */

#ifdef LLTRACE
	lltrace = PyDict_GetItemString(f->f_globals, "__lltrace__") != NULL;
#endif
#if defined(Py_DEBUG) || defined(LLTRACE)
	filename = PyString_AsString(co->co_filename);
#endif

	why = WHY_NOT;
	err = 0;
	x = Py_None;	/* Not a reference, just anything non-NULL */
	w = NULL;

	if (throwflag) { /* support for generator.throw() */
		why = WHY_EXCEPTION;
		goto on_error;
	}

	for (;;) {
#ifdef WITH_TSC
		if (inst1 == 0) {
			/* Almost surely, the opcode executed a break
			   or a continue, preventing inst1 from being set
			   on the way out of the loop.
			*/
			READ_TIMESTAMP(inst1);
			loop1 = inst1;
		}
		dump_tsc(opcode, ticked, inst0, inst1, loop0, loop1,
			 intr0, intr1);
		ticked = 0;
		inst1 = 0;
		intr0 = 0;
		intr1 = 0;
		READ_TIMESTAMP(loop0);
#endif
		assert(stack_pointer >= f->f_valuestack); /* else underflow */
		assert(STACK_LEVEL() <= co->co_stacksize);  /* else overflow */

		/* Do periodic things.  Doing this every time through
		   the loop would add too much overhead, so we do it
		   only every Nth instruction.  We also do it if
		   ``things_to_do'' is set, i.e. when an asynchronous
		   event needs attention (e.g. a signal handler or
		   async I/O handler); see Py_AddPendingCall() and
		   Py_MakePendingCalls() above. */

		if (--_Py_Ticker < 0) {
			if (*next_instr == SETUP_FINALLY) {
				/* Make the last opcode before
				   a try: finally: block uninterruptable. */
				goto fast_next_opcode;
			}
			_Py_Ticker = _Py_CheckInterval;
			tstate->tick_counter++;
#ifdef WITH_TSC
			ticked = 1;
#endif
			if (things_to_do) {
				if (Py_MakePendingCalls() < 0) {
					why = WHY_EXCEPTION;
					goto on_error;
				}
				if (things_to_do)
					/* MakePendingCalls() didn't succeed.
					   Force early re-execution of this
					   "periodic" code, possibly after
					   a thread switch */
					_Py_Ticker = 0;
			}
#ifdef WITH_THREAD
			if (interpreter_lock) {
				/* Give another thread a chance */

				if (PyThreadState_Swap(NULL) != tstate)
					Py_FatalError("ceval: tstate mix-up");
				PyThread_release_lock(interpreter_lock);

				/* Other threads may run now */

				PyThread_acquire_lock(interpreter_lock, 1);
				if (PyThreadState_Swap(tstate) != NULL)
					Py_FatalError("ceval: orphan tstate");

				/* Check for thread interrupts */

				if (tstate->async_exc != NULL) {
					x = tstate->async_exc;
					tstate->async_exc = NULL;
					PyErr_SetNone(x);
					Py_DECREF(x);
					why = WHY_EXCEPTION;
					goto on_error;
				}
			}
#endif
		}

	fast_next_opcode:
		f->f_lasti = INSTR_OFFSET();

		/* line-by-line tracing support */

		if (tstate->c_tracefunc != NULL && !tstate->tracing) {
			/* see maybe_call_line_trace
			   for expository comments */
			f->f_stacktop = stack_pointer;

			err = maybe_call_line_trace(tstate->c_tracefunc,
						    tstate->c_traceobj,
						    f, &instr_lb, &instr_ub,
						    &instr_prev);
			/* Reload possibly changed frame fields */
			JUMPTO(f->f_lasti);
			if (f->f_stacktop != NULL) {
				stack_pointer = f->f_stacktop;
				f->f_stacktop = NULL;
			}
			if (err) {
				/* trace function raised an exception */
				goto on_error;
			}
		}

		/* Extract opcode and argument */

		opcode = NEXTOP();
		oparg = 0;   /* allows oparg to be stored in a register because
			it doesn't have to be remembered across a full loop */
		if (HAS_ARG(opcode))
			oparg = NEXTARG();
	  dispatch_opcode:
#ifdef DYNAMIC_EXECUTION_PROFILE
#ifdef DXPAIRS
		dxpairs[lastopcode][opcode]++;
		lastopcode = opcode;
#endif
		dxp[opcode]++;
#endif

#ifdef LLTRACE
		/* Instruction tracing */

		if (lltrace) {
			if (HAS_ARG(opcode)) {
				printf("%d: %d, %d\n",
				       f->f_lasti, opcode, oparg);
			}
			else {
				printf("%d: %d\n",
				       f->f_lasti, opcode);
			}
		}
#endif

		/* Main switch on opcode */
		READ_TIMESTAMP(inst0);

		switch (opcode) {

		/* BEWARE!
		   It is essential that any operation that fails sets either
		   x to NULL, err to nonzero, or why to anything but WHY_NOT,
		   and that no operation that succeeds does this! */

		/* case STOP_CODE: this is an error! */

		case NOP:
			goto fast_next_opcode;

		case LOAD_FAST:
			x = GETLOCAL(oparg);
			if (x != NULL) {
				Py_INCREF(x);
				PUSH(x);
				goto fast_next_opcode;
			}
			format_exc_check_arg(PyExc_UnboundLocalError,
				UNBOUNDLOCAL_ERROR_MSG,
				PyTuple_GetItem(co->co_varnames, oparg));
			break;

		case LOAD_CONST:
			x = GETITEM(consts, oparg);
			Py_INCREF(x);
			PUSH(x);
			goto fast_next_opcode;

		PREDICTED_WITH_ARG(STORE_FAST);
		case STORE_FAST:
			v = POP();
			SETLOCAL(oparg, v);
			goto fast_next_opcode;

		PREDICTED(POP_TOP);
		case POP_TOP:
			v = POP();
			Py_DECREF(v);
			goto fast_next_opcode;

		case ROT_TWO:
			v = TOP();
			w = SECOND();
			SET_TOP(w);
			SET_SECOND(v);
			goto fast_next_opcode;

		case ROT_THREE:
			v = TOP();
			w = SECOND();
			x = THIRD();
			SET_TOP(w);
			SET_SECOND(x);
			SET_THIRD(v);
			goto fast_next_opcode;

		case ROT_FOUR:
			u = TOP();
			v = SECOND();
			w = THIRD();
			x = FOURTH();
			SET_TOP(v);
			SET_SECOND(w);
			SET_THIRD(x);
			SET_FOURTH(u);
			goto fast_next_opcode;

		case DUP_TOP:
			v = TOP();
			Py_INCREF(v);
			PUSH(v);
			goto fast_next_opcode;

		case DUP_TOPX:
			if (oparg == 2) {
				x = TOP();
				Py_INCREF(x);
				w = SECOND();
				Py_INCREF(w);
				STACKADJ(2);
				SET_TOP(x);
				SET_SECOND(w);
				goto fast_next_opcode;
			} else if (oparg == 3) {
				x = TOP();
				Py_INCREF(x);
				w = SECOND();
				Py_INCREF(w);
				v = THIRD();
				Py_INCREF(v);
				STACKADJ(3);
				SET_TOP(x);
				SET_SECOND(w);
				SET_THIRD(v);
				goto fast_next_opcode;
			}
			Py_FatalError("invalid argument to DUP_TOPX"
				      " (bytecode corruption?)");
			break;

		case UNARY_POSITIVE:
			v = TOP();
			x = PyNumber_Positive(v);
			Py_DECREF(v);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case UNARY_NEGATIVE:
			v = TOP();
			x = PyNumber_Negative(v);
			Py_DECREF(v);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case UNARY_NOT:
			v = TOP();
			err = PyObject_IsTrue(v);
			Py_DECREF(v);
			if (err == 0) {
				Py_INCREF(Py_True);
				SET_TOP(Py_True);
				continue;
			}
			else if (err > 0) {
				Py_INCREF(Py_False);
				SET_TOP(Py_False);
				err = 0;
				continue;
			}
			STACKADJ(-1);
			break;

		case UNARY_CONVERT:
			v = TOP();
			x = PyObject_Repr(v);
			Py_DECREF(v);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case UNARY_INVERT:
			v = TOP();
			x = PyNumber_Invert(v);
			Py_DECREF(v);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_POWER:
			w = POP();
			v = TOP();
			x = PyNumber_Power(v, w, Py_None);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_MULTIPLY:
			w = POP();
			v = TOP();
			x = PyNumber_Multiply(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_DIVIDE:
			if (!_Py_QnewFlag) {
				w = POP();
				v = TOP();
				x = PyNumber_Divide(v, w);
				Py_DECREF(v);
				Py_DECREF(w);
				SET_TOP(x);
				if (x != NULL) continue;
				break;
			}
			/* -Qnew is in effect:	fall through to
			   BINARY_TRUE_DIVIDE */
		case BINARY_TRUE_DIVIDE:
			w = POP();
			v = TOP();
			x = PyNumber_TrueDivide(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_FLOOR_DIVIDE:
			w = POP();
			v = TOP();
			x = PyNumber_FloorDivide(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_MODULO:
			w = POP();
			v = TOP();
			x = PyNumber_Remainder(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_ADD:
			w = POP();
			v = TOP();
			if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
				/* INLINE: int + int */
				register long a, b, i;
				a = PyInt_AS_LONG(v);
				b = PyInt_AS_LONG(w);
				i = a + b;
				if ((i^a) < 0 && (i^b) < 0)
					goto slow_add;
				x = PyInt_FromLong(i);
			}
			else if (PyString_CheckExact(v) &&
				 PyString_CheckExact(w)) {
				x = string_concatenate(v, w, f, next_instr);
				/* string_concatenate consumed the ref to v */
				goto skip_decref_vx;
			}
			else {
			  slow_add:
				x = PyNumber_Add(v, w);
			}
			Py_DECREF(v);
		  skip_decref_vx:
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_SUBTRACT:
			w = POP();
			v = TOP();
			if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
				/* INLINE: int - int */
				register long a, b, i;
				a = PyInt_AS_LONG(v);
				b = PyInt_AS_LONG(w);
				i = a - b;
				if ((i^a) < 0 && (i^~b) < 0)
					goto slow_sub;
				x = PyInt_FromLong(i);
			}
			else {
			  slow_sub:
				x = PyNumber_Subtract(v, w);
			}
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_SUBSCR:
			w = POP();
			v = TOP();
			if (PyList_CheckExact(v) && PyInt_CheckExact(w)) {
				/* INLINE: list[int] */
				Py_ssize_t i = PyInt_AsSsize_t(w);
				if (i < 0)
					i += PyList_GET_SIZE(v);
				if (i >= 0 && i < PyList_GET_SIZE(v)) {
					x = PyList_GET_ITEM(v, i);
					Py_INCREF(x);
				}
				else
					goto slow_get;
			}
			else
			  slow_get:
				x = PyObject_GetItem(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_LSHIFT:
			w = POP();
			v = TOP();
			x = PyNumber_Lshift(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_RSHIFT:
			w = POP();
			v = TOP();
			x = PyNumber_Rshift(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_AND:
			w = POP();
			v = TOP();
			x = PyNumber_And(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_XOR:
			w = POP();
			v = TOP();
			x = PyNumber_Xor(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case BINARY_OR:
			w = POP();
			v = TOP();
			x = PyNumber_Or(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case LIST_APPEND:
			w = POP();
			v = POP();
			err = PyList_Append(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			if (err == 0) {
				PREDICT(JUMP_ABSOLUTE);
				continue;
			}
			break;

		case INPLACE_POWER:
			w = POP();
			v = TOP();
			x = PyNumber_InPlacePower(v, w, Py_None);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_MULTIPLY:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceMultiply(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_DIVIDE:
			if (!_Py_QnewFlag) {
				w = POP();
				v = TOP();
				x = PyNumber_InPlaceDivide(v, w);
				Py_DECREF(v);
				Py_DECREF(w);
				SET_TOP(x);
				if (x != NULL) continue;
				break;
			}
			/* -Qnew is in effect:	fall through to
			   INPLACE_TRUE_DIVIDE */
		case INPLACE_TRUE_DIVIDE:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceTrueDivide(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_FLOOR_DIVIDE:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceFloorDivide(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_MODULO:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceRemainder(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_ADD:
			w = POP();
			v = TOP();
			if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
				/* INLINE: int + int */
				register long a, b, i;
				a = PyInt_AS_LONG(v);
				b = PyInt_AS_LONG(w);
				i = a + b;
				if ((i^a) < 0 && (i^b) < 0)
					goto slow_iadd;
				x = PyInt_FromLong(i);
			}
			else if (PyString_CheckExact(v) &&
				 PyString_CheckExact(w)) {
				x = string_concatenate(v, w, f, next_instr);
				/* string_concatenate consumed the ref to v */
				goto skip_decref_v;
			}
			else {
			  slow_iadd:
				x = PyNumber_InPlaceAdd(v, w);
			}
			Py_DECREF(v);
		  skip_decref_v:
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_SUBTRACT:
			w = POP();
			v = TOP();
			if (PyInt_CheckExact(v) && PyInt_CheckExact(w)) {
				/* INLINE: int - int */
				register long a, b, i;
				a = PyInt_AS_LONG(v);
				b = PyInt_AS_LONG(w);
				i = a - b;
				if ((i^a) < 0 && (i^~b) < 0)
					goto slow_isub;
				x = PyInt_FromLong(i);
			}
			else {
			  slow_isub:
				x = PyNumber_InPlaceSubtract(v, w);
			}
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_LSHIFT:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceLshift(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_RSHIFT:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceRshift(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_AND:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceAnd(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_XOR:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceXor(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case INPLACE_OR:
			w = POP();
			v = TOP();
			x = PyNumber_InPlaceOr(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case SLICE+0:
		case SLICE+1:
		case SLICE+2:
		case SLICE+3:
			if ((opcode-SLICE) & 2)
				w = POP();
			else
				w = NULL;
			if ((opcode-SLICE) & 1)
				v = POP();
			else
				v = NULL;
			u = TOP();
			x = apply_slice(u, v, w);
			Py_DECREF(u);
			Py_XDECREF(v);
			Py_XDECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case STORE_SLICE+0:
		case STORE_SLICE+1:
		case STORE_SLICE+2:
		case STORE_SLICE+3:
			if ((opcode-STORE_SLICE) & 2)
				w = POP();
			else
				w = NULL;
			if ((opcode-STORE_SLICE) & 1)
				v = POP();
			else
				v = NULL;
			u = POP();
			t = POP();
			err = assign_slice(u, v, w, t); /* u[v:w] = t */
			Py_DECREF(t);
			Py_DECREF(u);
			Py_XDECREF(v);
			Py_XDECREF(w);
			if (err == 0) continue;
			break;

		case DELETE_SLICE+0:
		case DELETE_SLICE+1:
		case DELETE_SLICE+2:
		case DELETE_SLICE+3:
			if ((opcode-DELETE_SLICE) & 2)
				w = POP();
			else
				w = NULL;
			if ((opcode-DELETE_SLICE) & 1)
				v = POP();
			else
				v = NULL;
			u = POP();
			err = assign_slice(u, v, w, (PyObject *)NULL);
							/* del u[v:w] */
			Py_DECREF(u);
			Py_XDECREF(v);
			Py_XDECREF(w);
			if (err == 0) continue;
			break;

		case STORE_SUBSCR:
			w = TOP();
			v = SECOND();
			u = THIRD();
			STACKADJ(-3);
			/* v[w] = u */
			err = PyObject_SetItem(v, w, u);
			Py_DECREF(u);
			Py_DECREF(v);
			Py_DECREF(w);
			if (err == 0) continue;
			break;

		case DELETE_SUBSCR:
			w = TOP();
			v = SECOND();
			STACKADJ(-2);
			/* del v[w] */
			err = PyObject_DelItem(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			if (err == 0) continue;
			break;

		case PRINT_EXPR:
			v = POP();
			w = PySys_GetObject("displayhook");
			if (w == NULL) {
				PyErr_SetString(PyExc_RuntimeError,
						"lost sys.displayhook");
				err = -1;
				x = NULL;
			}
			if (err == 0) {
				x = PyTuple_Pack(1, v);
				if (x == NULL)
					err = -1;
			}
			if (err == 0) {
				w = PyEval_CallObject(w, x);
				Py_XDECREF(w);
				if (w == NULL)
					err = -1;
			}
			Py_DECREF(v);
			Py_XDECREF(x);
			break;

		case PRINT_ITEM_TO:
			w = stream = POP();
			/* fall through to PRINT_ITEM */

		case PRINT_ITEM:
			v = POP();
			if (stream == NULL || stream == Py_None) {
				w = PySys_GetObject("stdout");
				if (w == NULL) {
					PyErr_SetString(PyExc_RuntimeError,
							"lost sys.stdout");
					err = -1;
				}
			}
			/* PyFile_SoftSpace() can exececute arbitrary code
			   if sys.stdout is an instance with a __getattr__.
			   If __getattr__ raises an exception, w will
			   be freed, so we need to prevent that temporarily. */
			Py_XINCREF(w);
			if (w != NULL && PyFile_SoftSpace(w, 0))
				err = PyFile_WriteString(" ", w);
			if (err == 0)
				err = PyFile_WriteObject(v, w, Py_PRINT_RAW);
			if (err == 0) {
			    /* XXX move into writeobject() ? */
			    if (PyString_Check(v)) {
				char *s = PyString_AS_STRING(v);
				Py_ssize_t len = PyString_GET_SIZE(v);
				if (len == 0 ||
				    !isspace(Py_CHARMASK(s[len-1])) ||
				    s[len-1] == ' ')
					PyFile_SoftSpace(w, 1);
			    }
#ifdef Py_USING_UNICODE
			    else if (PyUnicode_Check(v)) {
				Py_UNICODE *s = PyUnicode_AS_UNICODE(v);
				Py_ssize_t len = PyUnicode_GET_SIZE(v);
				if (len == 0 ||
				    !Py_UNICODE_ISSPACE(s[len-1]) ||
				    s[len-1] == ' ')
				    PyFile_SoftSpace(w, 1);
			    }
#endif
			    else
			    	PyFile_SoftSpace(w, 1);
			}
			Py_XDECREF(w);
			Py_DECREF(v);
			Py_XDECREF(stream);
			stream = NULL;
			if (err == 0)
				continue;
			break;

		case PRINT_NEWLINE_TO:
			w = stream = POP();
			/* fall through to PRINT_NEWLINE */

		case PRINT_NEWLINE:
			if (stream == NULL || stream == Py_None) {
				w = PySys_GetObject("stdout");
				if (w == NULL)
					PyErr_SetString(PyExc_RuntimeError,
							"lost sys.stdout");
			}
			if (w != NULL) {
				/* w.write() may replace sys.stdout, so we
				 * have to keep our reference to it */
				Py_INCREF(w);
				err = PyFile_WriteString("\n", w);
				if (err == 0)
					PyFile_SoftSpace(w, 0);
				Py_DECREF(w);
			}
			Py_XDECREF(stream);
			stream = NULL;
			break;


#ifdef CASE_TOO_BIG
		default: switch (opcode) {
#endif
		case RAISE_VARARGS:
			u = v = w = NULL;
			switch (oparg) {
			case 3:
				u = POP(); /* traceback */
				/* Fallthrough */
			case 2:
				v = POP(); /* value */
				/* Fallthrough */
			case 1:
				w = POP(); /* exc */
			case 0: /* Fallthrough */
				why = do_raise(w, v, u);
				break;
			default:
				PyErr_SetString(PyExc_SystemError,
					   "bad RAISE_VARARGS oparg");
				why = WHY_EXCEPTION;
				break;
			}
			break;

		case LOAD_LOCALS:
			if ((x = f->f_locals) != NULL) {
				Py_INCREF(x);
				PUSH(x);
				continue;
			}
			PyErr_SetString(PyExc_SystemError, "no locals");
			break;

		case RETURN_VALUE:
			retval = POP();
			why = WHY_RETURN;
			goto fast_block_end;

		case YIELD_VALUE:
			retval = POP();
			f->f_stacktop = stack_pointer;
			why = WHY_YIELD;
			goto fast_yield;

		case EXEC_STMT:
			w = TOP();
			v = SECOND();
			u = THIRD();
			STACKADJ(-3);
			READ_TIMESTAMP(intr0);
			err = exec_statement(f, u, v, w);
			READ_TIMESTAMP(intr1);
			Py_DECREF(u);
			Py_DECREF(v);
			Py_DECREF(w);
			break;

		case POP_BLOCK:
			{
				PyTryBlock *b = PyFrame_BlockPop(f);
				while (STACK_LEVEL() > b->b_level) {
					v = POP();
					Py_DECREF(v);
				}
			}
			continue;

		PREDICTED(END_FINALLY);
		case END_FINALLY:
			v = POP();
			if (PyInt_Check(v)) {
				why = (enum why_code) PyInt_AS_LONG(v);
				assert(why != WHY_YIELD);
				if (why == WHY_RETURN ||
				    why == WHY_CONTINUE)
					retval = POP();
			}
			else if (PyExceptionClass_Check(v) ||
				 PyString_Check(v)) {
				w = POP();
				u = POP();
				PyErr_Restore(v, w, u);
				why = WHY_RERAISE;
				break;
			}
			else if (v != Py_None) {
				PyErr_SetString(PyExc_SystemError,
					"'finally' pops bad exception");
				why = WHY_EXCEPTION;
			}
			Py_DECREF(v);
			break;

		case BUILD_CLASS:
			u = TOP();
			v = SECOND();
			w = THIRD();
			STACKADJ(-2);
			x = build_class(u, v, w);
			SET_TOP(x);
			Py_DECREF(u);
			Py_DECREF(v);
			Py_DECREF(w);
			break;

		case STORE_NAME:
			w = GETITEM(names, oparg);
			v = POP();
			if ((x = f->f_locals) != NULL) {
				if (PyDict_CheckExact(x))
					err = PyDict_SetItem(x, w, v);
				else
					err = PyObject_SetItem(x, w, v);
				Py_DECREF(v);
				if (err == 0) continue;
				break;
			}
			PyErr_Format(PyExc_SystemError,
				     "no locals found when storing %s",
				     PyObject_REPR(w));
			break;

		case DELETE_NAME:
			w = GETITEM(names, oparg);
			if ((x = f->f_locals) != NULL) {
				if ((err = PyObject_DelItem(x, w)) != 0)
					format_exc_check_arg(PyExc_NameError,
							     NAME_ERROR_MSG,
							     w);
				break;
			}
			PyErr_Format(PyExc_SystemError,
				     "no locals when deleting %s",
				     PyObject_REPR(w));
			break;

		PREDICTED_WITH_ARG(UNPACK_SEQUENCE);
		case UNPACK_SEQUENCE:
			v = POP();
			if (PyTuple_CheckExact(v) &&
			    PyTuple_GET_SIZE(v) == oparg) {
				PyObject **items = \
					((PyTupleObject *)v)->ob_item;
				while (oparg--) {
					w = items[oparg];
					Py_INCREF(w);
					PUSH(w);
				}
				Py_DECREF(v);
				continue;
			} else if (PyList_CheckExact(v) &&
				   PyList_GET_SIZE(v) == oparg) {
				PyObject **items = \
					((PyListObject *)v)->ob_item;
				while (oparg--) {
					w = items[oparg];
					Py_INCREF(w);
					PUSH(w);
				}
			} else if (unpack_iterable(v, oparg,
						   stack_pointer + oparg)) {
				stack_pointer += oparg;
			} else {
				/* unpack_iterable() raised an exception */
				why = WHY_EXCEPTION;
			}
			Py_DECREF(v);
			break;

		case STORE_ATTR:
			w = GETITEM(names, oparg);
			v = TOP();
			u = SECOND();
			STACKADJ(-2);
			err = PyObject_SetAttr(v, w, u); /* v.w = u */
			Py_DECREF(v);
			Py_DECREF(u);
			if (err == 0) continue;
			break;

		case DELETE_ATTR:
			w = GETITEM(names, oparg);
			v = POP();
			err = PyObject_SetAttr(v, w, (PyObject *)NULL);
							/* del v.w */
			Py_DECREF(v);
			break;

		case STORE_GLOBAL:
			w = GETITEM(names, oparg);
			v = POP();
			err = PyDict_SetItem(f->f_globals, w, v);
			Py_DECREF(v);
			if (err == 0) continue;
			break;

		case DELETE_GLOBAL:
			w = GETITEM(names, oparg);
			if ((err = PyDict_DelItem(f->f_globals, w)) != 0)
				format_exc_check_arg(
				    PyExc_NameError, GLOBAL_NAME_ERROR_MSG, w);
			break;

		case LOAD_NAME:
			w = GETITEM(names, oparg);
			if ((v = f->f_locals) == NULL) {
				PyErr_Format(PyExc_SystemError,
					     "no locals when loading %s",
					     PyObject_REPR(w));
				break;
			}
			if (PyDict_CheckExact(v)) {
				x = PyDict_GetItem(v, w);
				Py_XINCREF(x);
			}
			else {
				x = PyObject_GetItem(v, w);
				if (x == NULL && PyErr_Occurred()) {
					if (!PyErr_ExceptionMatches(
							PyExc_KeyError))
						break;
					PyErr_Clear();
				}
			}
			if (x == NULL) {
				x = PyDict_GetItem(f->f_globals, w);
				if (x == NULL) {
					x = PyDict_GetItem(f->f_builtins, w);
					if (x == NULL) {
						format_exc_check_arg(
							    PyExc_NameError,
							    NAME_ERROR_MSG, w);
						break;
					}
				}
				Py_INCREF(x);
			}
			PUSH(x);
			continue;

		case LOAD_GLOBAL:
			w = GETITEM(names, oparg);
			if (PyString_CheckExact(w)) {
				/* Inline the PyDict_GetItem() calls.
				   WARNING: this is an extreme speed hack.
				   Do not try this at home. */
				long hash = ((PyStringObject *)w)->ob_shash;
				if (hash != -1) {
					PyDictObject *d;
					PyDictEntry *e;
					d = (PyDictObject *)(f->f_globals);
					e = d->ma_lookup(d, w, hash);
					if (e == NULL) {
						x = NULL;
						break;
					}
					x = e->me_value;
					if (x != NULL) {
						Py_INCREF(x);
						PUSH(x);
						continue;
					}
					d = (PyDictObject *)(f->f_builtins);
					e = d->ma_lookup(d, w, hash);
					if (e == NULL) {
						x = NULL;
						break;
					}
					x = e->me_value;
					if (x != NULL) {
						Py_INCREF(x);
						PUSH(x);
						continue;
					}
					goto load_global_error;
				}
			}
			/* This is the un-inlined version of the code above */
			x = PyDict_GetItem(f->f_globals, w);
			if (x == NULL) {
				x = PyDict_GetItem(f->f_builtins, w);
				if (x == NULL) {
				  load_global_error:
					format_exc_check_arg(
						    PyExc_NameError,
						    GLOBAL_NAME_ERROR_MSG, w);
					break;
				}
			}
			Py_INCREF(x);
			PUSH(x);
			continue;

		case DELETE_FAST:
			x = GETLOCAL(oparg);
			if (x != NULL) {
				SETLOCAL(oparg, NULL);
				continue;
			}
			format_exc_check_arg(
				PyExc_UnboundLocalError,
				UNBOUNDLOCAL_ERROR_MSG,
				PyTuple_GetItem(co->co_varnames, oparg)
				);
			break;

		case LOAD_CLOSURE:
			x = freevars[oparg];
			Py_INCREF(x);
			PUSH(x);
			if (x != NULL) continue;
			break;

		case LOAD_DEREF:
			x = freevars[oparg];
			w = PyCell_Get(x);
			if (w != NULL) {
				PUSH(w);
				continue;
			}
			err = -1;
			/* Don't stomp existing exception */
			if (PyErr_Occurred())
				break;
			if (oparg < PyTuple_GET_SIZE(co->co_cellvars)) {
				v = PyTuple_GET_ITEM(co->co_cellvars,
						       oparg);
			       format_exc_check_arg(
				       PyExc_UnboundLocalError,
				       UNBOUNDLOCAL_ERROR_MSG,
				       v);
			} else {
				v = PyTuple_GET_ITEM(co->co_freevars, oparg -
					PyTuple_GET_SIZE(co->co_cellvars));
				format_exc_check_arg(PyExc_NameError,
						     UNBOUNDFREE_ERROR_MSG, v);
			}
			break;

		case STORE_DEREF:
			w = POP();
			x = freevars[oparg];
			PyCell_Set(x, w);
			Py_DECREF(w);
			continue;

		case BUILD_TUPLE:
			x = PyTuple_New(oparg);
			if (x != NULL) {
				for (; --oparg >= 0;) {
					w = POP();
					PyTuple_SET_ITEM(x, oparg, w);
				}
				PUSH(x);
				continue;
			}
			break;

		case BUILD_LIST:
			x =  PyList_New(oparg);
			if (x != NULL) {
				for (; --oparg >= 0;) {
					w = POP();
					PyList_SET_ITEM(x, oparg, w);
				}
				PUSH(x);
				continue;
			}
			break;

		case BUILD_MAP:
			x = _PyDict_NewPresized((Py_ssize_t)oparg);
			PUSH(x);
			if (x != NULL) continue;
			break;

		case STORE_MAP:
			w = TOP();     /* key */
			u = SECOND();  /* value */
			v = THIRD();   /* dict */
			STACKADJ(-2);
			assert (PyDict_CheckExact(v));
			err = PyDict_SetItem(v, w, u);  /* v[w] = u */
			Py_DECREF(u);
			Py_DECREF(w);
			if (err == 0) continue;
			break;

		case LOAD_ATTR:
			w = GETITEM(names, oparg);
			v = TOP();
			x = PyObject_GetAttr(v, w);
			Py_DECREF(v);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case COMPARE_OP:
			w = POP();
			v = TOP();
			if (PyInt_CheckExact(w) && PyInt_CheckExact(v)) {
				/* INLINE: cmp(int, int) */
				register long a, b;
				register int res;
				a = PyInt_AS_LONG(v);
				b = PyInt_AS_LONG(w);
				switch (oparg) {
				case PyCmp_LT: res = a <  b; break;
				case PyCmp_LE: res = a <= b; break;
				case PyCmp_EQ: res = a == b; break;
				case PyCmp_NE: res = a != b; break;
				case PyCmp_GT: res = a >  b; break;
				case PyCmp_GE: res = a >= b; break;
				case PyCmp_IS: res = v == w; break;
				case PyCmp_IS_NOT: res = v != w; break;
				default: goto slow_compare;
				}
				x = res ? Py_True : Py_False;
				Py_INCREF(x);
			}
			else {
			  slow_compare:
				x = cmp_outcome(oparg, v, w);
			}
			Py_DECREF(v);
			Py_DECREF(w);
			SET_TOP(x);
			if (x == NULL) break;
			PREDICT(JUMP_IF_FALSE);
			PREDICT(JUMP_IF_TRUE);
			continue;

		case IMPORT_NAME:
			w = GETITEM(names, oparg);
			x = PyDict_GetItemString(f->f_builtins, "__import__");
			if (x == NULL) {
				PyErr_SetString(PyExc_ImportError,
						"__import__ not found");
				break;
			}
			Py_INCREF(x);
			v = POP();
			u = TOP();
			if (PyInt_AsLong(u) != -1 || PyErr_Occurred())
				w = PyTuple_Pack(5,
					    w,
					    f->f_globals,
					    f->f_locals == NULL ?
						  Py_None : f->f_locals,
					    v,
					    u);
			else
				w = PyTuple_Pack(4,
					    w,
					    f->f_globals,
					    f->f_locals == NULL ?
						  Py_None : f->f_locals,
					    v);
			Py_DECREF(v);
			Py_DECREF(u);
			if (w == NULL) {
				u = POP();
				Py_DECREF(x);
				x = NULL;
				break;
			}
			READ_TIMESTAMP(intr0);
			v = x;
			x = PyEval_CallObject(v, w);
			Py_DECREF(v);
			READ_TIMESTAMP(intr1);
			Py_DECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case IMPORT_STAR:
			v = POP();
			PyFrame_FastToLocals(f);
			if ((x = f->f_locals) == NULL) {
				PyErr_SetString(PyExc_SystemError,
					"no locals found during 'import *'");
				break;
			}
			READ_TIMESTAMP(intr0);
			err = import_all_from(x, v);
			READ_TIMESTAMP(intr1);
			PyFrame_LocalsToFast(f, 0);
			Py_DECREF(v);
			if (err == 0) continue;
			break;

		case IMPORT_FROM:
			w = GETITEM(names, oparg);
			v = TOP();
			READ_TIMESTAMP(intr0);
			x = import_from(v, w);
			READ_TIMESTAMP(intr1);
			PUSH(x);
			if (x != NULL) continue;
			break;

		case JUMP_FORWARD:
			JUMPBY(oparg);
			goto fast_next_opcode;

		PREDICTED_WITH_ARG(JUMP_IF_FALSE);
		case JUMP_IF_FALSE:
			w = TOP();
			if (w == Py_True) {
				PREDICT(POP_TOP);
				goto fast_next_opcode;
			}
			if (w == Py_False) {
				JUMPBY(oparg);
				goto fast_next_opcode;
			}
			err = PyObject_IsTrue(w);
			if (err > 0)
				err = 0;
			else if (err == 0)
				JUMPBY(oparg);
			else
				break;
			continue;

		PREDICTED_WITH_ARG(JUMP_IF_TRUE);
		case JUMP_IF_TRUE:
			w = TOP();
			if (w == Py_False) {
				PREDICT(POP_TOP);
				goto fast_next_opcode;
			}
			if (w == Py_True) {
				JUMPBY(oparg);
				goto fast_next_opcode;
			}
			err = PyObject_IsTrue(w);
			if (err > 0) {
				err = 0;
				JUMPBY(oparg);
			}
			else if (err == 0)
				;
			else
				break;
			continue;

		PREDICTED_WITH_ARG(JUMP_ABSOLUTE);
		case JUMP_ABSOLUTE:
			JUMPTO(oparg);
#if FAST_LOOPS
			/* Enabling this path speeds-up all while and for-loops by bypassing
			   the per-loop checks for signals.  By default, this should be turned-off
			   because it prevents detection of a control-break in tight loops like
			   "while 1: pass".  Compile with this option turned-on when you need
			   the speed-up and do not need break checking inside tight loops (ones
			   that contain only instructions ending with goto fast_next_opcode).
			*/
			goto fast_next_opcode;
#else
			continue;
#endif

		case GET_ITER:
			/* before: [obj]; after [getiter(obj)] */
			v = TOP();
			x = PyObject_GetIter(v);
			Py_DECREF(v);
			if (x != NULL) {
				SET_TOP(x);
				PREDICT(FOR_ITER);
				continue;
			}
			STACKADJ(-1);
			break;

		PREDICTED_WITH_ARG(FOR_ITER);
		case FOR_ITER:
			/* before: [iter]; after: [iter, iter()] *or* [] */
			v = TOP();
			x = (*v->ob_type->tp_iternext)(v);
			if (x != NULL) {
				PUSH(x);
				PREDICT(STORE_FAST);
				PREDICT(UNPACK_SEQUENCE);
				continue;
			}
			if (PyErr_Occurred()) {
				if (!PyErr_ExceptionMatches(
						PyExc_StopIteration))
					break;
				PyErr_Clear();
			}
			/* iterator ended normally */
 			x = v = POP();
			Py_DECREF(v);
			JUMPBY(oparg);
			continue;

		case BREAK_LOOP:
			why = WHY_BREAK;
			goto fast_block_end;

		case CONTINUE_LOOP:
			retval = PyInt_FromLong(oparg);
			if (!retval) {
				x = NULL;
				break;
			}
			why = WHY_CONTINUE;
			goto fast_block_end;

		case SETUP_LOOP:
		case SETUP_EXCEPT:
		case SETUP_FINALLY:
			/* NOTE: If you add any new block-setup opcodes that
			   are not try/except/finally handlers, you may need
			   to update the PyGen_NeedsFinalizing() function.
			   */

			PyFrame_BlockSetup(f, opcode, INSTR_OFFSET() + oparg,
					   STACK_LEVEL());
			continue;

		case WITH_CLEANUP:
		{
			/* At the top of the stack are 1-3 values indicating
			   how/why we entered the finally clause:
			   - TOP = None
			   - (TOP, SECOND) = (WHY_{RETURN,CONTINUE}), retval
			   - TOP = WHY_*; no retval below it
			   - (TOP, SECOND, THIRD) = exc_info()
			   Below them is EXIT, the context.__exit__ bound method.
			   In the last case, we must call
			     EXIT(TOP, SECOND, THIRD)
			   otherwise we must call
			     EXIT(None, None, None)

			   In all cases, we remove EXIT from the stack, leaving
			   the rest in the same order.

			   In addition, if the stack represents an exception,
			   *and* the function call returns a 'true' value, we
			   "zap" this information, to prevent END_FINALLY from
			   re-raising the exception.  (But non-local gotos
			   should still be resumed.)
			*/

			PyObject *exit_func;

			u = POP();
			if (u == Py_None) {
			       	exit_func = TOP();
				SET_TOP(u);
				v = w = Py_None;
			}
			else if (PyInt_Check(u)) {
				switch(PyInt_AS_LONG(u)) {
				case WHY_RETURN:
				case WHY_CONTINUE:
					/* Retval in TOP. */
					exit_func = SECOND();
					SET_SECOND(TOP());
					SET_TOP(u);
					break;
				default:
					exit_func = TOP();
					SET_TOP(u);
					break;
				}
				u = v = w = Py_None;
			}
			else {
				v = TOP();
				w = SECOND();
				exit_func = THIRD();
				SET_TOP(u);
				SET_SECOND(v);
				SET_THIRD(w);
			}
			/* XXX Not the fastest way to call it... */
			x = PyObject_CallFunctionObjArgs(exit_func, u, v, w,
							 NULL);
			if (x == NULL) {
				Py_DECREF(exit_func);
				break; /* Go to error exit */
			}
			if (u != Py_None && PyObject_IsTrue(x)) {
				/* There was an exception and a true return */
				STACKADJ(-2);
				Py_INCREF(Py_None);
				SET_TOP(Py_None);
				Py_DECREF(u);
				Py_DECREF(v);
				Py_DECREF(w);
			} else {
				/* The stack was rearranged to remove EXIT
				   above. Let END_FINALLY do its thing */
			}
			Py_DECREF(x);
			Py_DECREF(exit_func);
			PREDICT(END_FINALLY);
			break;
		}

		case CALL_FUNCTION:
		{
			PyObject **sp;
			PCALL(PCALL_ALL);
			sp = stack_pointer;
#ifdef WITH_TSC
			x = call_function(&sp, oparg, &intr0, &intr1);
#else
			x = call_function(&sp, oparg);
#endif
			stack_pointer = sp;
			PUSH(x);
			if (x != NULL)
				continue;
			break;
		}

		case CALL_FUNCTION_VAR:
		case CALL_FUNCTION_KW:
		case CALL_FUNCTION_VAR_KW:
		{
		    int na = oparg & 0xff;
		    int nk = (oparg>>8) & 0xff;
		    int flags = (opcode - CALL_FUNCTION) & 3;
		    int n = na + 2 * nk;
		    PyObject **pfunc, *func, **sp;
		    PCALL(PCALL_ALL);
		    if (flags & CALL_FLAG_VAR)
			    n++;
		    if (flags & CALL_FLAG_KW)
			    n++;
		    pfunc = stack_pointer - n - 1;
		    func = *pfunc;

		    if (PyMethod_Check(func)
			&& PyMethod_GET_SELF(func) != NULL) {
			    PyObject *self = PyMethod_GET_SELF(func);
			    Py_INCREF(self);
			    func = PyMethod_GET_FUNCTION(func);
			    Py_INCREF(func);
			    Py_DECREF(*pfunc);
			    *pfunc = self;
			    na++;
			    n++;
		    } else
			    Py_INCREF(func);
		    sp = stack_pointer;
		    READ_TIMESTAMP(intr0);
		    x = ext_do_call(func, &sp, flags, na, nk);
		    READ_TIMESTAMP(intr1);
		    stack_pointer = sp;
		    Py_DECREF(func);

		    while (stack_pointer > pfunc) {
			    w = POP();
			    Py_DECREF(w);
		    }
		    PUSH(x);
		    if (x != NULL)
			    continue;
		    break;
		}

		case MAKE_FUNCTION:
			v = POP(); /* code object */
			x = PyFunction_New(v, f->f_globals);
			Py_DECREF(v);
			/* XXX Maybe this should be a separate opcode? */
			if (x != NULL && oparg > 0) {
				v = PyTuple_New(oparg);
				if (v == NULL) {
					Py_DECREF(x);
					x = NULL;
					break;
				}
				while (--oparg >= 0) {
					w = POP();
					PyTuple_SET_ITEM(v, oparg, w);
				}
				err = PyFunction_SetDefaults(x, v);
				Py_DECREF(v);
			}
			PUSH(x);
			break;

		case MAKE_CLOSURE:
		{
			v = POP(); /* code object */
			x = PyFunction_New(v, f->f_globals);
			Py_DECREF(v);
			if (x != NULL) {
				v = POP();
				err = PyFunction_SetClosure(x, v);
				Py_DECREF(v);
			}
			if (x != NULL && oparg > 0) {
				v = PyTuple_New(oparg);
				if (v == NULL) {
					Py_DECREF(x);
					x = NULL;
					break;
				}
				while (--oparg >= 0) {
					w = POP();
					PyTuple_SET_ITEM(v, oparg, w);
				}
				err = PyFunction_SetDefaults(x, v);
				Py_DECREF(v);
			}
			PUSH(x);
			break;
		}

		case BUILD_SLICE:
			if (oparg == 3)
				w = POP();
			else
				w = NULL;
			v = POP();
			u = TOP();
			x = PySlice_New(u, v, w);
			Py_DECREF(u);
			Py_DECREF(v);
			Py_XDECREF(w);
			SET_TOP(x);
			if (x != NULL) continue;
			break;

		case EXTENDED_ARG:
			opcode = NEXTOP();
			oparg = oparg<<16 | NEXTARG();
			goto dispatch_opcode;

//////////////////////////////////////////////////////////////// py3k beg - add new opcodes here
		case SET_ADD_py3k:
			w = POP();
			v = POP();
			err = PySet_Add(v, w);
			Py_DECREF(v);
			Py_DECREF(w);
			if (err == 0) {
				PREDICT(JUMP_ABSOLUTE);
				continue;
			}
			break;

		case STORE_LOCALS_py3k:
			x = POP();
			v = f->f_locals;
			Py_XDECREF(v);
			f->f_locals = x;
			continue;

		// case LOAD_BUILD_CLASS_py3k - unsupported

		// case MAKE_BYTES_py3k - unused

		// case POP_EXCEPT_py3k - unsupported

		case UNPACK_EX_py3k:
		{
			int totalargs = 1 + (oparg & 0xFF) + (oparg >> 8);
			v = POP();

			if (unpack_iterable_py3k(v, oparg & 0xFF, oparg >> 8,
					    stack_pointer + totalargs)) {
				stack_pointer += totalargs;
			} else {
				why = WHY_EXCEPTION;
			}
			Py_DECREF(v);
			break;
		}

		case BUILD_SET_py3k:
			x = PySet_New(NULL);
			if (x != NULL) {
				for (; --oparg >= 0;) {
					w = POP();
					if (err == 0)
						err = PySet_Add(x, w);
					Py_DECREF(w);
				}
				if (err != 0) {
					Py_DECREF(x);
					break;
				}
				PUSH(x);
				continue;
			}
			break;
//////////////////////////////////////////////////////////////// py3k end

		default:
			fprintf(stderr,
				"XXX lineno: %d, opcode: %d\n",
				PyCode_Addr2Line(f->f_code, f->f_lasti),
				opcode);
			PyErr_SetString(PyExc_SystemError, "unknown opcode");
			why = WHY_EXCEPTION;
			break;

#ifdef CASE_TOO_BIG
		}
#endif

		} /* switch */

	    on_error:

		READ_TIMESTAMP(inst1);

		/* Quickly continue if no error occurred */

		if (why == WHY_NOT) {
			if (err == 0 && x != NULL) {
#ifdef CHECKEXC
				/* This check is expensive! */
				if (PyErr_Occurred())
					fprintf(stderr,
						"XXX undetected error\n");
				else {
#endif
					READ_TIMESTAMP(loop1);
					continue; /* Normal, fast path */
#ifdef CHECKEXC
				}
#endif
			}
			why = WHY_EXCEPTION;
			x = Py_None;
			err = 0;
		}

		/* Double-check exception status */

		if (why == WHY_EXCEPTION || why == WHY_RERAISE) {
			if (!PyErr_Occurred()) {
				PyErr_SetString(PyExc_SystemError,
					"error return without exception set");
				why = WHY_EXCEPTION;
			}
		}
#ifdef CHECKEXC
		else {
			/* This check is expensive! */
			if (PyErr_Occurred()) {
				char buf[128];
				sprintf(buf, "Stack unwind with exception "
					"set and why=%d", why);
				Py_FatalError(buf);
			}
		}
#endif

		/* Log traceback info if this is a real exception */

		if (why == WHY_EXCEPTION) {
			PyTraceBack_Here(f);

			if (tstate->c_tracefunc != NULL)
				call_exc_trace(tstate->c_tracefunc,
					       tstate->c_traceobj, f);
		}

		/* For the rest, treat WHY_RERAISE as WHY_EXCEPTION */

		if (why == WHY_RERAISE)
			why = WHY_EXCEPTION;

		/* Unwind stacks if a (pseudo) exception occurred */

fast_block_end:
		while (why != WHY_NOT && f->f_iblock > 0) {
			PyTryBlock *b = PyFrame_BlockPop(f);

			assert(why != WHY_YIELD);
			if (b->b_type == SETUP_LOOP && why == WHY_CONTINUE) {
				/* For a continue inside a try block,
				   don't pop the block for the loop. */
				PyFrame_BlockSetup(f, b->b_type, b->b_handler,
						   b->b_level);
				why = WHY_NOT;
				JUMPTO(PyInt_AS_LONG(retval));
				Py_DECREF(retval);
				break;
			}

			while (STACK_LEVEL() > b->b_level) {
				v = POP();
				Py_XDECREF(v);
			}
			if (b->b_type == SETUP_LOOP && why == WHY_BREAK) {
				why = WHY_NOT;
				JUMPTO(b->b_handler);
				break;
			}
			if (b->b_type == SETUP_FINALLY ||
			    (b->b_type == SETUP_EXCEPT &&
			     why == WHY_EXCEPTION)) {
				if (why == WHY_EXCEPTION) {
					PyObject *exc, *val, *tb;
					PyErr_Fetch(&exc, &val, &tb);
					if (val == NULL) {
						val = Py_None;
						Py_INCREF(val);
					}
					/* Make the raw exception data
					   available to the handler,
					   so a program can emulate the
					   Python main loop.  Don't do
					   this for 'finally'. */
					if (b->b_type == SETUP_EXCEPT) {
						PyErr_NormalizeException(
							&exc, &val, &tb);
						set_exc_info(tstate,
							     exc, val, tb);
					}
					if (tb == NULL) {
						Py_INCREF(Py_None);
						PUSH(Py_None);
					} else
						PUSH(tb);
					PUSH(val);
					PUSH(exc);
				}
				else {
					if (why & (WHY_RETURN | WHY_CONTINUE))
						PUSH(retval);
					v = PyInt_FromLong((long)why);
					PUSH(v);
				}
				why = WHY_NOT;
				JUMPTO(b->b_handler);
				break;
			}
		} /* unwind stack */

		/* End the loop if we still have an error (or return) */

		if (why != WHY_NOT)
			break;
		READ_TIMESTAMP(loop1);

	} /* main loop */

	assert(why != WHY_YIELD);
	/* Pop remaining stack entries. */
	while (!EMPTY()) {
		v = POP();
		Py_XDECREF(v);
	}

	if (why != WHY_RETURN)
		retval = NULL;

fast_yield:
	if (tstate->use_tracing) {
		if (tstate->c_tracefunc) {
			if (why == WHY_RETURN || why == WHY_YIELD) {
				if (call_trace(tstate->c_tracefunc,
					       tstate->c_traceobj, f,
					       PyTrace_RETURN, retval)) {
					Py_XDECREF(retval);
					retval = NULL;
					why = WHY_EXCEPTION;
				}
			}
			else if (why == WHY_EXCEPTION) {
				call_trace_protected(tstate->c_tracefunc,
						     tstate->c_traceobj, f,
						     PyTrace_RETURN, NULL);
			}
		}
		if (tstate->c_profilefunc) {
			if (why == WHY_EXCEPTION)
				call_trace_protected(tstate->c_profilefunc,
						     tstate->c_profileobj, f,
						     PyTrace_RETURN, NULL);
			else if (call_trace(tstate->c_profilefunc,
					    tstate->c_profileobj, f,
					    PyTrace_RETURN, retval)) {
				Py_XDECREF(retval);
				retval = NULL;
				why = WHY_EXCEPTION;
			}
		}
	}

	if (tstate->frame->f_exc_type != NULL)
		reset_exc_info(tstate);
	else {
		assert(tstate->frame->f_exc_value == NULL);
		assert(tstate->frame->f_exc_traceback == NULL);
	}

	/* pop frame */
exit_eval_frame:
	Py_LeaveRecursiveCall();
	tstate->frame = f->f_back;

	return retval;
}

static PyObject *
PyEval_EvalCodeEx_py3k(PyCodeObject *co, PyObject *globals, PyObject *locals,
	   PyObject **args, int argcount, PyObject **kws, int kwcount,
	   PyObject **defs, int defcount, PyObject *closure)
{
	register PyFrameObject *f;
	register PyObject *retval = NULL;
	register PyObject **fastlocals, **freevars;
	PyThreadState *tstate = PyThreadState_GET();
	PyObject *x, *u;

	if (globals == NULL) {
		PyErr_SetString(PyExc_SystemError,
				"PyEval_EvalCodeEx: NULL globals");
		return NULL;
	}

	assert(tstate != NULL);
	assert(globals != NULL);
	f = PyFrame_New(tstate, co, globals, locals);
	if (f == NULL)
		return NULL;

	fastlocals = f->f_localsplus;
	freevars = f->f_localsplus + co->co_nlocals;

	if (co->co_argcount > 0 ||
	    co->co_flags & (CO_VARARGS | CO_VARKEYWORDS)) {
		int i;
		int n = argcount;
		PyObject *kwdict = NULL;
		if (co->co_flags & CO_VARKEYWORDS) {
			kwdict = PyDict_New();
			if (kwdict == NULL)
				goto fail;
			i = co->co_argcount;
			if (co->co_flags & CO_VARARGS)
				i++;
			SETLOCAL(i, kwdict);
		}
		if (argcount > co->co_argcount) {
			if (!(co->co_flags & CO_VARARGS)) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() takes %s %d "
				    "%sargument%s (%d given)",
				    PyString_AsString(co->co_name),
				    defcount ? "at most" : "exactly",
				    co->co_argcount,
				    kwcount ? "non-keyword " : "",
				    co->co_argcount == 1 ? "" : "s",
				    argcount);
				goto fail;
			}
			n = co->co_argcount;
		}
		for (i = 0; i < n; i++) {
			x = args[i];
			Py_INCREF(x);
			SETLOCAL(i, x);
		}
		if (co->co_flags & CO_VARARGS) {
			u = PyTuple_New(argcount - n);
			if (u == NULL)
				goto fail;
			SETLOCAL(co->co_argcount, u);
			for (i = n; i < argcount; i++) {
				x = args[i];
				Py_INCREF(x);
				PyTuple_SET_ITEM(u, i-n, x);
			}
		}
		for (i = 0; i < kwcount; i++) {
			PyObject **co_varnames;
			PyObject *keyword = kws[2*i];
			PyObject *value = kws[2*i + 1];
			int j;
			if (keyword == NULL || !PyString_Check(keyword)) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() keywords must be strings",
				    PyString_AsString(co->co_name));
				goto fail;
			}
			/* Speed hack: do raw pointer compares. As names are
			   normally interned this should almost always hit. */
			co_varnames = PySequence_Fast_ITEMS(co->co_varnames);
			for (j = 0; j < co->co_argcount; j++) {
				PyObject *nm = co_varnames[j];
				if (nm == keyword)
					goto kw_found;
			}
			/* Slow fallback, just in case */
			for (j = 0; j < co->co_argcount; j++) {
				PyObject *nm = co_varnames[j];
				int cmp = PyObject_RichCompareBool(
					keyword, nm, Py_EQ);
				if (cmp > 0)
					goto kw_found;
				else if (cmp < 0)
					goto fail;
			}
			/* Check errors from Compare */
			if (PyErr_Occurred())
				goto fail;
			if (j >= co->co_argcount) {
				if (kwdict == NULL) {
					PyErr_Format(PyExc_TypeError,
					    "%.200s() got an unexpected "
					    "keyword argument '%.400s'",
					    PyString_AsString(co->co_name),
					    PyString_AsString(keyword));
					goto fail;
				}
				PyDict_SetItem(kwdict, keyword, value);
				continue;
			}
kw_found:
			if (GETLOCAL(j) != NULL) {
				PyErr_Format(PyExc_TypeError,
						"%.200s() got multiple "
						"values for keyword "
						"argument '%.400s'",
						PyString_AsString(co->co_name),
						PyString_AsString(keyword));
				goto fail;
			}
			Py_INCREF(value);
			SETLOCAL(j, value);
		}
		if (argcount < co->co_argcount) {
			int m = co->co_argcount - defcount;
			for (i = argcount; i < m; i++) {
				if (GETLOCAL(i) == NULL) {
					PyErr_Format(PyExc_TypeError,
					    "%.200s() takes %s %d "
					    "%sargument%s (%d given)",
					    PyString_AsString(co->co_name),
					    ((co->co_flags & CO_VARARGS) ||
					     defcount) ? "at least"
						       : "exactly",
					    m, kwcount ? "non-keyword " : "",
					    m == 1 ? "" : "s", i);
					goto fail;
				}
			}
			if (n > m)
				i = n - m;
			else
				i = 0;
			for (; i < defcount; i++) {
				if (GETLOCAL(m+i) == NULL) {
					PyObject *def = defs[i];
					Py_INCREF(def);
					SETLOCAL(m+i, def);
				}
			}
		}
	}
	else {
		if (argcount > 0 || kwcount > 0) {
			PyErr_Format(PyExc_TypeError,
				     "%.200s() takes no arguments (%d given)",
				     PyString_AsString(co->co_name),
				     argcount + kwcount);
			goto fail;
		}
	}
	/* Allocate and initialize storage for cell vars, and copy free
	   vars into frame.  This isn't too efficient right now. */
	if (PyTuple_GET_SIZE(co->co_cellvars)) {
		int i, j, nargs, found;
		char *cellname, *argname;
		PyObject *c;

		nargs = co->co_argcount;
		if (co->co_flags & CO_VARARGS)
			nargs++;
		if (co->co_flags & CO_VARKEYWORDS)
			nargs++;

		/* Initialize each cell var, taking into account
		   cell vars that are initialized from arguments.

		   Should arrange for the compiler to put cellvars
		   that are arguments at the beginning of the cellvars
		   list so that we can march over it more efficiently?
		*/
		for (i = 0; i < PyTuple_GET_SIZE(co->co_cellvars); ++i) {
			cellname = PyString_AS_STRING(
				PyTuple_GET_ITEM(co->co_cellvars, i));
			found = 0;
			for (j = 0; j < nargs; j++) {
				argname = PyString_AS_STRING(
					PyTuple_GET_ITEM(co->co_varnames, j));
				if (strcmp(cellname, argname) == 0) {
					c = PyCell_New(GETLOCAL(j));
					if (c == NULL)
						goto fail;
					GETLOCAL(co->co_nlocals + i) = c;
					found = 1;
					break;
				}
			}
			if (found == 0) {
				c = PyCell_New(NULL);
				if (c == NULL)
					goto fail;
				SETLOCAL(co->co_nlocals + i, c);
			}
		}
	}
	if (PyTuple_GET_SIZE(co->co_freevars)) {
		int i;
		for (i = 0; i < PyTuple_GET_SIZE(co->co_freevars); ++i) {
			PyObject *o = PyTuple_GET_ITEM(closure, i);
			Py_INCREF(o);
			freevars[PyTuple_GET_SIZE(co->co_cellvars) + i] = o;
		}
	}

	if (co->co_flags & CO_GENERATOR) {
		/* Don't need to keep the reference to f_back, it will be set
		 * when the generator is resumed. */
		Py_XDECREF(f->f_back);
		f->f_back = NULL;

		PCALL(PCALL_GENERATOR);

		/* Create a new generator that owns the ready to run frame
		 * and return that as the value. */
		return PyGen_New(f);
	}

	retval = PyEval_EvalFrameEx_py3k(f,0);

fail: /* Jump here from prelude on failure */

	/* decref'ing the frame can cause __del__ methods to get invoked,
	   which can call back into Python.  While we're done with the
	   current Python frame (f), the associated C stack is still in use,
	   so recursion_depth must be boosted for the duration.
	*/
	assert(tstate != NULL);
	++tstate->recursion_depth;
	Py_DECREF(f);
	--tstate->recursion_depth;
	return retval;
}
