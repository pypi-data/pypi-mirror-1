#include "Python.h"
#include "Python-ast.h"

#include "node.h"
#include "code.h"
#include "eval.h"

#include <ctype.h>

//////////////////////////////////////////////////////////////// py3k beg - header
#define py3k_PyUnicode_Check(x) PyString_Check(x)
#define py3k_PyUnicode_AS_UNICODE PyString_AS_STRING

static PyObject *compile(PyObject *str, char *filename, char *mode, int flags, int dont_inherit) {
	PyObject *func = PyDict_GetItemString(PyEval_GetBuiltins(), "_compile"); // get function
	if (!(func && PyCallable_Check(func))) {PyErr_SetString(PyExc_NotImplementedError, "py3k_compile"); return NULL;}
	return PyObject_CallFunction(func, "Ossii", str, filename, mode, flags, dont_inherit);
}
//////////////////////////////////////////////////////////////// py3k end

static PyObject *
builtin___build_class__(PyObject *self, PyObject *args, PyObject *kwds)
{
	PyObject *func, *name, *bases, *mkw, *meta, *prep, *ns, *cell;
	PyObject *cls = NULL;
	Py_ssize_t nargs, nbases;

	assert(args != NULL);
	if (!PyTuple_Check(args)) {
		PyErr_SetString(PyExc_TypeError,
				"__build_class__: args is not a tuple");
		return NULL;
	}
	nargs = PyTuple_GET_SIZE(args);
	if (nargs < 2) {
		PyErr_SetString(PyExc_TypeError,
				"__build_class__: not enough arguments");
		return NULL;
	}
	func = PyTuple_GET_ITEM(args, 0); /* Better be callable */
	name = PyTuple_GET_ITEM(args, 1);
	if (!py3k_PyUnicode_Check(name)) {
		PyErr_SetString(PyExc_TypeError,
				"__build_class__: name is not a string");
		return NULL;
	}
	bases = PyTuple_GetSlice(args, 2, nargs);
	if (bases == NULL)
		return NULL;
	nbases = nargs - 2;

	if (kwds == NULL) {
		meta = NULL;
                mkw = NULL;
        }
	else {
		mkw = PyDict_Copy(kwds); /* Don't modify kwds passed in! */
		if (mkw == NULL) {
			Py_DECREF(bases);
			return NULL;
		}
		meta = PyDict_GetItemString(mkw, "metaclass");
		if (meta != NULL) {
			Py_INCREF(meta);
			if (PyDict_DelItemString(mkw, "metaclass") < 0) {
				Py_DECREF(meta);
				Py_DECREF(mkw);
				Py_DECREF(bases);
				return NULL;
			}
		}
	}
	if (meta == NULL) {
		if (PyTuple_GET_SIZE(bases) == 0)
			meta = (PyObject *) (&PyType_Type);
		else {
			PyObject *base0 = PyTuple_GET_ITEM(bases, 0);
			meta = (PyObject *) (base0->ob_type);
		}
		Py_INCREF(meta);
	}
	prep = PyObject_GetAttrString(meta, "__prepare__");
	if (prep == NULL) {
		PyErr_Clear();
		ns = PyDict_New();
	}
	else {
		PyObject *pargs = Py_BuildValue("OO", name, bases);
		if (pargs == NULL) {
			Py_DECREF(prep);
			Py_DECREF(meta);
			Py_XDECREF(mkw);
			Py_DECREF(bases);
			return NULL;
		}
		ns = PyEval_CallObjectWithKeywords(prep, pargs, mkw);
		Py_DECREF(pargs);
		Py_DECREF(prep);
		if (ns == NULL) {
			Py_DECREF(meta);
			Py_XDECREF(mkw);
			Py_DECREF(bases);
			return NULL;
		}
	}
	cell = PyObject_CallFunctionObjArgs(func, ns, NULL);
	if (cell != NULL) {
		PyObject *margs;
		margs = Py_BuildValue("OOO", name, bases, ns);
		if (margs != NULL) {
			cls = PyEval_CallObjectWithKeywords(meta, margs, mkw);
			Py_DECREF(margs);
		}
		if (cls != NULL && PyCell_Check(cell)) {
			Py_INCREF(cls);
			PyCell_SET(cell, cls);
		}
		Py_DECREF(cell);
	}
	Py_DECREF(ns);
	Py_DECREF(meta);
	Py_XDECREF(mkw);
	Py_DECREF(bases);
	return cls;
}

