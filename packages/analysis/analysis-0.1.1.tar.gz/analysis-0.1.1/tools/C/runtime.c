#include "runtime.h"

/* Global variables. */

FILE *_stream;
reference *_tmp;
reference *_expr;
reference *_iter;
object_stack *_stack = None;

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

reference *TOP()
{
    return _stack->value;
}

reference *POP()
{
    reference *obj = _stack->value;
    _stack = _stack->next;
    return obj;
}

reference *PUSH(reference *obj)
{
    object_stack *next = _stack;
    _stack = NEW_OBJECT(stack);
    _stack->value = obj;
    _stack->next = next;
    return obj;
}

int _builtins___isinstance(reference *obj, int type)
{
    return ((object *) obj)->type == type;
}

/* NOTE: Some of these functions could almost be macros. */

reference *builtins___int_____add__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_int *result = (object_int *) NEW_OBJECT(int);
    result->value = ((object_int *) self)->value + ((object_int *) other)->value;
    return (reference *) result;
}

reference *builtins___int_____sub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_int *result = (object_int *) NEW_OBJECT(int);
    result->value = ((object_int *) self)->value - ((object_int *) other)->value;
    return (reference *) result;
}

/* NOTE: Should use a boolean type. Condition testing should use a special
 * NOTE: true value testing function or method. */

int builtins___int_____lt__(reference *self, reference *other)
{
    return ((object_int *) self)->value < ((object_int *) other)->value;
}

int builtins___int_____le__(reference *self, reference *other)
{
    return ((object_int *) self)->value <= ((object_int *) other)->value;
}

int builtins___int_____eq__(reference *self, reference *other)
{
    return ((object_int *) self)->value == ((object_int *) other)->value;
}

int builtins___int_____ne__(reference *self, reference *other)
{
    return ((object_int *) self)->value != ((object_int *) other)->value;
}

int builtins___int_____ge__(reference *self, reference *other)
{
    return ((object_int *) self)->value >= ((object_int *) other)->value;
}

int builtins___int_____gt__(reference *self, reference *other)
{
    return ((object_int *) self)->value > ((object_int *) other)->value;
}

reference *builtins___float_____add__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_float *result = (object_float *) NEW_OBJECT(float);
    if (TYPEOF(other) == type_float)
    {
        result->value = ((object_float *) self)->value + ((object_float *) other)->value;
    }
    else if (TYPEOF(other) == type_int)
    {
        result->value = ((object_float *) self)->value + ((object_int *) other)->value;
    }
    return (reference *) result;
}

reference *builtins___float_____sub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_float *result = (object_float *) NEW_OBJECT(float);
    if (TYPEOF(other) == type_float)
    {
        result->value = ((object_float *) self)->value - ((object_float *) other)->value;
    }
    else if (TYPEOF(other) == type_int)
    {
        result->value = ((object_float *) self)->value - ((object_int *) other)->value;
    }
    return (reference *) result;
}

reference *builtins___float_____rsub__(reference *self, reference *other)
{
    /* NOTE: Check for overflow! */
    object_float *result = (object_float *) NEW_OBJECT(float);
    if (TYPEOF(other) == type_float)
    {
        result->value = ((object_float *) other)->value - ((object_float *) self)->value;
    }
    else if (TYPEOF(other) == type_int)
    {
        result->value = ((object_int *) other)->value - ((object_float *) self)->value;
    }
    return (reference *) result;
}

reference *builtins___list___append(reference *self, reference *value)
{
    /* NOTE: To be replaced with something more established/better. */
    object_list *this = (object_list *) self;

    while (this->next != None)
    {
        this = this->next;
    }
    this->value = value;
    this->next = (object_list *) NEW_OBJECT(list);
    return None;
}

reference *builtins___list_____getitem__(reference *self, reference *index)
{
    /* NOTE: To be replaced with something more established/better. */
    object_list *this = (object_list *) self;
    object_int *target = (object_int *) index;
    int i = 0;

    while (i < target->value)
    {
        if (this->next != None)
        {
            this = this->next;
            i++;
        }
        else
        {
            /* NOTE: Raise an exception here. */
            return None;
        }
    }
    return this->value;
}

reference *builtins___list_____getslice__(reference *self, reference *start, reference *end)
{
    /* NOTE: To be replaced with something more established/better. */
    object_list *this = (object_list *) self;
    object_list *result = NEW_OBJECT(list);
    object_list *target = result;
    int start_value = internal___int_from_reference(start, 0);
    int end_value = internal___int_from_reference(end, 0);
    int i = 0;

    while ((this != None) && (this->next != None) && ((end == None) || (i < end_value)))
    {
        if (i >= start_value)
        {
            target->next = NEW_OBJECT(list);
            target->value = this->value;
            target = target->next;
        }
        this = this->next;
        i++;
    }

    return result;
}

reference *builtins___list_____len__(reference *self)
{
    /* NOTE: To be replaced with something more established/better. */
    object_list *this = (object_list *) self;
    object_int *result = NEW_OBJECT(int);
    result->value = 0;

    while (this->next != None)
    {
        this = this->next;
        result->value++;
    }
    return result;
}

reference *builtins___listiterator_____init__(reference *self, reference *obj)
{
    /* NOTE: To be replaced with something more established/better. */
    object_listiterator *this = (object_listiterator *) self;
    this->next = obj;
    return self;
}

reference *builtins___listiterator___next(reference *self)
{
    /* NOTE: To be replaced with something more established/better. */
    object_listiterator *this = (object_listiterator *) self;
    object_list *obj = this->next;
    if (obj == None)
    {
        /* NOTE: Should raise a StopIteration exception. */
        return None;
    }
    this->next = obj->next;
    return obj->value;
}

/* NOTE: Replace this with the appropriate methods. */

char *builtins___str(reference *obj)
{
    static char s[20];
    if (TYPEOF(obj) == type_int)
    {
        sprintf(s, "%d", ((object_int *) obj)->value);
    }
    else if (TYPEOF(obj) == type_float)
    {
        sprintf(s, "%f", ((object_float *) obj)->value);
    }
    else if (TYPEOF(obj) == type_string)
    {
        return ((object_string *) obj)->value;
    }
    return s;
}

int internal___int_from_reference(reference *obj, int default_value)
{
    if (obj == None)
    {
        return default_value;
    }
    else
    {
        return ((object_int *) obj)->value;
    }
}

/* vim: tabstop=4 expandtab shiftwidth=4
 */
