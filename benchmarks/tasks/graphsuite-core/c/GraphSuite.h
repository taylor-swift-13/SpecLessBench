#include "../../qcip-core/common/io.h"

#if EB_FAMILY == 0
#define LIMIT 1000000
static int n, weights[64], distance_matrix[64], dist[8], seen[8];
static void floyd(void) {
    int i,j,k,x,y;
    for(i=0;i<n;i++) for(j=0;j<n;j++) {
        x=weights[i*n+j]; distance_matrix[i*n+j]=(i==j?0:(x<0?LIMIT:x));
    }
    for(k=0;k<n;k++) for(i=0;i<n;i++) for(j=0;j<n;j++) {
        x=distance_matrix[i*n+k];y=distance_matrix[k*n+j];
        if(x!=LIMIT && y!=LIMIT && x+y<distance_matrix[i*n+j]) distance_matrix[i*n+j]=x+y;
    }
}
static void dijkstra_all(void) {
    int source,i,j,u,best,w;
    for(source=0;source<n;source++) {
        for(i=0;i<n;i++) {dist[i]=LIMIT;seen[i]=0;} dist[source]=0;
        for(i=0;i<n;i++) {
            u=-1;best=LIMIT;
            for(j=0;j<n;j++) if(!seen[j] && dist[j]<best) {u=j;best=dist[j];}
            if(u<0) break;
            seen[u]=1;
            for(j=0;j<n;j++) {w=weights[u*n+j];
#if EB_STYLE == 2
                if(w==0) w=-1;
#endif
                if(w>=0 && dist[u]+w<dist[j]) dist[j]=dist[u]+w;
            }
        }
        for(j=0;j<n;j++) distance_matrix[source*n+j]=dist[j];
    }
}
int main(void) {
    int i;begin_output();n=eb_input[0];
    for(i=0;i<n*n;i++) weights[i]=eb_input[1+i];
#if EB_STYLE == 0
    floyd();
#else
    dijkstra_all();
#endif
    for(i=0;i<n*n;i++) emit(distance_matrix[i]==LIMIT?-1:distance_matrix[i]);
    return end_output();
}
#elif EB_FAMILY == 1
static int n, edge[64], mark[8], order[8], order_size, comp[8];
static int idx[8],low[8],onstack[8],stack[8],top,clock_value,component_count;
static void tarjan_visit(int v) {
    int w,x; idx[v]=clock_value;low[v]=clock_value;clock_value++;
    stack[top++]=v;onstack[v]=1;
    for(w=0;w<n;w++) if(edge[v*n+w]) {
        if(idx[w]<0) {tarjan_visit(w);if(low[w]<low[v])low[v]=low[w];}
        else if(onstack[w] && idx[w]<low[v])low[v]=idx[w];
    }
    if(low[v]==idx[v]) {
        do {x=stack[--top];onstack[x]=0;comp[x]=component_count;} while(x!=v);
        component_count++;
    }
}
static void first_visit(int v) {
    int w;mark[v]=1;
    for(w=0;w<n;w++) if(edge[v*n+w] && !mark[w]) first_visit(w);
    order[order_size++]=v;
}
static void second_visit(int v,int c) {
    int w;comp[v]=c;
    for(w=0;w<n;w++) {
#if EB_STYLE == 2
        if(edge[v*n+w] && comp[w]<0) second_visit(w,c);
#else
        if(edge[w*n+v] && comp[w]<0) second_visit(w,c);
#endif
    }
}
static void tarjan(void) {
    int i;top=0;clock_value=0;component_count=0;
    for(i=0;i<n;i++){idx[i]=-1;low[i]=0;onstack[i]=0;comp[i]=-1;}
    for(i=0;i<n;i++)if(idx[i]<0)tarjan_visit(i);
}
static void kosaraju(void) {
    int i,v;order_size=0;component_count=0;
    for(i=0;i<n;i++){mark[i]=0;comp[i]=-1;}
    for(i=0;i<n;i++)if(!mark[i])first_visit(i);
    for(i=order_size-1;i>=0;i--){v=order[i];if(comp[v]<0)second_visit(v,component_count++);}
}
int main(void) {
    int i,j;begin_output();n=eb_input[0];for(i=0;i<n*n;i++)edge[i]=eb_input[1+i];
#if EB_STYLE == 0
    tarjan();
#else
    kosaraju();
#endif
    for(i=0;i<n;i++)for(j=0;j<n;j++)emit(comp[i]==comp[j]);
    return end_output();
}
#else
static int text[48],pattern[16],right[4],n,m;
static int brute(void) {
    int i,j;for(i=0;i<=n-m;i++){for(j=0;j<m && text[i+j]==pattern[j];j++);if(j==m)return i;}return -1;
}
static int boyer_moore(void) {
    int i,j,skip;if(m==0)return 0;
    for(i=0;i<4;i++)right[i]=-1;for(i=0;i<m;i++)right[pattern[i]]=i;
    i=0;while(i<=n-m){j=m-1;while(j>=0 && text[i+j]==pattern[j])j--;
        if(j<0)return i;
#if EB_STYLE == 2
        skip=m;
#else
        skip=j-right[text[i+j]];if(skip<1)skip=1;
#endif
        i+=skip;
    }return -1;
}
int main(void) {
    int i,result;begin_output();n=eb_input[0];m=eb_input[1];
    for(i=0;i<n;i++)text[i]=eb_input[2+i];for(i=0;i<m;i++)pattern[i]=eb_input[2+n+i];
#if EB_STYLE == 0
    result=brute();
#else
    result=boyer_moore();
#endif
    emit(result);return end_output();
}
#endif
