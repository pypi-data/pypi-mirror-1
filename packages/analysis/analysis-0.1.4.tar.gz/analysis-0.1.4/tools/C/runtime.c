#include "runtime.h"

/* Global variables. */

object_int _True = {type_int, 1};
object_int _False = {type_int, 0};
reference *True = &_True;
reference *False = &_False;

/* Special exception system variables. */

struct exception_context the_exception_context[1];
object_Exception *_exc;

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

reference *IGNORE(reference *obj)
{
    return None;
}

/*
reference *PUSH(reference *obj, reference **stack)
{
    *stack = obj;
    return obj;
}
*/

int _msg(const char *s)
{
    printf(s);
    return 0;
}

reference *_builtins___isinstance(reference *obj, int type)
{
    /* NOTE: Should be boolean. */
    if (((object *) obj)->type == type)
    {
        return True;
    }
    else
    {
        return False;
    }
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

reference *builtins___int_____lt__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value < ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____le__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value <= ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____eq__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value == ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____ne__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value != ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____ge__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value >= ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____gt__(reference *self, reference *other)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value > ((object_int *) other)->value)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins___int_____true__(reference *self)
{
    /* NOTE: Should be boolean. */
    if (((object_int *) self)->value != 0)
    {
        return True;
    }
    else
    {
        return False;
    }
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
    object_StopIteration *exc;
    if ((obj == None) || (obj->next == None))
    {
        exc = NEW_OBJECT(StopIteration);
        Throw (object_Exception *) exc;
    }
    this->next = obj->next;
    return obj->value;
}

reference *builtins___tuple___append(reference *self, reference *value)
{
    /* NOTE: To be replaced with something more established/better. */
    object_tuple *this = (object_tuple *) self;

    while (this->next != None)
    {
        this = this->next;
    }
    this->value = value;
    this->next = (object_tuple *) NEW_OBJECT(tuple);
    return None;
}

reference *builtins___tuple_____getitem__(reference *self, reference *index)
{
    /* NOTE: To be replaced with something more established/better. */
    object_tuple *this = (object_tuple *) self;
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

reference *builtins___tuple_____len__(reference *self)
{
    /* NOTE: To be replaced with something more established/better. */
    object_tuple *this = (object_tuple *) self;
    object_int *result = NEW_OBJECT(int);
    result->value = 0;

    while (this->next != None)
    {
        this = this->next;
        result->value++;
    }
    return result;
}

reference *builtins___tupleiterator_____init__(reference *self, reference *obj)
{
    /* NOTE: To be replaced with something more established/better. */
    object_tupleiterator *this = (object_tupleiterator *) self;
    this->next = obj;
    return self;
}

reference *builtins___tupleiterator___next(reference *self)
{
    /* NOTE: To be replaced with something more established/better. */
    object_tupleiterator *this = (object_tupleiterator *) self;
    object_tuple *obj = this->next;
    object_StopIteration *exc;
    if ((obj == None) || (obj->next == None))
    {
        exc = NEW_OBJECT(StopIteration);
        Throw (object_Exception *) exc;
    }
    this->next = obj->next;
    return obj->value;
}

reference *builtins___string_____len__(reference *self)
{
    object_string *this = (object_string *) self;
    object_int *result = NEW_OBJECT(int);
    result->value = strlen(this->value);
    return result;
}

reference *builtins_____is__(reference *a, reference *b)
{
    /* NOTE: Should be a boolean. */
    if (a == b)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins_____is_not__(reference *a, reference *b)
{
    /* NOTE: Should be a boolean. */
    if (a != b)
    {
        return True;
    }
    else
    {
        return False;
    }
}

reference *builtins_____not__(reference *a)
{
    /* NOTE: Should be a boolean. */
    if ((a == None) || (a == False))
    {
        return True;
    }
    else
    {
        return False;
    }
}

/* NOTE: Replace this with the appropriate methods. */

char *builtins___str(reference *obj)
{
    static char s[20];
    if (obj == None)
    {
        /* NOTE: This could also be False using the current boolean scheme. */
        strcpy(s, "None");
    }
    else if (TYPEOF(obj) == type_int)
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
