#if EB_FAMILY == 3

#define INF 100000
struct Candidate { int cost, moves; };
static int dp[13][13], vertical[13], horizontal;
static int open_cost, extension, mismatch, n;

static int cost_add(int base, int penalty) {
    return base == INF ? INF : base + penalty;
}

static void offer(struct Candidate *best, int cost, int move) {
    if (cost < best->cost) {
        best->cost = cost;
        best->moves = move;
    }
#if EB_STYLE != 2
    else if (cost != INF && cost == best->cost) best->moves |= move;
#endif
}

static int diagonal(int i, int j) {
    int a = eb_input[5+i], b = eb_input[5+n+j];
    int penalty = a == b || a == 4 || b == 4 ? 0 : mismatch + (a < b);
    return cost_add(dp[i-1][j-1], penalty);
}

#if EB_STYLE == 0
static int gap_from(int base, int length) {
    return cost_add(base, open_cost + extension * (length - 1));
}
static void offer_gaps(struct Candidate *best, int i, int j) {
    int k;
    for (k = 0; k < i; ++k) offer(best, gap_from(dp[k][j], i-k), 2);
    for (k = 0; k < j; ++k) offer(best, gap_from(dp[i][k], j-k), 4);
}
#else
static int extend_minimum(int previous, int gap) {
    int start = cost_add(previous, open_cost);
    int extend = cost_add(gap, extension);
    return start < extend ? start : extend;
}
static void offer_gaps(struct Candidate *best, int i, int j) {
    if (i > 0) vertical[j] = extend_minimum(dp[i-1][j], vertical[j]);
    if (j > 0) horizontal = extend_minimum(dp[i][j-1], horizontal);
    offer(best, vertical[j], 2);
    offer(best, horizontal, 4);
}
#endif

static int align_cell(int i, int j, int band) {
    struct Candidate best;
    best.cost = INF;
    best.moves = 0;
    if (i-j > band || j-i > band) {
        vertical[j] = INF;
        horizontal = INF;
    } else if (i == 0 && j == 0) best.cost = 0;
    else {
        if (i > 0 && j > 0) offer(&best, diagonal(i, j), 1);
        offer_gaps(&best, i, j);
    }
    dp[i][j] = best.cost;
    return best.moves;
}

static void align(int m, int band) {
    int i, j, mask = 0;
    for (j = 0; j <= m; ++j) vertical[j] = INF;
    for (i = 0; i <= n; ++i) {
        horizontal = INF;
        for (j = 0; j <= m; ++j) mask = align_cell(i, j, band);
    }
    emit(dp[n][m] == INF ? -1 : dp[n][m]);
    emit(mask);
}

int main(void) {
    begin_output();
    n = eb_input[0];
    open_cost = eb_input[3];
    extension = eb_input[4];
    mismatch = eb_input[5];
    align(eb_input[1], eb_input[2]);
    return end_output();
}

#else

struct Phase { int index, remainder; };
static int denominator, lower, upper, last;

static void normalize_phase(struct Phase *phase) {
    while (phase->remainder < 0) {
        phase->remainder += denominator;
        --phase->index;
    }
    while (phase->remainder >= denominator) {
        phase->remainder -= denominator;
        ++phase->index;
    }
}

static void split_phase(struct Phase *phase, int coordinate) {
    phase->index = coordinate / denominator;
    phase->remainder = coordinate % denominator;
    normalize_phase(phase);
}

static int round_signed(int numerator) {
    int magnitude = numerator < 0 ? -numerator : numerator;
    int result = magnitude / denominator;
    int twice = 2 * (magnitude % denominator);
#if EB_STYLE == 2
    if (twice > denominator) ++result;
#else
    if (twice >= denominator) ++result;
#endif
    return numerator < 0 ? -result : result;
}

static int interpolate(int index, int rem) {
    int left = eb_input[7+index];
    int right = eb_input[8+index];
    return round_signed((denominator-rem)*left+rem*right);
}

static void emit_sample(const struct Phase *phase) {
    int index = phase->index, rem = phase->remainder;
    int edge = 0, saturation = 0, value;
    if (index < 0) {
        edge = -1;
        value = eb_input[7];
    } else if (index >= last) {
        if (index > last || rem != 0) edge = 1;
        value = eb_input[7+last];
    } else value = interpolate(index, rem);
    if (value < lower) { value = lower; saturation = -1; }
    else if (value > upper) { value = upper; saturation = 1; }
    emit(value); emit(edge); emit(saturation);
}

static void resample(int count, int coordinate, int step) {
    int i;
    struct Phase phase;
    split_phase(&phase, coordinate);
    for (i = 0; i < count; ++i) {
#if EB_STYLE == 0
        split_phase(&phase, coordinate+i*step);
#endif
        emit_sample(&phase);
#if EB_STYLE != 0
        phase.remainder += step;
        normalize_phase(&phase);
#endif
    }
}

int main(void) {
    begin_output();
    last = eb_input[0]-1;
    denominator = eb_input[3];
    lower = eb_input[5];
    upper = eb_input[6];
    resample(eb_input[1], eb_input[4], eb_input[2]);
    return end_output();
}
#endif
