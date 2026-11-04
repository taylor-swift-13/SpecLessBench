typedef unsigned char uint8;
typedef unsigned int uint32;
typedef int x_bool;

/*@ Import Coq From SimpleC.EE.OUTPUT.xizi.xizi_circular_area_read.source Require Import xizi_circular_area_read_lib */
/*@ Extern Coq (circular_area_state :: *) */
/*@ Extern Coq
      (ca_capacity : circular_area_state -> Z)
      (ca_contents : circular_area_state -> list Z)
      (Build_circular_area_state : Z -> list Z -> circular_area_state)
      (store_circular_area : circular_area_state -> Z -> Assertion)
      (CircularAreaLogicalState :
         Z -> Z -> Z -> Z -> list Z -> list (option Z) -> Prop)
      (CircularAreaLiveBytes :
         Z -> Z -> list Z -> list (option Z) -> Prop)
      (CircularAreaStateFullResult : circular_area_state -> Z -> Prop)
      (CircularAreaStateEmptyResult : circular_area_state -> Z -> Prop)
      (CircularAreaStateDataLengthResult : circular_area_state -> Z -> Prop)
      (CircularAreaStateDivideRdDataResult :
         circular_area_state -> Z -> Z -> Prop)
      (CircularAreaReadResult :
         circular_area_state -> Z -> Z -> list (option Z) -> Z ->
         circular_area_state -> list (option Z) -> Prop)
      (CircularAreaReadInput :
         circular_area_state -> (String -> Z) -> Z -> list (option Z) ->
         Z -> Z -> Z -> Assertion)
      (CircularAreaDivideRdDataResult : Z -> Z -> Z -> Z -> Prop)
      (CircularAreaActualReadLength : list Z -> Z -> Z -> Prop)
      (CircularAreaInitializedSlice :
         list (option Z) -> Z -> Z -> list Z -> Prop)
      (CircularAreaSomeBytes : list Z -> list (option Z))
      (CircularAreaReadSuccess :
         Z -> Z -> Z -> Z -> list Z -> list (option Z) -> Z -> Z ->
         list Z -> list Z -> list (option Z) -> Prop)
      (CircularAreaErrorResult : Z -> Prop)
      (UCharArray::seg : Z -> Z -> Z -> list Z -> Assertion)
      (UCharArray::mixed_seg :
         Z -> Z -> Z -> list (option Z) -> Assertion)
*/

uint8 *memcpy(uint8 *dest, uint8 *src, uint32 count)
/*@ With src_base src_lo src_hi
          (dest_before : list (option Z)) (src_contents : list Z)
    Require
      src == src_base + src_lo &&
      count == src_hi - src_lo &&
      Zlength(dest_before) == count &&
      Zlength(src_contents) == count &&
      UCharArray::mixed_full(dest, count, dest_before) *
      UCharArray::mixed_seg(src_base, src_lo, src_hi,
                            CircularAreaSomeBytes(src_contents))
    Ensure
      __return == dest &&
      UCharArray::mixed_full(dest, count,
                             CircularAreaSomeBytes(src_contents)) *
      UCharArray::mixed_seg(src_base, src_lo, src_hi,
                            CircularAreaSomeBytes(src_contents))
*/;

void KPrintf(char *format)
/*@ Require emp
    Ensure emp
*/;

#define NONE ((void *)0)
#define RET_TRUE 1
#define RET_FALSE 0
#define EOK 0
#define ERROR 1
#define NULL_PARAM_CHECK(p) do { if ((p) == NONE) return ERROR; } while (0)
#define CHECK(cond) do { if (!(cond)) return ERROR; } while (0)

struct CircularAreaOps;

struct CircularArea {
    uint8 *data_buffer;
    uint8 readidx;
    uint8 writeidx;
    uint8 *p_head;
    uint8 *p_tail;
    uint32 area_length;
    x_bool b_status;
    struct CircularAreaOps *CircularAreaOperations;
};

typedef struct CircularArea *CircularAreaType;

