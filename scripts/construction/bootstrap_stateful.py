"""Reuse audited construction scaffolding, keeping program groups independent."""
from accounting import ROOT
from stateful_common import CORE
def main():
    folder=ROOT/'scripts/construction'
    names=['prepare_boundaries','build_boundaries','differential_boundaries','run_boundaries','prepare_boundary_targets','check_boundary_contract','summarize_boundaries']
    destinations=[folder/(name.replace('boundaries','stateful').replace('boundary','stateful')+'.py')for name in names]
    if any(p.exists()for p in destinations):
        raise SystemExit('One-shot scaffold refuses to overwrite existing versioned tools; use audited revisions instead.')
    for name in names:
        src=(folder/(name+'.py')).read_text()
        text=src.replace('boundaries','stateful').replace('Boundary','Stateful').replace('boundary','stateful').replace('v0.4','v0.5')
        text=text.replace('("Structures.h" if i<4 else "Formats.h")','"Stateful.h"')
        text=text.replace('Eight implementation groups','Three implementation groups').replace('8 groups, 16 contexts, 48','3 groups, 6 contexts, 18')
        text=text.replace('24 actual Clight ASTs','9 actual Clight ASTs').replace('40 contexts','46 contexts')
        text=text.replace("len(reg['groups'])==8 and len(meta['exports'])==24","len(reg['groups'])==3 and len(meta['exports'])==9")
        text=text.replace("len(interface['contexts'])==40","len(interface['contexts'])==46")
        text=text.replace("'implementation_groups':8,'semantic_contexts':16","'implementation_groups':3,'semantic_contexts':6")
        text=text.replace("'platform_instances':48,'clight_ast_count':24","'platform_instances':18,'clight_ast_count':9")
        text=text.replace("'tooling_revision':'tooling-v0.5.2'","'tooling_revision':'tooling-v0.5.0'")
        if name=='check_boundary_contract':
            text=text.replace("if 'batches'in prior:prior=prior['batches'][0]", "prior_batches=prior.get('batches',[prior]); prior_batches=[b for b in prior_batches if b.get('tranche')!='stateful']")
            text=text.replace("counts.update(final_target_proofs_attempted=False", "counts.update(tranche='stateful',final_target_proofs_attempted=False")
            text=text.replace("prior[k]+counts[k]", "sum(b[k]for b in prior_batches)+counts[k]")
            text=text.replace("batches=[prior,counts]", "batches=prior_batches+[counts]")
        if name=='summarize_boundaries':
            start=text.index('    issues=[json.loads(s)')
            end=text.index('    print(json.dumps',start)
            text=text[:start]+text[end:]
            text=text.replace("attribution_correction='benchmarks/construction/attribution-corrections.jsonl',", "")
        dest=name.replace('boundaries','stateful').replace('boundary','stateful')
        (folder/(dest+'.py')).write_text(text,encoding='utf-8',newline='\n')
    print('Prepared independent stateful construction tools; no program proof.')
if __name__=='__main__':main()