PyDoc_STRVAR(build_class_doc,
"__build_class__(func, name, *bases, metaclass=None, **kwds) -> class\n\
\n\
Internal helper function used by the class statement.");

static PyObject *
builtin_compile(PyObject *self, PyObject *args, PyObject *kwds)
{
	char *str;
	char *filename;
	char *startstr;
	int mode = -1;
	int dont_inherit = 0;
	int supplied_flags = 0;
	PyCompilerFlags cf;
	PyObject *cmd;
	static char *kwlist[] = {"source", "filename", "mode", "flags",
				 "dont_inherit", NULL};
	// int start[] = {Py_file_input, Py_eval_input, Py_single_input};

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "Oss|ii:compile",
					 kwlist, &cmd, &filename, &startstr,
					 &supplied_flags, &dont_inherit))
		return NULL;

	cf.cf_flags = supplied_flags | PyCF_SOURCE_IS_UTF8;

	if (supplied_flags &
	    ~(PyCF_MASK | PyCF_MASK_OBSOLETE | PyCF_DONT_IMPLY_DEDENT | PyCF_ONLY_AST))
	{
		PyErr_SetString(PyExc_ValueError,
				"compile(): unrecognised flags");
		return NULL;
	}
	/* XXX Warn if (supplied_flags & PyCF_MASK_OBSOLETE) != 0? */

	if (!dont_inherit) {
		PyEval_MergeCompilerFlags(&cf);
	}

	if (strcmp(startstr, "exec") == 0)
		mode = 0;
	else if (strcmp(startstr, "eval") == 0)
		mode = 1;
	else if (strcmp(startstr, "single") == 0)
		mode = 2;
	else {
		PyErr_SetString(PyExc_ValueError,
				"compile() arg 3 must be 'exec', 'eval' or 'single'");
		return NULL;
	}

	if (PyAST_Check(cmd)) {
		PyObject *result;
		if (supplied_flags & PyCF_ONLY_AST) {
			Py_INCREF(cmd);
			result = cmd;
		}
		else {
			PyArena *arena;
			mod_ty mod;

			arena = PyArena_New();
			mod = PyAST_obj2mod(cmd, arena, mode);
			if (mod == NULL) {
				PyArena_Free(arena);
				return NULL;
			}
			result = (PyObject*)PyAST_Compile(mod, filename,
							  &cf, arena);
			PyArena_Free(arena);
		}
		return result;
	}

	return compile(cmd, filename, startstr, supplied_flags, dont_inherit); // py3k
}

PyDoc_STRVAR(compile_doc,
"compile(source, filename, mode[, flags[, dont_inherit]]) -> code object\n\
\n\
Compile the source string (a Python module, statement or expression)\n\
into a code object that can be executed by exec() or eval().\n\
The filename will be used for run-time error messages.\n\
The mode must be 'exec' to compile a module, 'single' to compile a\n\
single (interactive) statement, or 'eval' to compile an expression.\n\
The flags argument, if present, controls which future statements influence\n\
the compilation of the code.\n\
The dont_inherit argument, if non-zero, stops the compilation inheriting\n\
the effects of any future statements in effect in the code calling\n\
compile; if absent or zero these statements do influence the compilation,\n\
in addition to any features explicitly specified.");

