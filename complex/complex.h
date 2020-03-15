
#ifndef COMPLEX_H_
#define COMPLEX_H_

typedef struct {
    int re;
    int im;
} complex_t;

complex_t summ(const complex_t * const lhs, const complex_t * const rhs);

#endif
