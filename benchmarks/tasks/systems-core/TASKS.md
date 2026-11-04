# Executable references for graph, state and numerical tasks

Each group fixes a reference V0, an alternate V1 and a mutant V2. The positive task pairs V0/V1 and the refutation task pairs V0/V2. The Lean and Rocq targets quantify over the admitted wire inputs and require both programs to return the same successful observation. The CompCert targets use the same admitted inputs and compare safe terminating Clight runs through the initialized input and output globals. The length prefix and zero padding are part of the transport. Below, observations omit the length prefix.

The reference programs define the behavior used for comparison. The prose describes the chosen interface and test boundaries. The formal targets remain pending.

| Task IDs | Reference and alternate | Refutation mutant |
|---|---|---|
| G-INVALIDATE-WORKLIST / G-INVALIDATE-DIRTY | Eight full graph passes / enqueue-once reachability | Skips an already dirty intermediate |
| N-SCOPE-OVERLAY / N-SCOPE-TOMBSTONE | Complete scope snapshots / layered bindings | Treats an explicit hide as inheritance |
| T-LEASE-WHEEL / T-LEASE-STALE | Scan absolute deadlines / rotate a nine-slot time wheel | Retains a previous scheduled expiry when renewing |
| A-ALIGN-MINIMA / A-ALIGN-TIES | Enumerate gap predecessors / maintain directional running minima | Retains only the first cheapest direction |
| A-RESAMPLE-PHASE / A-RESAMPLE-HALF | Recompute phase by division / incrementally normalize phase | Rounds signed halves toward zero |

## G. Invalidation through changing dependencies

The input is `[q]` followed by up to 64 commands `[op,a,b,0]`. The graph starts empty with eight clean vertices. Operations 0 and 1 add or remove edge `a→b`. Operation 2 marks the root and all vertices reachable from it as dirty. Operation 3 clears the dirty bit of a single vertex. Operation 4 reads that bit. For operations 2–4, b is zero. Vertex numbers range from 0 to 7. Edge edits do not themselves trigger propagation. Cycles, self-edges, redundant edits and repeated invalidations are admitted.

Each command emits `[op,result,dirtyMask]`, with result zero except on reads. A three-node history adds 0→1, invalidates 0, adds 1→2, then invalidates 0 again. A fresh reachability traversal must pass through dirty vertex 1. The work queue marks a vertex reached at insertion time so an eight-slot queue suffices.

## N. Scoped lookup and deletion masks

The input is `[q]` followed by up to 64 commands `[op,key,value,0]`. The base scope contains eight absent bindings. Operations 0, 1 and 2 bind, hide and query a key. Bind values lie in [-1000,1000], and other value fields are zero. Operations 3 and 4 push and pop with zero key/value fields. Up to four inner scopes may be open. Pushing at the depth limit yields status 2. Popping the base yields status 1. Successful commands yield status 0.

Each command emits `[op,status,found,value,depth]`. Only queries populate found and value. Missing values encode as 0/0. The final visible map appends eight found/value pairs in key order. A hide masks the name until overwritten or until its own scope pops. The overlay represents inheritance and explicit absence separately. Bind a base value, push and hide it to expose the mutant.

## T. Renewal and ordered expiry

The input is `[q]` followed by up to 64 commands `[op,a,b,c]`. The eight-key table starts empty at tick zero. Operation 0 inserts or renews key a with value b in [-1000,1000] and TTL c in [1,8]. Operations 1 and 2 read or erase a key, and b and c are zero. Operation 3 advances a in [0,4] ticks, with b and c zero. Advance visits each crossed tick. A lease expires at its absolute deadline. Renew replaces both the value and the deadline.

Each command emits `[op,found,value,count]` followed by count expired keys. Read and erase populate found/value using the prior binding. Advance emits expired keys ordered by tick and then ascending key. Final clock and eight live/value pairs follow the command observations. A key renewed from TTL 1 to TTL 2 at tick 0 must survive tick 1. The mutant's stale bucket entry can remove the renewed key.

## A1. Banded alignment with affine gaps and ties

The input is `[n,m,band,open,extend,mismatch] ++ left ++ right`. Sequence lengths and band lie in [0,12]. Symbols lie in [0,4], with 4 matching every symbol. Open lies in [1,10], extend in [0,open] and mismatch in [0,10]. The dynamic program visits prefix pairs `(i,j)` within `|i-j| ≤ band`. A diagonal step costs zero for a match and otherwise mismatch plus one when the left symbol is smaller. A gap of length k costs `open + (k-1)*extend`. Gap candidates may start at any reachable predecessor in the same row or column.

The reference enumerates the gap candidates. The alternate carries one running minimum per column and one for the current row. Each is reset when its cell is blocked by the band. The result `[score,mask]` uses -1/0 for unreachable and 0/0 for two empty sequences. Otherwise the bits 1, 2 and 4 denote all tied cheapest terminal move classes (diagonal, vertical gap and horizontal gap). For left [0], right [1], band 1, open 1, extend 0 and mismatch 1, the minimum is 2 and all three bits apply. Keeping the score alone would miss the mutant.

## A2. Fixed-point rational resampling

The input is `[n,count,step,den,phase,lo,hi] ++ samples`. Source length is 1–16, output count 0–32, step -24–24, positive denominator 1–16, phase -64–128, and signed samples and clipping bounds -512–512 with lo ≤ hi.

At output index i, the coordinate numerator is `phase + i*step`. Divide by den into floor index and nonnegative remainder. Interpolate between adjacent source values using integer weights, then round nearest with exact halves away from zero. Coordinates strictly outside the source interval use the nearest endpoint. Clip the rounded result to [lo,hi]. Emit `[value,edge,saturation]` per output. Edge and saturation use -1 for lower-side clipping, +1 for upper-side clipping and 0 otherwise. Exact endpoint coordinates have edge 0. The incremental version carries the unclipped index and remainder across steps. Samples [-1,0] at phase 1/2 expose the signed-half mutant.

## Sources and evidence

[fixtures.json](fixtures.json) records a Ninja dependency scenario, a Bash nested lookup example, a Redis renewal scenario and the first sixteen monthly observations of R's AirPassengers dataset. The first three map source operations to the bounded SpecLessBench interfaces. The resampling source supplies sample values and the benchmark supplies the fixed-point rules. Alignment is a classical-algorithm derivative with synthetic sequence tests. The generator counts source-derived inputs separately and the reports bind the fixture snapshot by SHA-256.

The exact target names replace each ID's hyphens with underscores and append `_equivalence` or `_refutationAt`. See `lean/SystemsGoals.lean`, `rocq/SystemsGoals.v` and `compcert/*Goals.v`. `call-graphs.json` binds direct-call reachability to the 15 actual ASTs. `evidence/` records exhaustive small cases, seeded random attempts, structured boundary cases, observed events and distinguishing inputs. C evaluations use sanitizers. Clight evidence consists of AST export and target type checking.
