#include "runtime.h"
#include <math.h>
#include <sys/time.h>

/* Global variables. */

object_builtins___boolean _builtins___True = {type_builtins___boolean, 1};
object_builtins___boolean _builtins___False = {type_builtins___boolean, 0};
object_builtins___none _builtins___None = {type_builtins___none};
reference *builtins___True = &_builtins___True;
reference *builtins___False = &_builtins___False;
reference *builtins___None = &_builtins___None;
int _argc;
char **_argv;

/* Special exception system variables. */

struct exception_context the_exception_context[1];
reference *_exc;

reference *_NEW_OBJECT(int type, int size)
{
    object *result = GC_MALLOC(size);
    result->type = type;
    return result;
}

reference *_NEW_METHOD(reference *function, reference *context)
{
    object_method *method = NEW_OBJECT(method);
    method->function = function;
    method->context = context;
    return method;
}

reference *THROW(reference *obj)
{
    Throw obj;
    return 0;
}

reference *_msg(const char *s, reference *r)
{
    printf(s);
    fflush(stdout);
    return r;
}

reference *IMPL___builtins___isinstance(reference *obj, reference *type)
{
    /* NOTE: Must correspond to the series size value in the visitor. */
    if ((((object *) obj)->type / 256) == ((int) type / 256))
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

/* NOTE: Some of these functions could almost be macros. */

reference *IMPL___builtins___int_____add__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = ((object_builtins___int *) self)->value + ((object_builtins___int *) other)->value;
    return (reference *) result;
}

reference *IMPL___builtins___int_____sub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = ((object_builtins___int *) self)->value - ((object_builtins___int *) other)->value;
    return (reference *) result;
}

reference *IMPL___builtins___int_____mul__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = ((object_builtins___int *) self)->value * ((object_builtins___int *) other)->value;
    return (reference *) result;
}

reference *IMPL___builtins___int_____rsub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = ((object_builtins___int *) other)->value - ((object_builtins___int *) self)->value;
    return (reference *) result;
}

reference *IMPL___builtins___int_____pow__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = (int) pow(((object_builtins___int *) self)->value, ((object_builtins___int *) other)->value);
    return (reference *) result;
}

/* NOTE: Should use a boolean type. Condition testing should use a special
 * NOTE: true value testing function or method. */

reference *IMPL___builtins___int_____lt__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value < ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____le__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value <= ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____eq__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value == ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____ne__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value != ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____ge__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value >= ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____gt__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_builtins___int *) self)->value > ((object_builtins___int *) other)->value)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins___int_____neg__(reference *self)
{
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = -((object_builtins___int *) self)->value;
    return (reference *) result;
}

reference *IMPL___builtins___int_____str__(reference *self)
{
    /* NOTE: Limited buffer size. */
    /* NOTE: Standard char type in use. */
    char buffer[256];
    object_builtins___string *result = (object_builtins___string *) NEW_OBJECT(builtins___string);
    sprintf(buffer, "%d", ((object_builtins___int *) self)->value);
    result->value = GC_MALLOC((strlen(buffer) + 1) * sizeof(char));
    strcpy(result->value, buffer);
    return (reference *) result;
}

reference *IMPL___builtins___float_____add__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) self)->value + ((object_builtins___float *) other)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___float *) self)->value + ((object_builtins___int *) other)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____sub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) self)->value - ((object_builtins___float *) other)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___float *) self)->value - ((object_builtins___int *) other)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____rsub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) other)->value - ((object_builtins___float *) self)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___int *) other)->value - ((object_builtins___float *) self)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____mul__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) self)->value * ((object_builtins___float *) other)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___float *) self)->value * ((object_builtins___int *) other)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____rmul__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) other)->value * ((object_builtins___float *) self)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___int *) other)->value * ((object_builtins___float *) self)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____div__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) self)->value / ((object_builtins___float *) other)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___float *) self)->value / ((object_builtins___int *) other)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____rdiv__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = ((object_builtins___float *) other)->value / ((object_builtins___float *) self)->value;
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = ((object_builtins___int *) other)->value / ((object_builtins___float *) self)->value;
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____pow__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    if (TYPEOF(other) == type_builtins___float)
    {
        result->value = pow(((object_builtins___float *) self)->value, ((object_builtins___float *) other)->value);
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        result->value = pow(((object_builtins___float *) self)->value, ((object_builtins___int *) other)->value);
    }
    return (reference *) result;
}

