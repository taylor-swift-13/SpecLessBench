/* Newly authored bounded APIs; every reachable helper body is fixed.
 * This header is preprocessed into each concrete family/style program. */
#include "../../qcip-core/common/io.h"
#if EB_FAMILY == 0
struct Stream {int data[32];int head;int count;int base;int code;int pos;};
static struct Stream st;
static int peek_byte(int k){
#if EB_STYLE == 0
 return st.data[k];
#else
 return st.data[(st.head+k)%32];
#endif
}
static void push_byte(int c){
#if EB_STYLE == 0
 st.data[st.count]=c;
#else
 st.data[(st.head+st.count)%32]=c;
#endif
 st.count=st.count+1;}
static void drop_bytes(int k){int i;
#if EB_STYLE == 0
 for(i=k;i<st.count;i=i+1)st.data[i-k]=st.data[i];
#else
 st.head=(st.head+k)%32;
#endif
 st.count=st.count-k;st.base=st.base+k;}
static int checksum_frame(int size){int i,x=0;for(i=0;i<size-1;i=i+1)x=x^peek_byte(i);return x;}
static void stream_error(int code,int pos){st.code=code;st.pos=pos;}
static int drain_frames(int *out){int used=0,tag,len,size,i,frames=0;
 while(st.count>0&&st.code==0){tag=peek_byte(0);
  if(tag<1||tag>3){stream_error(1,st.base);break;}
  if(st.count<2)break;len=peek_byte(1);
  if(len>8){stream_error(2,st.base+1);break;}
  size=len+3;if(st.count<size)break;
  if(checksum_frame(size)!=peek_byte(size-1)){stream_error(3,st.base+size-1);break;}
  out[used++]=tag;out[used++]=len;for(i=0;i<len;i=i+1)out[used++]=peek_byte(2+i);
  frames=frames+1;drop_bytes(size);
 }out[128]=frames;return used;}
static void reset_stream(void){st.head=0;st.count=0;st.base=0;st.code=0;st.pos=-1;}
static int feed_chunk(int *src,int n,int *out){int i;
 if(st.code!=0){out[128]=0;return 0;}
#if EB_STYLE == 2
 if(n==0){st.count=0;}
#endif
 for(i=0;i<n;i=i+1)push_byte(src[i]);return drain_frames(out);}
static void finish_stream(void){if(st.code==0&&st.count>0)stream_error(4,st.base);}
static void observe_stream(int op,int *frames,int used){int i;emit(op);emit(st.code);emit(st.pos);emit(st.base);emit(frames[128]);
 for(i=0;i<used;i=i+1)emit(frames[i]);emit(st.count);for(i=0;i<st.count;i=i+1)emit(peek_byte(i));}
int main(void){int q=eb_input[0],i,p,op,len,used,frames[129];begin_output();reset_stream();
 for(i=0;i<q;i=i+1){p=1+10*i;op=eb_input[p];len=eb_input[p+1];used=0;frames[128]=0;
  if(op==0)used=feed_chunk(eb_input+p+2,len,frames);else if(op==1)finish_stream();else reset_stream();
  observe_stream(op,frames,used);
 }return end_output();}
#elif EB_FAMILY == 1
struct Undo {int key;int found;int value;};
static int found_[8],value_[8],depth_,saved_f[8][8],saved_v[8][8],mark_[8],used_;
static struct Undo journal[64];
static void read_slot(int key,int *found,int *value){*found=found_[key];*value=value_[key];}
static void write_slot(int key,int found,int value){found_[key]=found;value_[key]=value;}
static void append_undo(int key){int f,v;
#if EB_STYLE != 0
 if(depth_>0){read_slot(key,&f,&v);journal[used_].key=key;journal[used_].found=f;journal[used_].value=v;used_=used_+1;}
#endif
}
static void tx_write(int key,int found,int value){append_undo(key);write_slot(key,found,value);}
static int tx_begin(void){int k;if(depth_==8)return 2;
#if EB_STYLE == 0
 for(k=0;k<8;k=k+1){saved_f[depth_][k]=found_[k];saved_v[depth_][k]=value_[k];}
#else
 mark_[depth_]=used_;
#endif
 depth_=depth_+1;return 0;}
static int tx_commit(void){if(depth_==0)return 1;depth_=depth_-1;
#if EB_STYLE == 2
 used_=mark_[depth_];
#else
 if(depth_==0)used_=0;
#endif
 return 0;}
static void restore_undo(int i){write_slot(journal[i].key,journal[i].found,journal[i].value);}
static void undo_to(int mark){while(used_>mark){used_=used_-1;restore_undo(used_);}}
static int tx_rollback(void){int k;if(depth_==0)return 1;depth_=depth_-1;
#if EB_STYLE == 0
 for(k=0;k<8;k=k+1)write_slot(k,saved_f[depth_][k],saved_v[depth_][k]);
#else
 undo_to(mark_[depth_]);
#endif
 return 0;}
