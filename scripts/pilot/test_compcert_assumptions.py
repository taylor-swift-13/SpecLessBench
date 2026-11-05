"""Check the explicit CompCert assumption policy and reject spoofed output."""
from rocq_grader_core import allowed_assumptions

closed = 'Closed under the global context\n'
trusted = ('Axioms:\nAxioms.proof_irr : ClassicalFacts.proof_irrelevance\n'
           'Events.external_functions_sem :\n  String.string -> AST.signature -> Events.extcall_sem\n')
assert allowed_assumptions('rocq', closed)
assert allowed_assumptions('compcert', closed)
assert allowed_assumptions('compcert', trusted)
assert not allowed_assumptions('rocq', trusted)
assert not allowed_assumptions('compcert', trusted + 'Submission.cheat : False\n')
assert not allowed_assumptions('compcert', trusted + 'Axioms.proof_irr : False\n')
assert not allowed_assumptions('compcert', 'noise\n' + trusted)
assert not allowed_assumptions('compcert', 'Axioms:\n  Submission.cheat : False\n')
assert not allowed_assumptions('compcert', 'Axioms:\n')
print('CompCert standard assumptions accepted; unknown, duplicate and spoofed assumptions rejected')