x_bool CircularAreaIsFull(CircularAreaType circular_area)
/*@ With (state : circular_area_state) LitMap
    Require GlobalStrings(LitMap) * store_circular_area(state, circular_area)
    Ensure CircularAreaStateFullResult(state, __return) &&
           GlobalStrings(LitMap) * store_circular_area(state, circular_area)
*/
{
    /*@ Assert
      exists data_buffer operations readidx writeidx b_status physical,
        circular_area == circular_area@pre && circular_area != 0 &&
        data_buffer != 0 &&
        CircularAreaLogicalState(readidx, writeidx, ca_capacity(state), b_status,
                                 ca_contents(state), physical) &&
        GlobalStrings(LitMap) *
        UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
        store_ptr(&(circular_area->data_buffer), data_buffer) *
        store_uchar(&(circular_area->readidx), readidx) *
        store_uchar(&(circular_area->writeidx), writeidx) *
        store_ptr(&(circular_area->p_head), data_buffer) *
        store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
        store_uint(&(circular_area->area_length), ca_capacity(state)) *
        store_int(&(circular_area->b_status), b_status) *
        store_ptr(&(circular_area->CircularAreaOperations), operations)
    */
    NULL_PARAM_CHECK(circular_area);

    if((circular_area->readidx == circular_area->writeidx) && (circular_area->b_status)) {
        KPrintf("the circular area is full\n");
        return RET_TRUE;
    } else {
        return RET_FALSE;
    }
}

x_bool CircularAreaIsEmpty(CircularAreaType circular_area)
/*@ With (state : circular_area_state) LitMap
    Require GlobalStrings(LitMap) * store_circular_area(state, circular_area)
    Ensure CircularAreaStateEmptyResult(state, __return) &&
           GlobalStrings(LitMap) * store_circular_area(state, circular_area)
*/
{
    /*@ Assert
      exists data_buffer operations readidx writeidx b_status physical,
        circular_area == circular_area@pre && circular_area != 0 &&
        data_buffer != 0 &&
        CircularAreaLogicalState(readidx, writeidx, ca_capacity(state), b_status,
                                 ca_contents(state), physical) &&
        GlobalStrings(LitMap) *
        UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
        store_ptr(&(circular_area->data_buffer), data_buffer) *
        store_uchar(&(circular_area->readidx), readidx) *
        store_uchar(&(circular_area->writeidx), writeidx) *
        store_ptr(&(circular_area->p_head), data_buffer) *
        store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
        store_uint(&(circular_area->area_length), ca_capacity(state)) *
        store_int(&(circular_area->b_status), b_status) *
        store_ptr(&(circular_area->CircularAreaOperations), operations)
    */
    NULL_PARAM_CHECK(circular_area);

    if((circular_area->readidx == circular_area->writeidx) && (!circular_area->b_status)) {
        KPrintf("the circular area is empty\n");
        return RET_TRUE;
    } else {
        return RET_FALSE;
    }
}

uint32 CircularAreaGetDataLength(CircularAreaType circular_area)
/*@ With (state : circular_area_state) LitMap
    Require GlobalStrings(LitMap) * store_circular_area(state, circular_area)
    Ensure CircularAreaStateDataLengthResult(state, __return) &&
           GlobalStrings(LitMap) * store_circular_area(state, circular_area)
*/
{
    NULL_PARAM_CHECK(circular_area);

    if (CircularAreaIsFull(circular_area)
        /*@ where state = state, LitMap = LitMap */) {
        /*@ Assert
          exists data_buffer operations readidx writeidx b_status physical,
            circular_area == circular_area@pre && circular_area != 0 &&
            data_buffer != 0 &&
            Zlength(ca_contents(state)) == ca_capacity(state) &&
            CircularAreaLogicalState(readidx, writeidx, ca_capacity(state), b_status,
                                     ca_contents(state), physical) &&
            GlobalStrings(LitMap) *
            UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
            store_ptr(&(circular_area->data_buffer), data_buffer) *
            store_uchar(&(circular_area->readidx), readidx) *
            store_uchar(&(circular_area->writeidx), writeidx) *
            store_ptr(&(circular_area->p_head), data_buffer) *
            store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
            store_uint(&(circular_area->area_length), ca_capacity(state)) *
            store_int(&(circular_area->b_status), b_status) *
            store_ptr(&(circular_area->CircularAreaOperations), operations)
        */
        return circular_area->area_length;
    } else {
        /*@ Assert
          exists data_buffer operations readidx writeidx b_status physical,
            circular_area == circular_area@pre && circular_area != 0 &&
            data_buffer != 0 &&
            Zlength(ca_contents(state)) < ca_capacity(state) &&
            CircularAreaLogicalState(readidx, writeidx, ca_capacity(state), b_status,
                                     ca_contents(state), physical) &&
            GlobalStrings(LitMap) *
            UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
            store_ptr(&(circular_area->data_buffer), data_buffer) *
            store_uchar(&(circular_area->readidx), readidx) *
            store_uchar(&(circular_area->writeidx), writeidx) *
            store_ptr(&(circular_area->p_head), data_buffer) *
            store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
            store_uint(&(circular_area->area_length), ca_capacity(state)) *
            store_int(&(circular_area->b_status), b_status) *
            store_ptr(&(circular_area->CircularAreaOperations), operations)
        */
        return (circular_area->writeidx - circular_area->readidx +
                circular_area->area_length) % circular_area->area_length;
    }
}

