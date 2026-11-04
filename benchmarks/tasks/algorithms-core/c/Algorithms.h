/* Newly authored EqualBench bounded algorithm variants. No external callees.
 * EB_FAMILY: factorial/reverse/sum/matrix/search/queue = 0..5.
 * EB_STYLE: reference/replacement/retained mutant = 0/1/2. */
#include "../../qcip-core/common/io.h"

#if EB_FAMILY == 0
static int factorial_rec(int n) { if (n == 0) return 1; return n * factorial_rec(n-1); }
static int factorial_acc(int n, int a) {
    if (n == 0) return a;
#if EB_STYLE == 2
    return factorial_acc(n-1, a*(n-1));
#else
    return factorial_acc(n-1, a*n);
#endif
}
int main(void) {
    int result; begin_output();
#if EB_STYLE == 0
    result = factorial_rec(eb_input[0]);
#else
    result = factorial_acc(eb_input[0], 1);
#endif
    emit(result); return end_output();
}
#elif EB_FAMILY == 1
static void reverse_rec(int n, int pos) {
    if (n == 0) return;
    reverse_rec(n-1, pos+1); emit(eb_input[1+pos]);
}
int main(void) {
    int n=eb_input[0]; int i; begin_output();
#if EB_STYLE == 0
    reverse_rec(n,0);
#else
    for(i=n;i>0;i=i-1) emit(eb_input[i]);
#if EB_STYLE == 2
    emit(0);
#endif
#endif
    return end_output();
}
#elif EB_FAMILY == 2
static int sum_rec(int n, int pos) {
    if(n==0) return 0;
    return eb_input[1+pos]+sum_rec(n-1,pos+1);
}
int main(void) {
    int n=eb_input[0]; int i; int result=0; begin_output();
#if EB_STYLE == 0
    result=sum_rec(n,0);
#else
#if EB_STYLE == 2
    if(n>0) n=n-1;
#endif
    for(i=0;i<n;i=i+1) result=result+eb_input[1+i];
#endif
    emit(result); return end_output();
}
#elif EB_FAMILY == 3
static int output[36];
int main(void) {
    int r=eb_input[0]; int k=eb_input[1]; int c=eb_input[2];
    int i,j,t,a,b; begin_output();
    for(i=0;i<36;i=i+1) output[i]=0;
#if EB_STYLE == 1
    for(i=0;i<r;i=i+1) for(t=0;t<k;t=t+1) for(j=0;j<c;j=j+1) {
        a=eb_input[3+i*k+t]; b=eb_input[3+r*k+t*c+j];
        output[i*c+j]=output[i*c+j]+a*b;
    }
#else
    for(i=0;i<r;i=i+1) for(j=0;j<c;j=j+1) for(t=0;t<k;t=t+1) {
        a=eb_input[3+i*k+t];
#if EB_STYLE == 2
        b=eb_input[3+r*k+j*k+t];
#else
        b=eb_input[3+r*k+t*c+j];
#endif
        output[i*c+j]=output[i*c+j]+a*b;
    }
#endif
    for(i=0;i<r*c;i=i+1) emit(output[i]);
    return end_output();
}
#elif EB_FAMILY == 4
static int prefix[32];
static void build_prefix(int n,int m) {
    int i,j; prefix[0]=0; j=0;
    for(i=1;i<m;i=i+1) {
        while(j>0 && eb_input[2+n+i]!=eb_input[2+n+j]) j=prefix[j-1];
        if(eb_input[2+n+i]==eb_input[2+n+j]) j=j+1;
        prefix[i]=j;
    }
}
static int search(int n,int m) {
    int i,j;
    if(m==0) return 0;
#if EB_STYLE == 0
    for(i=0;i<=n-m;i=i+1) {
        j=0; while(j<m && eb_input[2+i+j]==eb_input[2+n+j]) j=j+1;
        if(j==m) return i;
    }
#else
    build_prefix(n,m); j=0;
    for(i=0;i<n;i=i+1) {
        while(j>0 && eb_input[2+i]!=eb_input[2+n+j]) {
#if EB_STYLE == 2
            j=0;
#else
            j=prefix[j-1];
#endif
        }
        if(eb_input[2+i]==eb_input[2+n+j]) j=j+1;
        if(j==m) return i-m+1;
    }
#endif
    return -1;
}
int main(void) { int result; begin_output(); result=search(eb_input[0],eb_input[1]); emit(result); return end_output(); }
#else
static int front[64]; static int rear[64]; static int nf,nr;
static void enqueue(int v) {
#if EB_STYLE == 0
    front[nf]=v; nf=nf+1;
#else
    rear[nr]=v; nr=nr+1;
#endif
}
static void normalize(void) {
    int i;
#if EB_STYLE != 0
    if(nf==0) {
        for(i=0;i<nr;i=i+1) front[i]=rear[nr-1-i];
        nf=nr;
#if EB_STYLE == 1
        nr=0;
#endif
    }
#endif
}
static void query(int remove) {
    int v,i; normalize();
    if(nf==0) {emit(0);emit(0);return;}
#if EB_STYLE == 0
    v=front[0];
    if(remove) {for(i=1;i<nf;i=i+1) front[i-1]=front[i]; nf=nf-1;}
#else
    v=front[nf-1]; if(remove) nf=nf-1;
#endif
    emit(1);emit(v);
}
int main(void) {
    int q=eb_input[0]; int i,op; begin_output(); nf=0;nr=0;
    for(i=0;i<q;i=i+1) {
        op=eb_input[1+2*i]; emit(op);
        if(op==0) {enqueue(eb_input[2+2*i]);emit(0);}
        else query(op==1);
    }
    return end_output();
}
#endif
