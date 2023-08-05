#ifndef _RUNTIME_H_
#define _RUNTIME_H_

/* Require the Boehm-Demers-Weiser garbage collector. */

#include "gc/gc.h"

/* Require the cexcept library for exceptions. */

#include "cexcept.h"
#include <stdio.h>

/* Built-in type codes. */
/* Usage of synonyms for cases where it is inappropriate to use the actual
 * names in programs (eg. int, float). */
/* NOTE: Missing boolean type. */

#define type_None 0
#define type_method 1
#define type_int 2
#define type__int 2
#define type_float 3
#define type__float 3
#define type_string 4
#define type_list 5
#define type_listiterator 6
#define type_Exception 7
#define type_StopIteration 8

/* Special values and types. */

#define None 0
#define reference void

/* Built-in types. */
/* NOTE: The assumption that the type attribute will always be first in all
 * NOTE: these structures probably contravenes the C standard, and a better way
 * NOTE: of having a testable generic object is probably needed. */

typedef struct object
{
    int type;
} object;

typedef struct object_method
{
    int type;
    reference *context;
    reference *function;
} object_method;

typedef struct object_int
{
    int type;
    int value;
} object_int;

typedef object_int object__int; /* Synonym to handle _int in programs. */

typedef struct object_float
{
    int type;
    double value;
} object_float;

typedef object_float object__float; /* Synonym to handle _float in programs. */

typedef struct object_string
{
    int type;
    char *value;
} object_string;

/* NOTE: To be improved, using established list data structures. */

typedef struct object_list
{
    int type;
    reference *value;
    struct object_list *next;
} object_list;

typedef struct object_listiterator
{
    int type;
    struct object_list *next;
} object_listiterator;

/* Exceptions. */

typedef struct object_Exception
{
    int type;
    object_string *message;
} object_Exception;

typedef object_Exception object_StopIteration;

/* Convenience macros. */

#define SYSINIT GC_INIT()
#define NEW_OBJECT(x) _NEW_OBJECT(type_##x, sizeof(object_##x))
#define NEW_METHOD(function, context) _NEW_METHOD(function, context)
#define TYPEOF(x) ((object *) x)->type
#define CONTEXT(x) ((object_method *) x)->context
#define FNAME(x) ((object_method *) x)->function
#define PUSH(x, y) y = x

/* Administrative function declarations. */

reference *_NEW_OBJECT(int type, int size);
reference *_NEW_METHOD(reference *function, reference *context);
reference *IGNORE(reference *obj);

/* Internal function declarations. */

int internal___int_from_reference(reference *obj, int default_value);

/* Built-in function declarations. */

#define builtins___isinstance(obj, x) _builtins___isinstance(obj, type_##x)
int _builtins___isinstance(reference *obj, int type);
reference *builtins___int_____add__(reference *self, reference *other);
reference *builtins___int_____sub__(reference *self, reference *other);
int builtins___int_____lt__(reference *self, reference *other);
int builtins___int_____le__(reference *self, reference *other);
int builtins___int_____eq__(reference *self, reference *other);
int builtins___int_____ne__(reference *self, reference *other);
int builtins___int_____ge__(reference *self, reference *other);
int builtins___int_____gt__(reference *self, reference *other);
reference *builtins___float_____add__(reference *self, reference *other);
reference *builtins___float_____sub__(reference *self, reference *other);
#define builtins___float_____radd__ builtins_float_____add__
reference *builtins___float_____rsub__(reference *self, reference *other);
reference *builtins___list___append(reference *self, reference *value);
reference *builtins___list_____getitem__(reference *self, reference *index);
reference *builtins___list_____getslice__(reference *self, reference *start, reference *end);
reference *builtins___list_____len__(reference *self);
reference *builtins___listiterator_____init__(reference *self, reference *obj);
reference *builtins___listiterator___next(reference *self);
char *builtins___str(reference *obj);

/* Global variables. */

extern object_Exception *_exc;

/* Exception declarations. */

define_exception_type(object_Exception *);
extern struct exception_context the_exception_context[1];

#endif /* _RUNTIME_H_ */

/* vim: tabstop=4 expandtab shiftwidth=4
 */
