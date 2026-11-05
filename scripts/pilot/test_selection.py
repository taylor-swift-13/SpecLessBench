"""Ensure every factorial context is excluded on all three platforms."""
from release_gate import score
from selection import selection

eligible,reference=selection()
assert len(eligible)==69 and len(reference)==2
assert {x['split_family'] for x in eligible}.isdisjoint({x['split_family'] for x in reference})
for context in reference:
    for platform in ('lean','rocq','compcert'):
        assert score(context['pilot_id'],platform,'unused-proof')['status']=='reference-only'
print('All six factorial platform instances are reference-only; 69 contexts remain eligible.')
