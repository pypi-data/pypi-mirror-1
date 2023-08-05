#include <math.h>

#ifndef fmodf
    #define fmodf fmod
#endif

OP(Add, o=a+b)
OP(Sub, o=a-b)
OP(Mul, o=a*b)
OP(Div, o=a/b)
OP(Mod, o=fmodf(a,b))
OP(Max, if (a>b) o=a; else o=b)
OP(Min, if (a<b) o=a; else o=b)