static PyObject *
builtin_eval(PyObject *self, PyObject *args)
{
	PyObject *cmd;
	// PyObject *cmd, *result, *tmp = NULL;
	PyObject *globals = Py_None, *locals = Py_None;
	// char *str;
	// PyCompilerFlags cf;

	if (!PyArg_UnpackTuple(args, "eval", 1, 3, &cmd, &globals, &locals))
		return NULL;
	if (locals != Py_None && !PyMapping_Check(locals)) {
		PyErr_SetString(PyExc_TypeError, "locals must be a mapping");
		return NULL;
	}
	if (globals != Py_None && !PyDict_Check(globals)) {
		PyErr_SetString(PyExc_TypeError, PyMapping_Check(globals) ?
			"globals must be a real dict; try eval(expr, {}, mapping)"
			: "globals must be a dict");
		return NULL;
	}
	if (globals == Py_None) {
		globals = PyEval_GetGlobals();
		if (locals == Py_None)
			locals = PyEval_GetLocals();
	}
	else if (locals == Py_None)
		locals = globals;

	if (globals == NULL || locals == NULL) {
		PyErr_SetString(PyExc_TypeError, 
			"eval must be given globals and locals "
			"when called without a frame");
		return NULL;
	}

	if (PyDict_GetItemString(globals, "__builtins__") == NULL) {
		if (PyDict_SetItemString(globals, "__builtins__",
					 PyEval_GetBuiltins()) != 0)
			return NULL;
	}

	if (!PyCode_Check(cmd)) { // py3k
		if((cmd = compile(cmd, "", "eval", 0, 0)) == NULL) return NULL; // py3k
	} // py3k

	// if (PyCode_Check(cmd)) {
		if (PyCode_GetNumFree((PyCodeObject *)cmd) > 0) {
			PyErr_SetString(PyExc_TypeError,
		"code object passed to eval() may not contain free variables");
			return NULL;
		}
		return PyEval_EvalCode((PyCodeObject *) cmd, globals, locals);
	// }
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

static PyObject *
builtin_exec(PyObject *self, PyObject *args)
{
	PyObject *v;
	PyObject *prog, *globals = Py_None, *locals = Py_None;
	int plain = 0;

	if (!PyArg_ParseTuple(args, "O|OO:exec", &prog, &globals, &locals))
		return NULL;
	
	if (globals == Py_None) {
		globals = PyEval_GetGlobals();
		if (locals == Py_None) {
			locals = PyEval_GetLocals();
			plain = 1;
		}
		if (!globals || !locals) {
			PyErr_SetString(PyExc_SystemError,
					"globals and locals cannot be NULL");
			return NULL;
		}
	}
	else if (locals == Py_None)
		locals = globals;

	if (!PyDict_Check(globals)) {
		PyErr_Format(PyExc_TypeError, "exec() arg 2 must be a dict, not %.100s",
			     globals->ob_type->tp_name);
		return NULL;
	}
	if (!PyMapping_Check(locals)) {
		PyErr_Format(PyExc_TypeError,
		    "arg 3 must be a mapping or None, not %.100s",
		    locals->ob_type->tp_name);
		return NULL;
	}
	if (PyDict_GetItemString(globals, "__builtins__") == NULL) {
		if (PyDict_SetItemString(globals, "__builtins__",
					 PyEval_GetBuiltins()) != 0)
			return NULL;
	}

	if (!PyCode_Check(prog)) { // py3k
		if((prog = compile(prog, "", "exec", 0, 0)) == NULL) return NULL; // py3k
	} // py3k

	// if (PyCode_Check(prog)) {
		if (PyCode_GetNumFree((PyCodeObject *)prog) > 0) {
			PyErr_SetString(PyExc_TypeError,
				"code object passed to exec() may not "
				"contain free variables");
			return NULL;
		}
		v = PyEval_EvalCode((PyCodeObject *) prog, globals, locals);
	// }
	if (v == NULL)
		return NULL;
	Py_DECREF(v);
	Py_RETURN_NONE;
}

PyDoc_STRVAR(exec_doc,
"exec(object[, globals[, locals]])\n\
\n\
Read and execute code from a object, which can be a string, a code\n\
object or a file object.\n\
The globals and locals are dictionaries, defaulting to the current\n\
globals and locals.  If only globals is given, locals defaults to it.");

static PyMethodDef builtin_methods[] = {
 	{"__build_class__", (PyCFunction)builtin___build_class__,
         METH_VARARGS | METH_KEYWORDS, build_class_doc},
 	// {"__import__",	(PyCFunction)builtin___import__, METH_VARARGS | METH_KEYWORDS, import_doc},
 	// {"abs",		builtin_abs,        METH_O, abs_doc},
 	// {"all",		builtin_all,        METH_O, all_doc},
 	// {"any",		builtin_any,        METH_O, any_doc},
 	// {"ascii",	builtin_ascii,      METH_O, ascii_doc},
	// {"bin",		builtin_bin,	    METH_O, bin_doc},
 	// {"chr",		builtin_chr,        METH_VARARGS, chr_doc},
 	// {"cmp",		builtin_cmp,        METH_VARARGS, cmp_doc},
 	{"compile",	(PyCFunction)builtin_compile,    METH_VARARGS | METH_KEYWORDS, compile_doc},
 	// {"delattr",	builtin_delattr,    METH_VARARGS, delattr_doc},
 	// {"dir",		builtin_dir,        METH_VARARGS, dir_doc},
 	// {"divmod",	builtin_divmod,     METH_VARARGS, divmod_doc},
 	{"eval",	builtin_eval,       METH_VARARGS, eval_doc},
	{"exec",        builtin_exec,       METH_VARARGS, exec_doc},
 	// {"format",	builtin_format,     METH_VARARGS, format_doc},
 	// {"getattr",	builtin_getattr,    METH_VARARGS, getattr_doc},
 	// {"globals",	(PyCFunction)builtin_globals,    METH_NOARGS, globals_doc},
 	// {"hasattr",	builtin_hasattr,    METH_VARARGS, hasattr_doc},
 	// {"hash",	builtin_hash,       METH_O, hash_doc},
 	// {"hex",		builtin_hex,        METH_O, hex_doc},
 	// {"id",		builtin_id,         METH_O, id_doc},
 	// {"input",	builtin_input,      METH_VARARGS, input_doc},
 	// {"isinstance",  builtin_isinstance, METH_VARARGS, isinstance_doc},
 	// {"issubclass",  builtin_issubclass, METH_VARARGS, issubclass_doc},
 	// {"iter",	builtin_iter,       METH_VARARGS, iter_doc},
 	// {"len",		builtin_len,        METH_O, len_doc},
 	// {"locals",	(PyCFunction)builtin_locals,     METH_NOARGS, locals_doc},
 	// {"max",		(PyCFunction)builtin_max,        METH_VARARGS | METH_KEYWORDS, max_doc},
 	// {"min",		(PyCFunction)builtin_min,        METH_VARARGS | METH_KEYWORDS, min_doc},
	// {"next",	(PyCFunction)builtin_next,       METH_VARARGS, next_doc},
 	// {"oct",		builtin_oct,        METH_O, oct_doc},
 	// {"ord",		builtin_ord,        METH_O, ord_doc},
 	// {"pow",		builtin_pow,        METH_VARARGS, pow_doc},
 	// {"print",	(PyCFunction)builtin_print,      METH_VARARGS | METH_KEYWORDS, print_doc},
 	// {"repr",	builtin_repr,       METH_O, repr_doc},
 	// {"round",	(PyCFunction)builtin_round,      METH_VARARGS | METH_KEYWORDS, round_doc},
 	// {"setattr",	builtin_setattr,    METH_VARARGS, setattr_doc},
 	// {"sorted",	(PyCFunction)builtin_sorted,     METH_VARARGS | METH_KEYWORDS, sorted_doc},
 	// {"sum",		builtin_sum,        METH_VARARGS, sum_doc},
 	// {"vars",	builtin_vars,       METH_VARARGS, vars_doc},
	{NULL,		NULL},
};

PyDoc_STRVAR(builtin_doc,
"py3to2 Built-in functions, exceptions, and other objects");

// PyObject *initpy3k_builtins(void) {
				// return Py_InitModule("py3k_builtins", builtin_methods);
// }
// PyMODINIT_FUNC inittiming(void)
// {
    // if (PyErr_WarnPy3k("the timing module has been removed in "
                        // "Python 3.0; use time.clock() instead", 2) < 0)
        // return;
   //  
	// (void)Py_InitModule("timing", timing_methods);
// }

PyMODINIT_FUNC init_py3to2(void)
{
	PyObject *mod;
	mod = Py_InitModule4("_py3to2", builtin_methods,
			     builtin_doc, (PyObject *)NULL,
			     PYTHON_API_VERSION);
	if (mod == NULL)
		return NULL;
}
