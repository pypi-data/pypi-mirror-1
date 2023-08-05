#ifndef _RUNTIME_H_
#define _RUNTIME_H_

/* Require the Boehm-Demers-Weiser garbage collector. */

#include "gc/gc.h"

/* Require the cexcept library for exceptions. */

#include "cexcept.h"
#include <stdio.h>
#include <string.h>

/* Built-in type codes. */

#define type_method 0
#define type_builtins___none 1
#define type_builtins___boolean 2
#define type_builtins___int 3
#define type_builtins___float 4
#define type_builtins___string 5
#define type_builtins___buffer 6
#define type_builtins___long 7

/* Special values and types. */

#define reference void

/* Built-in types. */
/* NOTE: The assumption that the type attribute will always be first in all
 * NOTE: these structures probably contravenes the C standard, and a better way
 * NOTE: of having a testable generic object is probably needed. */

typedef struct object
{
    int type;
} object;

typedef object object_builtins___none;

typedef struct object_method
{
    int type;
    reference *function;
    reference *context;
} object_method;

typedef struct object_builtins___boolean
{
    int type;
    int value;
} object_builtins___boolean;

typedef struct object_builtins___int
{
    int type;
    int value;
} object_builtins___int;

typedef struct object_builtins___float
{
    int type;
    double value;
} object_builtins___float;

typedef struct object_builtins___string
{
    int type;
    char *value;
} object_builtins___string;

typedef struct object_builtins___buffer
{
    int type;
    int size;
    int pos;
    char *value;
} object_builtins___buffer;

/* Convenience macros. */

#define SYSINIT GC_INIT()
#define NEW_OBJECT(x) _NEW_OBJECT(type_##x, sizeof(object_##x))
#define NEW_METHOD(function, context) _NEW_METHOD(function, context)
#define TYPEOF(x) ((object *) x)->type
#define CONTEXT(x) ((object_method *) x)->context
#define FNAME(x) ((object_method *) x)->function
#define PUSH(x, y) (y = x)
#define TRUE(x) ((x) == builtins___True)
#define GET_STRING(x) ((object_builtins___string *) (x))->value

/* Administrative function declarations. */

reference *_NEW_OBJECT(int type, int size);
reference *_NEW_METHOD(reference *function, reference *context);
reference *THROW(reference *obj);
reference *_msg(const char *s, reference *r);

/* Built-in function declarations. */

reference *IMPL___builtins___isinstance(reference *obj, reference *type);
reference *IMPL___builtins___int_____add__(reference *self, reference *other);
reference *IMPL___builtins___int_____sub__(reference *self, reference *other);
reference *IMPL___builtins___int_____rsub__(reference *self, reference *other);
reference *IMPL___builtins___int_____mul__(reference *self, reference *other);
#define IMPL___builtins___int_____iadd__ IMPL___builtins___int_____add__
#define IMPL___builtins___int_____isub__ IMPL___builtins___int_____sub__
reference *IMPL___builtins___int_____pow__(reference *self, reference *other);
reference *IMPL___builtins___int_____lt__(reference *self, reference *other);
reference *IMPL___builtins___int_____le__(reference *self, reference *other);
reference *IMPL___builtins___int_____eq__(reference *self, reference *other);
reference *IMPL___builtins___int_____ne__(reference *self, reference *other);
reference *IMPL___builtins___int_____ge__(reference *self, reference *other);
reference *IMPL___builtins___int_____gt__(reference *self, reference *other);
reference *IMPL___builtins___int_____neg__(reference *self);
reference *IMPL___builtins___int_____str__(reference *self);
reference *IMPL___builtins___float_____add__(reference *self, reference *other);
#define IMPL___builtins___float_____radd__ IMPL___builtins_float_____add__
reference *IMPL___builtins___float_____sub__(reference *self, reference *other);
reference *IMPL___builtins___float_____rsub__(reference *self, reference *other);
reference *IMPL___builtins___float_____mul__(reference *self, reference *other);
reference *IMPL___builtins___float_____rmul__(reference *self, reference *other);
reference *IMPL___builtins___float_____div__(reference *self, reference *other);
reference *IMPL___builtins___float_____rdiv__(reference *self, reference *other);
reference *IMPL___builtins___float_____pow__(reference *self, reference *other);
#define IMPL___builtins___float_____iadd__ IMPL___builtins___float_____add__
#define IMPL___builtins___float_____isub__ IMPL___builtins___float_____sub__
reference *IMPL___builtins___float_____lt__(reference *self, reference *other);
reference *IMPL___builtins___float_____neg__(reference *self);
reference *IMPL___builtins___float_____str__(reference *self);
reference *IMPL___builtins___string_____len__(reference *self);
reference *IMPL___builtins___buffer_____init__(reference *self, reference *size);
reference *IMPL___builtins___buffer___append(reference *self, reference *s);
reference *IMPL___builtins___buffer_____str__(reference *self);
reference *IMPL___builtins_____is__(reference *a, reference *b);
reference *IMPL___builtins_____is_not__(reference *a, reference *b);
reference *IMPL___builtins_____not__(reference *a);

reference *IMPL___sys____get_argc();
reference *IMPL___sys____get_arg(reference *i);

reference *IMPL___time___time();

/* Global variables. */

extern reference *_exc;
extern reference *builtins___True;
extern reference *builtins___False;
extern reference *builtins___None;
extern int _argc;
extern char **_argv;

/* Exception declarations. */

define_exception_type(reference *);
extern struct exception_context the_exception_context[1];

#endif /* _RUNTIME_H_ */

/* vim: tabstop=4 expandtab shiftwidth=4
 */
