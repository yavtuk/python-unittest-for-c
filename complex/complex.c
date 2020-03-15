#include "complex/complex.h"

complex_t summ(const complex_t * const lhs, const complex_t * const rhs) {
    complex_t temp;
    temp.re = lhs->re + rhs->re;
    temp.im = lhs->im + rhs->im;
    return temp;
}
