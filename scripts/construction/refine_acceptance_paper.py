"""Document the actual proof-interface audit and its explicit-branch repair."""
import hashlib
from algorithms_common import ROOT
from accounting import AUDIT,append,now


def main():
    path=ROOT/"paper/main.tex"; old=path.read_text(); text=old
    paragraphs={
        "The benchmark goal is the fixed disjunction":r"""The accepted result is structured: either a literal equivalence claim with a proof of $\mathit{Eq}(P_A,P_B)$, or a literal counterexample claim supplying concrete input and observations with a proof specialized to those values. Both branch goals are visible; expected polarity is hidden. We do not accept a bare proof of $\mathit{Eq}\lor\mathit{Cex}$: for total functions, classical reasoning can prove that logical dichotomy without selecting an explicit behavioral conclusion or constructing an input. Provisional labels and test witnesses aid construction, but truth depends on the frozen programs and boundary. Final reference proofs remain optional during this construction stage.""",
        "Each concrete group has three intended-equivalent":r"""Each initial QCIP group has three intended-equivalent implementations and one near-miss per platform. We select two intended-equivalence contexts and one refutation context, giving eight and four expected contexts, respectively. The solver sees both explicit branch targets and must commit to one, with concrete data for refutation. Those 36 platform instances refine existing slots without increasing the54-context plan. Labels remain provisional; Appendix~\ref{app:targets} names this tranche's obligations.""",
        "For each task, $s_t=1$ only if":r"""For each task, $s_t=1$ only if the proof is accepted against the explicitly selected branch and, for refutation, the protected obligation specialized to the submitted literal input and observations; otherwise $s_t=0$. A proof of the bare logical disjunction is insufficient. Report overall certificate success and distinguish certified from provisional polarity labels. Also report task- and family-weighted scores:""",
    }
    lines=text.splitlines()
    for prefix,new in paragraphs.items():
        indexes=[i for i,s in enumerate(lines) if s.startswith(prefix)]; assert len(indexes)==1,prefix
        lines[indexes[0]]=new
    text="\n".join(lines)+"\n"
    anchor=r"\subsection{Construction Cost and Audit Trail}"
    section=r"""\subsection{Auditing the Certificate Interface}

Construction includes checking whether the goal can be discharged without the intended evidence. Our interface audit found that a bare proposition $\mathit{Eq}\lor\mathit{Cex}$ is too weak as a submission protocol. For total functions, classical logic yields either universal equality or an existential difference independently of understanding the programs. This is a valid logical proof, but it does not necessarily select a checked behavioral answer or produce a concrete counterexample. The issue is the task interface, not unsoundness of classical logic, which remains allowed within genuine branch proofs.

The revised contract requires a literal branch tag. Equivalence submissions must directly inhabit the fixed universal target. Refutations supply finite JSON data for input and both observations; a protected serializer produces the corresponding Lean/Rocq values and a goal asserting admissibility, two successful observations and their inequality at that input. A generated gate requires the submitted theorem to have this branch-specific type. Opaque witness programs and conditional tags cannot substitute for the literal data. This audit changed no implementation or input domain, so prior differential evidence remains applicable.

For all24 contexts, both branch target types were checked on all three platforms. We additionally checked18 generated literal-witness obligations and rejected90 malformed submission packages, including bare-disjunction claims, nonliteral witnesses and identical observations. These are interface checks, not final theorem proofs. The renderer and gate scaffold do not yet constitute an isolated grader with a completed dependency/axiom audit.

"""
    assert text.count(anchor)==1; text=text.replace(anchor,section+anchor)
    text=text.replace("The solver always receives a disjunction.","The solver chooses an explicit checked branch.")
    text=text.replace("Each agent-facing target remains the disjunction of equivalence and refutation, with polarity hidden.",
        "Each agent-facing context exposes both explicit branch targets; refutation requires literal witness data and a specialized proof, with polarity hidden.")
    replacements={"integers0--12":"integers 0--12","signed32-bit":"signed 32-bit","length0--64":"length 0--64",
        "range0--6":"range 0--6","most64":"most 64","most32":"most 32","bytes0--255":"bytes 0--255",
        "most7":"most 7","most2":"most 2","most4":"most 4","most6":"most 6","receives5,000":"receives 5,000",
        "to0 at":"to 0 at","at1 from":"at 1 from","enqueue1,":"enqueue 1,","repeated1.":"repeated 1.",
        "all24 contexts":"all 24 contexts","checked18 generated":"checked 18 generated","rejected90 malformed":"rejected 90 malformed",
        "the54-context":"the 54-context"}
    for a,b in replacements.items(): text=text.replace(a,b)
    path.write_text(text)
    append(AUDIT/"events.jsonl",{"schema_version":1,"timestamp_utc":now(),"batch_id":"algorithms-v0.3",
        "kind":"certificate-interface-method-revision","before_sha256":hashlib.sha256(old.encode()).hexdigest(),
        "after_sha256":hashlib.sha256(text.encode()).hexdigest(),"issue":"PROP-DISJUNCTION-ESCAPE",
        "programs_changed":False,"final_target_proofs_attempted":False})
    print("Paper revised: explicit branch evidence, literal refutation data, and certificate-interface audit.")

if __name__=="__main__": main()
