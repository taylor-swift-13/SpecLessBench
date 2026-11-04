/* Private bounded byte formats, not claims of OS/shell/protocol compliance.
 * Malformed content is admitted and its precise error observation is compared. */
#include "../../qcip-core/common/io.h"
#if EB_FAMILY == 4
static int records[256],nr,nrecords,status_,offset_;
static void put_record(int tag,int len,int *data){int i,v;records[nr++]=tag;
    if(tag==1){
#if EB_STYLE == 2
        v=256*data[0]+data[1];
#else
        v=data[0]+256*data[1];
#endif
        records[nr++]=v;
    }else if(tag==3)records[nr++]=data[0];else{records[nr++]=len;for(i=0;i<len;i=i+1)records[nr++]=data[i];}
    nrecords=nrecords+1;}
static int record_at(int *src,int remain,int start){int tag,len,i,sum;
    if(remain<3){status_=1;offset_=start;return 0;}
    tag=src[0];len=src[1]+256*src[2];
    if(tag<1||tag>3){status_=2;offset_=start;return 0;}
    if(len>32){status_=3;offset_=start;return 0;}
    if(remain<4+len){status_=4;offset_=start;return 0;}
    if((tag==1&&len!=2)||(tag==3&&len!=1)){status_=5;offset_=start;return 0;}
    sum=tag^src[1]^src[2];for(i=0;i<len;i=i+1)sum=sum^src[3+i];
    if(sum!=src[3+len]){status_=7;offset_=start+3+len;return 0;}
    if(tag==3&&src[3]>1){status_=6;offset_=start+3;return 0;}
    put_record(tag,len,src+3);return len+4;}
static void parse_suffix(int *src,int remain,int start){int used;if(remain==0){offset_=start;return;}
    used=record_at(src,remain,start);if(used>0)parse_suffix(src+used,remain-used,start+used);}
int main(void){int n=eb_input[0],p=0,used,i;begin_output();nr=0;nrecords=0;status_=0;offset_=0;
#if EB_STYLE == 1
    parse_suffix(eb_input+1,n,0);
#else
    while(p<n){used=record_at(eb_input+1+p,n-p,p);if(used==0)break;p=p+used;}if(status_==0)offset_=n;
#endif
    emit(status_);emit(offset_);emit(nrecords);for(i=0;i<nr;i=i+1)emit(records[i]);return end_output();}
#elif EB_FAMILY == 5
static int mode_,opening,escape_,slash_,active,cur[64],nc,tokens[128],nt,flat,status_,offset_;
static void add_char(int c){cur[nc++]=c;active=1;}
static void commit_token(void){int i;if(active){tokens[flat++]=nc;for(i=0;i<nc;i=i+1)tokens[flat++]=cur[i];nt=nt+1;}active=0;nc=0;}
static void step(int c,int p){if(c==0){status_=3;offset_=p;return;}
    if(escape_){add_char(c);escape_=0;return;}
    if(mode_==1){if(c==39)mode_=0;else add_char(c);return;}
    if(c==92){escape_=1;slash_=p;return;}
    if(mode_==2){if(c==34)mode_=0;else add_char(c);return;}
    if(c==9||c==32){commit_token();return;}
    if(c==39||c==34){mode_=c==39?1:2;opening=p;
#if EB_STYLE != 2
        active=1;
#endif
        return;}
    add_char(c);}
static int ordinary(int c){return c!=0&&c!=9&&c!=32&&c!=34&&c!=39&&c!=92;}
int main(void){int n=eb_input[0],p=0,e,i;begin_output();mode_=0;opening=0;escape_=0;slash_=0;active=0;nc=0;nt=0;flat=0;status_=0;offset_=n;
    while(p<n&&status_==0){
#if EB_STYLE == 1
        if(mode_==0&&!escape_&&ordinary(eb_input[1+p])){e=p;while(e<n&&ordinary(eb_input[1+e]))e=e+1;for(i=p;i<e;i=i+1)add_char(eb_input[1+i]);p=e;}
        else{step(eb_input[1+p],p);p=p+1;}
#else
        step(eb_input[1+p],p);p=p+1;
#endif
    }
    if(status_==0){if(escape_){status_=1;offset_=slash_;}else if(mode_!=0){status_=2;offset_=opening;}else commit_token();}
    emit(status_);emit(offset_);emit(nt);for(i=0;i<flat;i=i+1)emit(tokens[i]);return end_output();}