static uint32 CircularAreaDivideRdData(CircularAreaType circular_area,
                                       uint32 data_length)
/*@ With (state : circular_area_state) LitMap
    Require
      0 <= data_length && data_length <= Zlength(ca_contents(state)) &&
      GlobalStrings(LitMap) * store_circular_area(state, circular_area)
    Ensure
      exists data_buffer operations readidx writeidx b_status physical,
        circular_area != 0 && data_buffer != 0 &&
        CircularAreaStateDivideRdDataResult(state, data_length@pre, __return) &&
        CircularAreaDivideRdDataResult(
          readidx, data_length@pre, ca_capacity(state), __return) &&
        CircularAreaLogicalState(
          readidx, writeidx, ca_capacity(state), b_status,
          ca_contents(state), physical) &&
        GlobalStrings(LitMap) *
        UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
        store_ptr(&(circular_area->data_buffer), data_buffer) *
        store_uchar(&(circular_area->readidx), readidx) *
        store_uchar(&(circular_area->writeidx), writeidx) *
        store_ptr(&(circular_area->p_head), data_buffer) *
        store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
        store_uint(&(circular_area->area_length), ca_capacity(state)) *
        store_int(&(circular_area->b_status), b_status) *
        store_ptr(&(circular_area->CircularAreaOperations), operations)
*/
{
    /*@ Assert
      exists data_buffer operations readidx writeidx b_status physical,
        circular_area == circular_area@pre && data_length == data_length@pre &&
        circular_area != 0 && data_buffer != 0 &&
        0 <= data_length@pre &&
        data_length@pre <= Zlength(ca_contents(state)) &&
        readidx + data_length@pre <= UINT_MAX &&
        CircularAreaLogicalState(readidx, writeidx, ca_capacity(state), b_status,
                                 ca_contents(state), physical) &&
        GlobalStrings(LitMap) *
        UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
        store_ptr(&(circular_area->data_buffer), data_buffer) *
        store_uchar(&(circular_area->readidx), readidx) *
        store_uchar(&(circular_area->writeidx), writeidx) *
        store_ptr(&(circular_area->p_head), data_buffer) *
        store_ptr(&(circular_area->p_tail), data_buffer + ca_capacity(state)) *
        store_uint(&(circular_area->area_length), ca_capacity(state)) *
        store_int(&(circular_area->b_status), b_status) *
        store_ptr(&(circular_area->CircularAreaOperations), operations)
    */
    NULL_PARAM_CHECK(circular_area);

    if (circular_area->readidx + data_length <= circular_area->area_length) {
        return RET_FALSE;
    } else {
        return RET_TRUE;
    }
}

uint32 CircularAreaRead(CircularAreaType circular_area, uint8 *output_buffer,
                        uint32 data_length)
