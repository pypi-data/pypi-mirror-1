#ifndef _RUNTIME_H_
#define _RUNTIME_H_

#define type_int 1
#define type_long 2
#define type_float 3
#define type_string 4

typedef struct object_int
{
    int type;
    int value;
} object_int;

typedef struct object_long
{
    int type;
    long value;
} object_long;

typedef struct object_float
{
    int type;
    double value;
} object_float;

typedef struct object_string
{
    int type;
    char *value;
} object_string;

#define new(x) GC_MALLOC(x)

#endif /* _RUNTIME_H_ */