static void execute_tx(int op,int key,int value){int code=0,f=0,v=0;
 if(op==0)tx_write(key,1,value);else if(op==1)tx_write(key,0,0);else if(op==2)read_slot(key,&f,&v);
 else if(op==3)code=tx_begin();else if(op==4)code=tx_commit();else code=tx_rollback();
 emit(op);emit(code);emit(f);emit(v);emit(depth_);}
int main(void){int q=eb_input[0],i,k;begin_output();depth_=0;used_=0;for(k=0;k<8;k=k+1)write_slot(k,0,0);
 for(i=0;i<q;i=i+1)execute_tx(eb_input[1+3*i],eb_input[2+3*i],eb_input[3+3*i]);
 emit(depth_);for(k=0;k<8;k=k+1){emit(found_[k]);emit(value_[k]);}return end_output();}
#else
struct CacheNode {int key;int value;int prev;int next;int live;};
static struct CacheNode nodes[8];
static int keys[8],vals[8],size_,cap_,head_,tail_;
static int lookup_key(int key){int i;
#if EB_STYLE == 0
 for(i=0;i<size_;i=i+1)if(keys[i]==key)return i;
#else
 for(i=0;i<8;i=i+1)if(nodes[i].live&&nodes[i].key==key)return i;
#endif
 return -1;}
static int key_at(int i){
#if EB_STYLE == 0
 return keys[i];
#else
 return nodes[i].key;
#endif
}
static int value_at(int i){
#if EB_STYLE == 0
 return vals[i];
#else
 return nodes[i].value;
#endif
}
static void detach(int id){int p=nodes[id].prev,n=nodes[id].next;
 if(p<0)head_=n;else nodes[p].next=n;if(n<0)tail_=p;else nodes[n].prev=p;}
static void link_front(int id){nodes[id].prev=-1;nodes[id].next=head_;
 if(head_<0)tail_=id;else nodes[head_].prev=id;head_=id;}
static void erase_at(int id){int i;
#if EB_STYLE == 0
 for(i=id+1;i<size_;i=i+1){keys[i-1]=keys[i];vals[i-1]=vals[i];}
#else
 detach(id);nodes[id].live=0;
#endif
 size_=size_-1;}
static void touch(int id){int i,k,v;
#if EB_STYLE == 0
 k=keys[id];v=vals[id];for(i=id;i>0;i=i-1){keys[i]=keys[i-1];vals[i]=vals[i-1];}keys[0]=k;vals[0]=v;
#else
 detach(id);link_front(id);
#endif
}
static void set_value(int id,int v){
#if EB_STYLE == 0
 vals[id]=v;
#else
 nodes[id].value=v;
#endif
}
static void insert_front(int key,int value){int i,id;
#if EB_STYLE == 0
 for(i=size_;i>0;i=i-1){keys[i]=keys[i-1];vals[i]=vals[i-1];}keys[0]=key;vals[0]=value;
#else
 id=0;while(nodes[id].live)id=id+1;nodes[id].key=key;nodes[id].value=value;nodes[id].live=1;link_front(id);
#endif
 size_=size_+1;}
static void evict_tail(int *out,int *n){int id;
#if EB_STYLE == 0
 id=size_-1;
#else
 id=tail_;
#endif
 out[2*(*n)]=key_at(id);out[2*(*n)+1]=value_at(id);*n=*n+1;erase_at(id);}
static int cache_put(int key,int value,int *out,int *n){int id=lookup_key(key);if(id>=0){set_value(id,value);touch(id);return 1;}
 if(cap_==0)return 0;if(size_==cap_)evict_tail(out,n);insert_front(key,value);return 1;}
static int cache_query(int key,int update,int *value){int id=lookup_key(key);if(id<0){*value=0;return 0;}*value=value_at(id);
#if EB_STYLE != 2
 if(update)touch(id);
#endif
 return 1;}
static void resize_cache(int cap,int *out,int *n){cap_=cap;while(size_>cap_)evict_tail(out,n);}
static void execute_cache(int op,int key,int value){int out[16],n=0,status=0,v=0,id,i;
 if(op==0)status=cache_put(key,value,out,&n);else if(op==1||op==2)status=cache_query(key,op==1,&v);
 else if(op==3){id=lookup_key(key);if(id>=0){status=1;v=value_at(id);erase_at(id);}}
 else{resize_cache(key,out,&n);status=1;v=key;}
 emit(op);emit(status);emit(v);emit(n);for(i=0;i<2*n;i=i+1)emit(out[i]);}
static void observe_cache(void){int i,id;emit(cap_);emit(size_);
#if EB_STYLE == 0
 for(i=0;i<size_;i=i+1){emit(keys[i]);emit(vals[i]);}
#else
 id=head_;while(id>=0){emit(nodes[id].key);emit(nodes[id].value);id=nodes[id].next;}
#endif
}
int main(void){int q=eb_input[1],i;begin_output();cap_=eb_input[0];size_=0;head_=-1;tail_=-1;
 for(i=0;i<8;i=i+1){nodes[i].live=0;nodes[i].prev=-1;nodes[i].next=-1;}
 for(i=0;i<q;i=i+1)execute_cache(eb_input[2+3*i],eb_input[3+3*i],eb_input[4+3*i]);observe_cache();return end_output();}
#endif
