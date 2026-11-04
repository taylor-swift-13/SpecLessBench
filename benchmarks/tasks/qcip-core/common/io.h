/* SpecLessBench derived tasks. No I/O, allocation, or unspecified callees. */
#ifndef SPECLESSBENCH_IO_H
#define SPECLESSBENCH_IO_H
#define EB_INPUT_WORDS 8192
#define EB_OUTPUT_WORDS 8192
int eb_input[EB_INPUT_WORDS];
int eb_output[EB_OUTPUT_WORDS];
static int eb_out;
static void emit(int x) { eb_output[eb_out] = x; eb_out = eb_out + 1; }
static void begin_output(void) {
    int i;
    for (i = 0; i < EB_OUTPUT_WORDS; i = i + 1) eb_output[i] = 0;
    eb_out = 1;
}
static int end_output(void) { eb_output[0] = eb_out - 1; return 0; }
#endif