/*@ With (state : circular_area_state) LitMap
          output_capacity output_before
    Require
      CircularAreaReadInput(state, LitMap, output_capacity, output_before,
                            circular_area, output_buffer, data_length)
    Ensure
      GlobalStrings(LitMap) *
      ((circular_area@pre == 0 && CircularAreaErrorResult(__return) && emp) ||
      (circular_area@pre != 0 && output_buffer@pre == 0 &&
       CircularAreaErrorResult(__return) &&
       store_circular_area(state, circular_area@pre)) ||
      (exists state_after output_after,
       circular_area@pre != 0 && output_buffer@pre != 0 &&
       CircularAreaReadResult(state, data_length@pre, output_capacity,
                              output_before, __return, state_after,
                              output_after) &&
       store_circular_area(state_after, circular_area@pre) *
       UCharArray::mixed_full(output_buffer@pre, output_capacity, output_after))
      )
*/
{
    /*@ Assert
      circular_area == circular_area@pre &&
      output_buffer == output_buffer@pre &&
      data_length == data_length@pre &&
      0 <= data_length@pre && data_length@pre <= UINT_MAX &&
      GlobalStrings(LitMap) *
      ((circular_area == 0 && emp) ||
      (circular_area != 0 &&
       store_circular_area(state, circular_area) *
       ((output_buffer == 0 && emp) ||
        (output_buffer != 0 &&
         data_length@pre <= output_capacity &&
         UCharArray::mixed_full(output_buffer, output_capacity,
                                output_before)))))
    */
    NULL_PARAM_CHECK(circular_area);
    NULL_PARAM_CHECK(output_buffer);
    /*@ 0 <= data_length && data_length <= UINT_MAX by local */
    CHECK(data_length > 0);

    if (CircularAreaIsEmpty(circular_area)
        /*@ where state = state, LitMap = LitMap */) {
        /*@ Assert
          circular_area != 0 && output_buffer != 0 && data_length > 0 &&
          circular_area == circular_area@pre &&
          output_buffer == output_buffer@pre &&
          data_length == data_length@pre &&
          data_length <= output_capacity &&
          CircularAreaStateEmptyResult(state, 1) &&
          GlobalStrings(LitMap) *
          store_circular_area(state, circular_area@pre) *
          UCharArray::mixed_full(output_buffer, output_capacity, output_before) *
          emp
        */
        return ERROR;
    }

    data_length = (data_length > CircularAreaGetDataLength(circular_area)
                   /*@ where state = state, LitMap = LitMap */) ?
        CircularAreaGetDataLength(circular_area)
        /*@ where state = state, LitMap = LitMap */ : data_length;

    if (CircularAreaDivideRdData(circular_area, data_length)
        /*@ where state = state, LitMap = LitMap */) {
        /*@ Assert
          exists data_buffer operations readidx writeidx area_length b_status logical physical,
            circular_area == circular_area@pre &&
            output_buffer == output_buffer@pre &&
            circular_area@pre != 0 && output_buffer@pre != 0 &&
            data_buffer != 0 && data_length@pre > 0 &&
            area_length == ca_capacity(state) &&
            logical == ca_contents(state) &&
            CircularAreaStateEmptyResult(state, 0) &&
            CircularAreaActualReadLength(ca_contents(state), data_length@pre,
                                         data_length) &&
            0 < data_length && data_length <= output_capacity &&
            CircularAreaDivideRdDataResult(
              readidx, data_length, ca_capacity(state), 1) &&
            CircularAreaLogicalState(
              readidx, writeidx, ca_capacity(state), b_status,
              ca_contents(state), physical) &&
            GlobalStrings(LitMap) *
            UCharArray::mixed_full(data_buffer, ca_capacity(state), physical) *
            UCharArray::mixed_full(output_buffer, output_capacity, output_before) *
            store_ptr(&(circular_area@pre->data_buffer), data_buffer) *
            store_uchar(&(circular_area@pre->readidx), readidx) *
            store_uchar(&(circular_area@pre->writeidx), writeidx) *
            store_ptr(&(circular_area@pre->p_head), data_buffer) *
            store_ptr(&(circular_area@pre->p_tail),
                      data_buffer + ca_capacity(state)) *
            store_uint(&(circular_area@pre->area_length), ca_capacity(state)) *
            store_int(&(circular_area@pre->b_status), b_status) *
            store_ptr(&(circular_area@pre->CircularAreaOperations), operations)
        */
        uint32 read_len_up = circular_area->area_length -
            circular_area->readidx;
        uint32 read_len_down = data_length - read_len_up;

        /*@ Assert
          exists data_buffer operations readidx writeidx area_length b_status logical physical,
          circular_area == circular_area@pre &&
          output_buffer == output_buffer@pre &&
          circular_area@pre != 0 && output_buffer@pre != 0 &&
          data_buffer != 0 && data_length@pre > 0 &&
          area_length == ca_capacity(state) &&
          logical == ca_contents(state) &&
          CircularAreaStateEmptyResult(state, 0) &&
          CircularAreaActualReadLength(logical, data_length@pre, data_length) &&
          0 < data_length && data_length <= output_capacity &&
          0 <= readidx && readidx < area_length &&
          read_len_up == area_length - readidx &&
          read_len_down == data_length - read_len_up &&
          read_len_up <= data_length &&
          CircularAreaDivideRdDataResult(readidx, data_length, area_length, 1) &&
          CircularAreaLogicalState(readidx, writeidx, area_length, b_status,
                                   logical, physical) &&
          CircularAreaLiveBytes(readidx, area_length, logical, physical) &&
          CircularAreaInitializedSlice(physical, readidx, area_length,
                                       sublist(0, read_len_up, logical)) &&
          GlobalStrings(LitMap) *
          UCharArray::mixed_seg(data_buffer, 0, readidx,
                                sublist(0, readidx, physical)) *
          UCharArray::mixed_seg(data_buffer, readidx, area_length,
                                CircularAreaSomeBytes(
                                  sublist(0, read_len_up, logical))) *
          UCharArray::mixed_full(output_buffer, read_len_up,
                                 sublist(0, read_len_up, output_before)) *
          UCharArray::mixed_seg(output_buffer, read_len_up, output_capacity,
                                sublist(read_len_up, output_capacity,
                                        output_before)) *
          store_ptr(&(circular_area@pre->data_buffer), data_buffer) *
          store_uchar(&(circular_area@pre->readidx), readidx) *
          store_uchar(&(circular_area@pre->writeidx), writeidx) *
          store_ptr(&(circular_area@pre->p_head), data_buffer) *
          store_ptr(&(circular_area@pre->p_tail), data_buffer + area_length) *
          store_uint(&(circular_area@pre->area_length), area_length) *
          store_int(&(circular_area@pre->b_status), b_status) *
          store_ptr(&(circular_area@pre->CircularAreaOperations), operations)
        */
        memcpy(output_buffer,
               &circular_area->data_buffer[circular_area->readidx],
               read_len_up)
        /*@ where src_base = circular_area->data_buffer,
                  src_lo = circular_area->readidx,
                  src_hi = circular_area->area_length,
                  dest_before = sublist(0, read_len_up, output_before),
                  src_contents = sublist(0, read_len_up, ca_contents(state)) */;
        /*@ Assert
          exists data_buffer operations readidx writeidx area_length b_status logical physical,
          circular_area == circular_area@pre &&
          output_buffer == output_buffer@pre &&
          circular_area@pre != 0 && output_buffer@pre != 0 &&
          data_buffer != 0 && data_length@pre > 0 &&
          area_length == ca_capacity(state) &&
          logical == ca_contents(state) &&
          CircularAreaStateEmptyResult(state, 0) &&
          CircularAreaActualReadLength(logical, data_length@pre, data_length) &&
          0 < data_length && data_length <= output_capacity &&
          0 <= read_len_down && read_len_down <= readidx &&
          read_len_up == area_length - readidx &&
          read_len_down == data_length - read_len_up &&
          CircularAreaDivideRdDataResult(readidx, data_length, area_length, 1) &&
          CircularAreaLogicalState(readidx, writeidx, area_length, b_status,
                                   logical, physical) &&
          CircularAreaLiveBytes(readidx, area_length, logical, physical) &&
          CircularAreaInitializedSlice(physical, 0, read_len_down,
                                       sublist(read_len_up, data_length, logical)) &&
          GlobalStrings(LitMap) *
          UCharArray::mixed_seg(data_buffer, 0, read_len_down,
                                CircularAreaSomeBytes(
                                  sublist(read_len_up, data_length, logical))) *
          UCharArray::mixed_seg(data_buffer, read_len_down, readidx,
                                sublist(read_len_down, readidx, physical)) *
          UCharArray::mixed_seg(data_buffer, readidx, area_length,
                                sublist(readidx, area_length, physical)) *
          UCharArray::mixed_seg(output_buffer, 0, read_len_up,
                                CircularAreaSomeBytes(
                                  sublist(0, read_len_up, logical))) *
          UCharArray::mixed_full(output_buffer + read_len_up, read_len_down,
                                 sublist(read_len_up, data_length,
                                         output_before)) *
          UCharArray::mixed_seg(output_buffer, data_length, output_capacity,
                                sublist(data_length, output_capacity,
                                        output_before)) *
          store_ptr(&(circular_area@pre->data_buffer), data_buffer) *
          store_uchar(&(circular_area@pre->readidx), readidx) *
          store_uchar(&(circular_area@pre->writeidx), writeidx) *
          store_ptr(&(circular_area@pre->p_head), data_buffer) *
          store_ptr(&(circular_area@pre->p_tail), data_buffer + area_length) *
          store_uint(&(circular_area@pre->area_length), area_length) *
          store_int(&(circular_area@pre->b_status), b_status) *
          store_ptr(&(circular_area@pre->CircularAreaOperations), operations)
        */
        memcpy(output_buffer + read_len_up, circular_area->p_head,
               read_len_down)
        /*@ where src_base = circular_area->p_head, src_lo = 0,
                  src_hi = read_len_down,
                  dest_before = sublist(read_len_up, data_length, output_before),
                  src_contents =
                    sublist(read_len_up, data_length, ca_contents(state)) */;

        circular_area->readidx = read_len_down;
    } else {
        /*@ Assert
          exists data_buffer operations readidx writeidx area_length b_status logical physical,
          circular_area == circular_area@pre &&
          output_buffer == output_buffer@pre &&
          circular_area@pre != 0 && output_buffer@pre != 0 &&
          data_buffer != 0 && data_length@pre > 0 &&
          area_length == ca_capacity(state) &&
          logical == ca_contents(state) &&
          CircularAreaStateEmptyResult(state, 0) &&
          CircularAreaActualReadLength(logical, data_length@pre, data_length) &&
          0 < data_length && data_length <= output_capacity &&
          0 <= readidx && readidx + data_length <= area_length &&
          CircularAreaDivideRdDataResult(readidx, data_length, area_length, 0) &&
          CircularAreaLogicalState(readidx, writeidx, area_length, b_status,
                                   logical, physical) &&
          CircularAreaLiveBytes(readidx, area_length, logical, physical) &&
          CircularAreaInitializedSlice(physical, readidx,
                                       readidx + data_length,
                                       sublist(0, data_length, logical)) &&
          GlobalStrings(LitMap) *
          UCharArray::mixed_seg(data_buffer, 0, readidx,
                                sublist(0, readidx, physical)) *
          UCharArray::mixed_seg(data_buffer, readidx, readidx + data_length,
                                CircularAreaSomeBytes(
                                  sublist(0, data_length, logical))) *
          UCharArray::mixed_seg(data_buffer, readidx + data_length, area_length,
                                sublist(readidx + data_length, area_length, physical)) *
          UCharArray::mixed_full(output_buffer, data_length,
                                 sublist(0, data_length, output_before)) *
          UCharArray::mixed_seg(output_buffer, data_length, output_capacity,
                                sublist(data_length, output_capacity,
                                        output_before)) *
          store_ptr(&(circular_area@pre->data_buffer), data_buffer) *
          store_uchar(&(circular_area@pre->readidx), readidx) *
          store_uchar(&(circular_area@pre->writeidx), writeidx) *
          store_ptr(&(circular_area@pre->p_head), data_buffer) *
          store_ptr(&(circular_area@pre->p_tail), data_buffer + area_length) *
          store_uint(&(circular_area@pre->area_length), area_length) *
          store_int(&(circular_area@pre->b_status), b_status) *
          store_ptr(&(circular_area@pre->CircularAreaOperations), operations)
        */
        memcpy(output_buffer,
               &circular_area->data_buffer[circular_area->readidx],
               data_length)
        /*@ where src_base = circular_area->data_buffer,
                  src_lo = circular_area->readidx,
                  src_hi = circular_area->readidx + data_length,
                  dest_before = sublist(0, data_length, output_before),
                  src_contents = sublist(0, data_length, ca_contents(state)) */;
        circular_area->readidx =
            (circular_area->readidx + data_length) %
            circular_area->area_length;
    }

    circular_area->b_status = RET_FALSE;

    return EOK;
}
