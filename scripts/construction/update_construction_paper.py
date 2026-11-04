"""Write the observed construction procedure and new tranche into the paper."""
import hashlib
import json
from algorithms_common import ROOT
from accounting import AUDIT,append,now


def main():
    path=ROOT/"paper/main.tex"; old=path.read_text(); text=old
    replacements={
        "Four groups currently supply twelve contexts, or 36 platform instances":"Ten groups currently supply 24 contexts, or 72 platform instances",
        "Four groups currently supply twelve contexts and 36 platform instances":"Ten groups currently supply 24 contexts and 72 platform instances",
        "Four groups currently supply twelve concrete contexts and 36 platform instances":"Ten groups currently supply 24 concrete contexts and 72 platform instances",
        "Four groups have concrete native/C sources, actual Clight ASTs and type-checked unproved targets":"Ten groups have concrete native/C sources, 34 actual Clight ASTs and type-checked unproved targets",
        "The earlier C-only check executed 660 inputs":"The earlier C-only check executed 660 inputs",
    }
    for a,b in replacements.items():
        assert a in text,a
        text=text.replace(a,b)
    anchor=r"\subsection{Program Sources and Provenance}"
    new=r"""\subsection{Base-Algorithm Expansion}

Six additional groups materialize factorial, reversal, summation, matrix multiplication, first-match search, and queue traces. Each has a reference, one replacement, and one retained mutant, producing twelve contexts and 36 platform instances. Native differences include direct/accumulator recursion, cellwise/shared-dimension matrix accumulation, naive/KMP matching, and single-/two-list queues. C versions use bounded arrays and explicit calls; native call structure need not mirror C pointers or loops. Related future matrix/reversal contexts share their split groups.

The new tranche executed 66,358 distinct inputs, yielding 597,222 behavior evaluations across three variants and three executable platforms. It separately performed 132,774 Lean/Rocq input-domain evaluations, including deliberately invalid boundary records. No unintended positive, cross-language, or domain disagreement was observed, and every retained mutant had distinguishing inputs. Factorial exhausts its entire thirteen-value input domain; the other groups combine explicit small-domain enumeration with 5,000 random generation attempts and boundary/witness inputs. Duplicate inputs are removed and not recounted as novel coverage. These checks do not prove the final targets or execute Clight semantics.

The cumulative record has 96,640 tested input records, 96,483 distinct group-specific inputs, and 960,606 behavior evaluations over ten groups. The difference comes from 157 repeated records in the earlier QCIP tranche, identified by a retrospective corpus audit without rewriting its original reports. Neither platform executions nor repeated records count as independent benchmark contexts.

"""
    assert text.count(anchor)==1
    text=text.replace(anchor,new+anchor)
    anchor=r"\subsection{Quality Control}"
    method=r"""\subsection{Construction Method}
\label{sec:construction}

The unit is a versioned implementation group, not an isolated program pair. Construction selects an implementation-style contrast, fixes the input and observation boundary, and supplies concrete Lean, Rocq and C versions of each variant. No independently authored correct-output function is used. Constructor permissions end when a revision freezes; proof agents thereafter edit proofs only.

\begin{enumerate}
\item \textbf{Materialize the boundary and code.} Record provenance, source adaptations and all reachable callees. Define input layouts, safe numerical ranges and executable observation projections. Keep representation differences visible in metadata rather than assuming identical layouts or call graphs across platforms.
\item \textbf{Check definitions and obligations.} Type-check native code and target propositions, export real normalized Clight ASTs, and type-check their bindings and execution targets. Pending proofs are explicit; undefined program parameters, admitted certificates and equality of failed executions cannot fill gaps.
\item \textbf{Generate and audit inputs.} Combine retained witnesses, boundaries, stated exhaustive subdomains and seeded, structurally biased random generation. The new tranche deduplicates inputs and cross-checks executable Lean/Rocq domain predicates against the generator, including invalid neighboring inputs. Random attempts and unique accepted inputs are reported separately.
\item \textbf{Compare within and across platforms.} Compare intended-positive variants and each variant's ports using a common observation encoding. The C harness also checks normal return and zero output padding. C native sanitizer runs are distinguished from Clight semantic execution. Domain mismatch, failed execution, unintended pair difference and port disagreement are separate issue classes.
\item \textbf{Repair or retain, then freeze.} Persist the original input and observations before changing a program, decoder, boundary or task. A constructor may repair a defect or retain a meaningful non-equivalence context. Domain restrictions cannot silently discard counterexamples. Save before/after hashes, affected contexts and revision IDs, rerun affected checks, and freeze code, targets, ASTs and evidence fingerprints together.
\end{enumerate}

The constructor stops the selected tranche when concrete versions and target types check, testing reaches its predeclared coverage, retained negatives have distinguishing inputs, and discovered unintended differences are resolved or explicitly reclassified. Final theorem proofs are not required at this stage. A shortest observed witness is not claimed globally minimal. Absence of a differential counterexample yields only a provisional equivalence label. Appendix~\ref{app:construction} gives the exact domains and repair example.

"""
    assert text.count(anchor)==1
    text=text.replace(anchor,method+anchor)
    appendix=r"""
\section{Construction Details and Evidence}
\label{app:construction}

The six algorithm groups refine existing catalog slots rather than introducing extra pairwise samples. Each selects reference/replacement and reference/mutant contexts, realized on all three platforms. Their named goals are \texttt{R\_FAC\_EQ/CEX}, \texttt{R\_REV\_EQ/CEX}, \texttt{R\_SUM\_EQ/CEX}, \texttt{R\_MAT\_EQ/CEX}, \texttt{R\_STR\_EQ/CEX}, and \texttt{R\_QUE\_EQ/CEX}; expected polarity remains curator-only.

\begin{table*}[t]
\centering\small
\caption{Deduplicated construction coverage for the base-algorithm tranche. Domain evaluations are counted separately from behavior evaluations. No row denotes a proved final theorem.}
\begin{tabular}{lrrrr}
\toprule
Group & Unique inputs & Behavior evaluations & Domain evaluations & Distinguishing inputs \\
\midrule
Factorial & 13 & 117 & 34 & 12 \\
Reversal & 8,204 & 73,836 & 16,418 & 8,204 \\
Summation & 8,213 & 73,917 & 16,436 & 7,118 \\
Matrix product & 12,746 & 114,714 & 25,502 & 6,939 \\
First-match search & 12,869 & 115,821 & 25,748 & 346 \\
Queue traces & 24,313 & 218,817 & 48,636 & 7,790 \\
\midrule
Total & 66,358 & 597,222 & 132,774 & 30,409 \\
\bottomrule
\end{tabular}
\end{table*}

Factorial admits integers0--12 to avoid signed32-bit overflow. Sequences have length0--64 and values in $[-10^6,10^6]$. Matrix dimensions range0--6 and entries lie in $[-1000,1000]$, including empty dimensions and a zero inner dimension with nonempty output. Texts have length at most64, patterns at most32, and bytes0--255. Queue traces have at most64 commands over enqueue, dequeue and peek, with empty queries allowed. Exact lengths and command encodings are checked by executable input predicates, not by separate functional postconditions.

Small-domain enumeration covers ternary sequences of length at most7; ternary matrices with dimensions at most2; binary texts of length at most7 and patterns of length at most4; and traces of length at most6 over three enqueue values, dequeue and peek. Every non-factorial group additionally receives5,000 random attempts with fixed seeds, plus boundary and witness inputs. Deduplication explains why random attempt counts differ from novel input counts. The factorial group performs no random sampling after exhausting its admitted value inputs.

The retained matrix mutant reads the right operand using $j\cdot k+t$ instead of $t\cdot c+j$. Both accesses stay within the admitted buffer. For $A=[1,2]$ and $B=[1,2;3,4]$, observed results are $[7,10]$ and $[5,11]$. The KMP mutant resets its matched-prefix length to0 at every mismatch; text $[0,0,0,1]$ with pattern $[0,0,1]$ distinguishes a first match at1 from failure. The queue mutant keeps the rear list after normalization; enqueue1, dequeue, dequeue distinguishes an empty result from a repeated1. These are execution witnesses, not formal counterexample certificates.

One new Lean draft used reserved identifiers \texttt{matches} and \texttt{prefix}; type-checking rejected them before testing. The repair renamed them, archived the prior source, incremented the revision, and retained the failed command's cost. This is a construction error, not a discovered algorithmic counterexample. The earlier Clight global-environment error is likewise recorded separately from retained semantic mutants. No unintended algorithmic or cross-platform mismatch was observed in the completed tests, so we report none rather than inventing a repair example.

Native input sequences are passed directly to the Lean/Rocq entry; the C harness pads the same fields into its fixed input global. The native observation is a length-prefixed integer list; C requires normal return and initialized output padding, then projects the corresponding length and payload. All case generators, corpus hashes, source/AST fingerprints, invalid-domain cases, failed commands and cost scopes are retained in the repository. Final proof obligations remain unproved, and portable dependency locking and isolated solver packaging remain pending.

"""
    assert text.count(r"\end{document}")==1
    text=text.replace(r"\end{document}",appendix+r"\end{document}")
    path.write_text(text)
    append(AUDIT/"events.jsonl",{"schema_version":1,"timestamp_utc":now(),"kind":"construction-method-paper-update",
        "batch_id":"algorithms-v0.3","before_sha256":hashlib.sha256(old.encode()).hexdigest(),
        "after_sha256":hashlib.sha256(text.encode()).hexdigest(),"new_groups":6,"new_contexts":12,
        "method_source":"docs/construction-method.md","evidence_source":"benchmarks/construction/summary-algorithms-v0.3.json"})
    print("Paper updated: observed construction method, six-group expansion, evidence taxonomy and detailed appendix.")

if __name__=="__main__": main()