#elif EB_FAMILY == 6
static int decoded[96],produced,status_,offset_;
static int block(int *src,int remain,int start,int cap){int control=src[0],count,i,used;
    if(control==128)return 1;
    count=control<128?control+1:257-control;
#if EB_STYLE == 2
    if(control>128)count=count-1;
#endif
    used=control<128?count+1:2;
    if(remain<used){status_=1;offset_=start;return 0;}
    if(produced+count>cap){status_=2;offset_=start;return 0;}
    for(i=0;i<count;i=i+1)decoded[produced+i]=control<128?src[1+i]:src[1];
    produced=produced+count;return used;}
static void suffix(int *src,int remain,int start,int cap){int used;if(remain==0){offset_=start;return;}used=block(src,remain,start,cap);if(used>0)suffix(src+used,remain-used,start+used,cap);}
int main(void){int n=eb_input[0],cap=eb_input[1],p=0,used,i;begin_output();produced=0;status_=0;offset_=n;
#if EB_STYLE == 1
    suffix(eb_input+2,n,0,cap);
#else
    while(p<n){used=block(eb_input+2+p,n-p,p,cap);if(used==0)break;p=p+used;}
#endif
    emit(status_);emit(offset_);emit(produced);for(i=0;i<produced;i=i+1)emit(decoded[i]);return end_output();}
#else
static int start_[64],length_[64],chosen[64],nc,top,result[128],outn;
static int is_dot(int id){return length_[id]==1&&eb_input[1+start_[id]]==46;}
static int is_parent(int id){return length_[id]==2&&eb_input[1+start_[id]]==46&&eb_input[2+start_[id]]==46;}
static void append_parent(void){if(outn>0&&result[outn-1]!=47)result[outn++]=47;result[outn++]=46;result[outn++]=46;}
static void append_segment(int id){int i;if(outn>0&&result[outn-1]!=47)result[outn++]=47;for(i=0;i<length_[id];i=i+1)result[outn++]=eb_input[1+start_[id]+i];}
int main(void){int n=eb_input[0],p=0,a,i,absolute,pending=0;begin_output();nc=0;top=0;outn=0;
    for(i=0;i<n;i=i+1)if(eb_input[1+i]==0){emit(1);emit(i);emit(0);return end_output();}
    absolute=n>0&&eb_input[1]==47;
    while(p<n){while(p<n&&eb_input[1+p]==47)p=p+1;if(p==n)break;a=p;while(p<n&&eb_input[1+p]!=47)p=p+1;start_[nc]=a;length_[nc]=p-a;nc=nc+1;}
#if EB_STYLE == 1
    for(i=nc;i>0;i=i-1){a=i-1;if(is_dot(a))continue;if(is_parent(a))pending=pending+1;else if(pending>0)pending=pending-1;else chosen[top++]=a;}
    if(absolute)result[outn++]=47;else while(pending>0){append_parent();pending=pending-1;}
    while(top>0){top=top-1;append_segment(chosen[top]);}
#else
    for(i=0;i<nc;i=i+1){if(is_dot(i))continue;if(is_parent(i)){
#if EB_STYLE == 2
        if(top>0)top=top-1;else if(!absolute)chosen[top++]=i;
#else
        if(top>0&&!is_parent(chosen[top-1]))top=top-1;else if(!absolute)chosen[top++]=i;
#endif
    }else chosen[top++]=i;}
    if(absolute)result[outn++]=47;for(i=0;i<top;i=i+1)append_segment(chosen[i]);
#endif
    if(outn==0)result[outn++]=46;emit(0);emit(n);emit(outn);for(i=0;i<outn;i=i+1)emit(result[i]);return end_output();}
#endif
