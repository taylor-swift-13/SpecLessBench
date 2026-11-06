"""Reviewed baseline evaluation instructions."""
import hashlib
import json

REVISION = '2026-11-06'
VARIANTS = ('baseline',)

TASK = '''Determine whether the two fixed implementations have the same observable
behavior and submit a machine-checkable proof. Read the task in the read-only
/task directory and work in /work.

The task defines the input domain, observations and target propositions. Choose
one conclusion: prove equivalence on every valid input, or provide a concrete
valid input and prove that the two observations differ.

Write /work/claim.json as exactly one of:
{"claim":"equivalence"}
{"claim":"counterexample","input":[...],"left":[...],"right":[...]}
Counterexample fields must be literal integer lists following the platform
interface below. Write the proof in the specified Submission file and provide
the complete solve theorem with the selected target type. Auxiliary definitions
and lemmas are allowed; the proof method is unrestricted.

Do not change implementations, validity conditions, observation semantics or
targets. Do not use unproved placeholders or introduce axioms. Tests may help
find counterexamples, but the submitted conclusion requires a formal proof.
The independent grader checks the submitted files, exact target and axiom
dependencies. Success requires all checks to pass.
'''

INTERFACES = {
    'lean': '''Lean interface
Read /task/Task.lean. Submit /work/Submission.lean importing Task and defining
Submission.solve : Task.equivalent, or
Submission.solve : Task.refutationAt <input> <left> <right>.
For a counterexample, left/right are the complete Words inside some, including
the leading payload length.
Local compilation: LEAN_PATH=/task:/work lean /work/Submission.lean
No sorry or candidate-defined axioms. The grader permits Lean's standard
propext, Classical.choice and Quot.sound dependencies.
''',
    'rocq': '''Rocq interface
Read /task/Task.v. Submit /work/Submission.v, importing:
From Coq Require Import ZArith List.
From Trusted Require Import Task.
Import ListNotations.
Define the TOP-LEVEL theorem solve : Task.equivalent, or
solve : Task.refutationAt <input> <left> <right>.
Do not wrap the theorem in Module Submission. For a counterexample, left/right
are the complete Words inside Some, including the leading payload length.
Local compilation: coqc -Q /task Trusted -Q /work Candidate /work/Submission.v
No Admitted, admit or candidate-defined axioms. The final proof also undergoes
independent coqchk checking and an axiom audit; native Rocq requires no axioms.
''',
    'compcert': '''CompCert / Clight interface
C sources: /task/Left.c and /task/Right.c. Authoritative Clight ASTs: Left.v and
Right.v. Task.v and Execution.v define the targets and execution semantics.
Submit /work/Submission.v, importing:
From Stdlib Require Import ZArith List.
From Trusted Require Import Task Execution Left Right.
Import ListNotations.
Define the TOP-LEVEL theorem solve; do not wrap it in Module Submission.
The equivalence target is Task.equivalent, including the required safe,
terminating Clight executions and exact observations.
For a counterexample, input is unpadded. The claim's left/right lists contain
the length slot and meaningful payload. The grader pads each with zeros to 8192
words and pairs it with main return 0. The proof target is:
Task.refutationAt <input>
  (0%Z, <left> ++ repeat 0%Z <8192-left_length>)
  (0%Z, <right> ++ repeat 0%Z <8192-right_length>)
Use literal lists and actual padding lengths. The complete output buffer is part
of the fixed observation. Functional models are allowed if their correspondence
to the original Clight semantics is proved.
Local compilation: coqc -Q /task Trusted -Q /work Candidate /work/Submission.v
No Admitted, admit or candidate-defined axioms. CompCert standard dependencies
on the grader's allowlist are permitted, with independent checking and audit.
''',
}

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def build_prompt(platform, variant, budget):
    if variant not in VARIANTS:
        raise ValueError('Unknown prompt variant')
    interface = INTERFACES[platform]
    runtime = (f'Runtime: shared wall budget {budget} seconds including agent work and grading. '
               'The external controller enforces this budget.\n')
    components = {'task': TASK, 'interface': interface, 'runtime': runtime,
                  'execution_guidance': None}
    prompt = '\n'.join(x for k, x in components.items() if x)
    metadata = {'revision': REVISION, 'variant': variant, 'language': 'en',
                'delivery': 'prompt sections',
                'component_sha256': {k: digest(v) if v is not None else None
                                     for k, v in components.items()},
                'initial_prompt_sha256': digest(prompt)}
    return prompt, metadata, components

