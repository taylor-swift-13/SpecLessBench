/* SpecLessBench source-derived data-structure ports and newly authored clients.
 * See PROVENANCE.md. STYLE 0/1/2 = reference/replacement/retained mutant. */
#include "../../qcip-core/common/io.h"
#if EB_FAMILY == 0
struct Node { int id,value; struct Node *left,*right; };
static struct Node nodes[64];
static void mirror(struct Node *p) {
    struct Node *tmp;
    if(p==(void*)0) return;
    tmp=p->left;p->left=p->right;p->right=tmp;
    mirror(p->left);
#if EB_STYLE != 2
    mirror(p->right);
#endif
}
static void stack_mirror(struct Node *p) {
    struct Node *todo[64];struct Node *tmp;int n=0;
    if(p!=(void*)0){todo[n]=p;n=n+1;}
    while(n>0){n=n-1;p=todo[n];tmp=p->left;p->left=p->right;p->right=tmp;
        if(p->left!=(void*)0){todo[n]=p->left;n=n+1;}
        if(p->right!=(void*)0){todo[n]=p->right;n=n+1;}}
}
static int height(struct Node *p){int l,r;if(p==(void*)0)return 0;l=height(p->left);r=height(p->right);return (l>r?l:r)+1;}
static void project(struct Node *p){if(p==(void*)0){emit(-1);return;}emit(p->id);emit(p->value);project(p->left);project(p->right);}
int main(void){int n=eb_input[0],i,l,r;struct Node *root=(void*)0;begin_output();
    for(i=0;i<n;i=i+1){nodes[i].id=i;nodes[i].value=eb_input[1+3*i];l=eb_input[2+3*i];r=eb_input[3+3*i];nodes[i].left=l<0?(void*)0:&nodes[l];nodes[i].right=r<0?(void*)0:&nodes[r];}
    if(n>0)root=&nodes[n-1];
#if EB_STYLE == 1
    stack_mirror(root);
#else
    mirror(root);
#endif
    emit(height(root));project(root);return end_output();}
#elif EB_FAMILY == 1
static int parent[64],rank_[64];
static int find_root(int x){
#if EB_STYLE == 0
    if(parent[x]!=x)parent[x]=find_root(parent[x]);return parent[x];
#elif EB_STYLE == 1
    while(parent[x]!=x){parent[x]=parent[parent[x]];x=parent[x];}return x;
#else
    return parent[x];
#endif
}
static void unite(int a,int b){int x=find_root(a),y=find_root(b);if(x==y)return;
    if(rank_[x]>rank_[y])parent[y]=x;else{parent[x]=y;if(rank_[x]==rank_[y])rank_[y]=rank_[y]+1;}}
int main(void){int n=eb_input[0],q=eb_input[1],i,op,a,b,x,y;begin_output();
    for(i=0;i<n;i=i+1){parent[i]=i;rank_[i]=0;}
    for(i=0;i<q;i=i+1){op=eb_input[2+3*i];a=eb_input[3+3*i];b=eb_input[4+3*i];emit(op);
        if(op==0){unite(a,b);emit(0);}else{x=find_root(a);y=find_root(b);emit(x==y);}}
    return end_output();}
#elif EB_FAMILY == 2
static int heap[64],size_;
static void push(int v){int i=size_,p;
#if EB_STYLE == 1
    while(i>0&&heap[i-1]<v){heap[i]=heap[i-1];i=i-1;}
#else
    while(i>0){p=(i-1)/2;if(heap[p]>=v)break;heap[i]=heap[p];i=p;}
#endif
    heap[i]=v;size_=size_+1;}
static int pop(void){int result=heap[0],i=0,c,v,j;size_=size_-1;
#if EB_STYLE == 1
    for(j=0;j<size_;j=j+1)heap[j]=heap[j+1];
#else
    if(size_>0){v=heap[size_];while(2*i+1<size_){c=2*i+1;
#if EB_STYLE == 0
        if(c+1<size_&&heap[c+1]>heap[c])c=c+1;
#endif
        if(v>=heap[c])break;heap[i]=heap[c];i=c;}heap[i]=v;}
#endif
    return result;}
int main(void){int mode=eb_input[0],n=eb_input[1],i,op,v;begin_output();size_=0;
    if(mode==1){for(i=0;i<n;i=i+1)push(eb_input[2+i]);while(size_>0){v=pop();emit(v);}}
    else for(i=0;i<n;i=i+1){op=eb_input[2+2*i];v=eb_input[3+2*i];emit(op);
        if(op==0){push(v);emit(0);}else if(op==3)emit(size_==0);else if(size_==0){emit(0);emit(0);}else{emit(1);if(op==1)v=pop();else v=heap[0];emit(v);}}
    return end_output();}
#else
static int tags[64],aa[64],bb[64],env_[8],envn,ready[64],code_[64],err_[64],val_[64];
static void save(int i,int c,int e,int v){ready[i]=1;code_[i]=c;err_[i]=e;val_[i]=v;}
static void combine(int i){int t=tags[i],l=aa[i],r=bb[i],v=0;
    if(code_[l]!=0){save(i,code_[l],err_[l],0);return;}
    if(t==8||t==9){v=t==8?-val_[l]:(val_[l]==0);}
    else{
#if EB_STYLE == 2
        if((t==6||t==7)&&code_[r]!=0){save(i,code_[r],err_[r],0);return;}
#endif
        if(t==6&&val_[l]==0){save(i,0,-1,0);return;}
        if(t==7&&val_[l]!=0){save(i,0,-1,1);return;}
        if(code_[r]!=0){save(i,code_[r],err_[r],0);return;}
        if(t==2)v=val_[l]+val_[r];else if(t==3)v=val_[l]-val_[r];else if(t==4)v=val_[l]<val_[r];else if(t==5)v=val_[l]==val_[r];
        else if(t==6)v=(val_[l]!=0&&val_[r]!=0);else if(t==7)v=(val_[l]!=0||val_[r]!=0);
        else{if(val_[r]==0){save(i,3,i,0);return;}v=val_[l]/val_[r];}}
    if(v< -32768||v>32767)save(i,2,i,0);else save(i,0,-1,v);}
static int leaf(int i){int t=tags[i];if(t==0){save(i,0,-1,aa[i]);return 1;}
    if(t==1){if(aa[i]>=envn)save(i,1,i,0);else save(i,0,-1,env_[aa[i]]);return 1;}
    if(t>10){save(i,4,i,0);return 1;}return 0;}
static void eval_rec(int i){int t=tags[i];if(ready[i])return;if(leaf(i))return;eval_rec(aa[i]);
    if(code_[aa[i]]==0&&t!=8&&t!=9&&!(t==6&&val_[aa[i]]==0)&&!(t==7&&val_[aa[i]]!=0))eval_rec(bb[i]);
    combine(i);}
int main(void){int n=eb_input[0],i,p=2;begin_output();envn=eb_input[1];for(i=0;i<envn;i=i+1)env_[i]=eb_input[p++];
    for(i=0;i<n;i=i+1){tags[i]=eb_input[p++];aa[i]=eb_input[p++];bb[i]=eb_input[p++];ready[i]=0;code_[i]=0;err_[i]=-1;val_[i]=0;}
#if EB_STYLE == 0
    eval_rec(n-1);
#else
    for(i=0;i<n;i=i+1)if(!leaf(i))combine(i);
#endif
    emit(code_[n-1]);emit(err_[n-1]);emit(val_[n-1]);return end_output();}
#endif
