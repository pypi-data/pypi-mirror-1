#define OP(name, operation) name,
enum Operation {
    #include "operations.h"
};

#define GET_ARRAY(name) name = in_##name[i*stride_##name]

#define OP_A_A(name, operation, get_a, get_b) \
        case (name):\
            for (i=0;i<length;i++){\
                get_a;\
                get_b;\
                operation;\
                out[i*stride_o] = o;\
            }\
            break;

#define SWITCH_START switch(op) {

#define SWITCH_END default: return 0;} return 1;

int run_float_float(int length, int op,
        float * out,  int stride_o,
        float * in_a, int stride_a,
        float * in_b, int stride_b) {

    float o, a, b;
    int i;

    a = in_a[0];
    b = in_b[0];

    if (stride_a!=0){
        if (stride_b!=0) {
            #undef OP
            #define OP(name, operation) OP_A_A(name, operation, \
                    GET_ARRAY(a), \
                    GET_ARRAY(b))
            SWITCH_START
            #include "operations.h"
            SWITCH_END
        } else {
            #undef OP
            #define OP(name, operation) OP_A_A(name, operation, \
                    GET_ARRAY(a), \
                    b=b)
            SWITCH_START
            #include "operations.h"
            SWITCH_END
        }
    } else {
        if (stride_b!=0) {
            #undef OP
            #define OP(name, operation) OP_A_A(name, operation, \
                    a=a, \
                    GET_ARRAY(b))
            SWITCH_START
            #include "operations.h"
            SWITCH_END
        } else {
            // we shouldn't have to do an operation on two single values!
            return 0;
        }
    }
}