reference *IMPL___builtins___float_____lt__(reference *self, reference *other)
{
    if (TYPEOF(other) == type_builtins___float)
    {
        if (((object_builtins___float *) self)->value < ((object_builtins___float *) other)->value)
        {
            return builtins___True;
        }
        else
        {
            return builtins___False;
        }
    }
    else if (TYPEOF(other) == type_builtins___int)
    {
        if (((object_builtins___float *) self)->value < ((object_builtins___int *) other)->value)
        {
            return builtins___True;
        }
        else
        {
            return builtins___False;
        }
    }
}

reference *IMPL___builtins___float_____neg__(reference *self)
{
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    result->value = -((object_builtins___float *) self)->value;
    return (reference *) result;
}

/* NOTE: Precision information from Python 2.4.1. */

#define IMPL___PREC_STR 12

reference *IMPL___builtins___float_____str__(reference *self)
{
    /* NOTE: Limited buffer size. */
    /* NOTE: Standard char type in use. */
    char buffer[256];
    object_builtins___string *result = (object_builtins___string *) NEW_OBJECT(builtins___string);
    /* Format the value (parameter #1) using the precision (parameter #2) and the "g" format option. */
    sprintf(buffer, "%1$.*2$g", ((object_builtins___float *) self)->value, IMPL___PREC_STR);
    result->value = GC_MALLOC((strlen(buffer) + 1) * sizeof(char));
    strcpy(result->value, buffer);
    return (reference *) result;
}

reference *IMPL___builtins___string_____len__(reference *self)
{
    object_builtins___string *this = (object_builtins___string *) self;
    object_builtins___int *result = NEW_OBJECT(builtins___int);
    result->value = strlen(this->value);
    return result;
}

reference *IMPL___builtins___buffer_____init__(reference *self, reference *size)
{
    /* NOTE: Standard char type in use. */
    object_builtins___buffer *this = (object_builtins___buffer *) self;
    this->size = ((object_builtins___int *) size)->value;
    this->pos = 0;
    this->value = GC_MALLOC((this->size + 1) * sizeof(char));
    return self;
}

reference *IMPL___builtins___buffer___append(reference *self, reference *s)
{
    object_builtins___buffer *this = (object_builtins___buffer *) self;
    object_builtins___string *str = (object_builtins___string *) s;
    int length = strlen(str->value);
    /* NOTE: Should check for the end of the buffer. */
    strcpy(this->value + this->pos, str->value);
    this->pos += length;
}

reference *IMPL___builtins___buffer_____str__(reference *self)
{
    object_builtins___buffer *this = (object_builtins___buffer *) self;
    object_builtins___string *result = (object_builtins___string *) NEW_OBJECT(builtins___string);
    result->value = this->value;
    return (reference *) result;
}

reference *IMPL___builtins_____is__(reference *a, reference *b)
{
    /* NOTE: Should be a boolean. */
    if (a == b)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins_____is_not__(reference *a, reference *b)
{
    /* NOTE: Should be a boolean. */
    if (a != b)
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___builtins_____not__(reference *a)
{
    /* NOTE: Should be a boolean. */
    if ((a == builtins___None) || (a == builtins___False))
    {
        return builtins___True;
    }
    else
    {
        return builtins___False;
    }
}

reference *IMPL___sys____get_argc()
{
    object_builtins___int *result = (object_builtins___int *) NEW_OBJECT(builtins___int);
    result->value = _argc;
    return (reference *) result;
}

reference *IMPL___sys____get_arg(reference *i)
{
    object_builtins___string *result = (object_builtins___string *) NEW_OBJECT(builtins___string);
    result->value = _argv[((object_builtins___int *) i)->value];
    return (reference *) result;
}

reference *IMPL___time___time()
{
    /* NOTE: Not re-entrant! */
    object_builtins___float *result = (object_builtins___float *) NEW_OBJECT(builtins___float);
    struct timeval tp;
    /* NOTE: Error checking not done. */
    gettimeofday(&tp, NULL);
    result->value = tp.tv_sec + tp.tv_usec * 0.000001;
    return (reference *) result;
}

/* vim: tabstop=4 expandtab shiftwidth=4
 */
