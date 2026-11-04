#include "../../qcip-core/common/io.h"
struct Record { int key, payload; };
static struct Record data[64],output[64];
static int count[7],position[7];
static void insertion(int n) {
    int i,j;struct Record r;
    for(i=1;i<n;i++){r=data[i];j=i;while(j>0 && r.key<data[j-1].key){data[j]=data[j-1];j--;}data[j]=r;}
}
static void counting(int n) {
    int i,k,total=0;for(k=0;k<7;k++)count[k]=0;
    for(i=0;i<n;i++)count[data[i].key+3]++;
    for(k=0;k<7;k++){position[k]=total;total+=count[k];}
#if EB_STYLE == 2
    for(i=n-1;i>=0;i--){k=data[i].key+3;output[position[k]++]=data[i];}
#else
    for(i=0;i<n;i++){k=data[i].key+3;output[position[k]++]=data[i];}
#endif
    for(i=0;i<n;i++)data[i]=output[i];
}
int main(void){
    int n,i;begin_output();n=eb_input[0];
    for(i=0;i<n;i++){data[i].key=eb_input[1+2*i];data[i].payload=eb_input[2+2*i];}
#if EB_STYLE == 0
    insertion(n);
#else
    counting(n);
#endif
    for(i=0;i<n;i++){emit(data[i].key);emit(data[i].payload);}return end_output();
}
