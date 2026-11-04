#include "../../qcip-core/common/io.h"
static int alphabet(int x) {
    if (x < 26) return 65+x;
    if (x < 52) return 97+x-26;
    if (x < 62) return 48+x-52;
    return x == 62 ? 43 : 47;
}
#if EB_STYLE == 0
static void encode(int n) {
    int i, a, b, c;
    for (i=0; i<n; i+=3) {
        a=eb_input[1+i];
        b=i+1<n ? eb_input[2+i] : 0;
        c=i+2<n ? eb_input[3+i] : 0;
        emit(alphabet(a/4));
        emit(alphabet((a%4)*16+b/16));
        emit(i+1<n ? alphabet((b%16)*4+c/64) : 61);
        emit(i+2<n ? alphabet(c%64) : 61);
    }
}
#else
static void encode(int n) {
    int i, buffer=0, bits=0, groups=0;
    for (i=0; i<n; ++i) {
        buffer=buffer*256+eb_input[1+i];
        bits+=8;
        while (bits>=6) {
            bits-=6;
            emit(alphabet(buffer/(1<<bits)));
            ++groups;
            buffer=buffer%(1<<bits);
        }
    }
    if (bits>0) {
        emit(alphabet(buffer*(1<<(6-bits))));
        ++groups;
    }
    while (groups%4!=0) {
        emit(61);
        ++groups;
#if EB_STYLE == 2
        break;
#endif
    }
}
#endif
int main(void) {
    begin_output();
    encode(eb_input[0]);
    return end_output();
}
