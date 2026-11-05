"""Exercise single-run reports and real-goal bypass rejection with a fake agent."""
import json
import tempfile
from pathlib import Path

from run_evaluation import BUILD, run


def main():
    meta=json.loads((BUILD/'registry.json').read_text())
    with tempfile.TemporaryDirectory(prefix='specless-report-test-') as temp:
        root=Path(temp);config=root/'config.json'
        for label,body in [('sorry','theorem solve : Obligation.goal := by sorry'),
                           ('axiom','axiom bad : Obligation.goal\ntheorem solve : Obligation.goal := bad'),
                           ('wrong-goal','theorem solve : True := True.intro')]:
            source='import Obligation\nnamespace Submission\n'+body+'\nend Submission\n'
            code=('import json; from pathlib import Path; '
                  'assert not Path("/mnt/c").exists(); '
                  'print(json.dumps({"type":"message","content":"test conversation"})); '
                  'print(json.dumps({"type":"tool_call","name":"test","arguments":{}})); '
                  'print(json.dumps({"type":"tool_result","output":"ok"})); '
                  'print(json.dumps({"type":"usage","scope":"run_total","input_tokens":12,"cached_input_tokens":10,"output_tokens":3})); '
                  'print(json.dumps({"type":"session_end","transcript_complete":True})); '
                  'Path("/work/Submission.lean").write_text('+repr(source)+')')
            config.write_text(json.dumps({'agent':{'name':'fake-offline-agent','model_name':'fake','command':['/usr/bin/python3','-c',code,'{prompt}']},'limits':{'wall_seconds':90},'pricing':{'input_usd_per_million':1,'cached_input_usd_per_million':0.1,'output_usd_per_million':2,'version':'synthetic'}}))
            path,report=run(meta['pilot_id'],'lean','equivalence',config,root/'runs',purpose='reference')
            assert report['result']['status']=='rejected',(label,report['result'])
            assert report['transcript']['agent_reported_complete'] is True
            assert report['transcript']['completeness_independently_verified'] is False
            assert report['resources']['token_totals']['input_tokens']==12 and len(report['resources']['usage_events'])==1
            assert report['resources']['monetary_cost']['estimated_usd']=='0.000009'
            if label in ('sorry','axiom'):
                assert report['checks']['fixed_goal_gate']=='passed'
                assert report['checks']['axiom_audit']['status']=='failed'
                assert ('sorryAx' if label=='sorry' else 'bad') in report['checks']['axiom_audit']['auditor_output']
            else:assert report['checks']['fixed_goal_gate']=='not_passed_or_not_run'
            events=[json.loads(line) for line in (path/'events.jsonl').read_text().splitlines()]
            assert {x.get('event',{}).get('type') for x in events}>={'message','tool_call','tool_result','usage','session_end'}
            assert all((path/name).is_file() for name in ('report.json','report.md','config.json','prompt.txt','events.jsonl','Submission.lean','checker.log','resources.json','agent.stdout','agent.stderr'))
            assert json.loads((path/'checker.log').read_text()),'checker trace missing'
            print(label,'rejected; report and trace recorded',flush=True)
        code=('import json,time; print(json.dumps({"type":"message","content":"before timeout"}),flush=True); time.sleep(10)')
        config.write_text(json.dumps({'agent':{'name':'timeout-agent','command':['/usr/bin/python3','-c',code]},'limits':{'wall_seconds':1}}))
        path,report=run(meta['pilot_id'],'lean','equivalence',config,root/'runs',purpose='reference')
        assert report['result']['status']=='timeout',report['result']
        assert b'before timeout' in (path/'agent.stdout').read_bytes()
        assert report['transcript']['agent_reported_complete'] is False
        print('timeout recorded with partial transcript',flush=True)
        code=('import json; print(json.dumps({"type":"message","content":"x"*1100000}),flush=True)')
        config.write_text(json.dumps({'agent':{'name':'large-output-agent','command':['/usr/bin/python3','-c',code]},'limits':{'wall_seconds':30}}))
        path,report=run(meta['pilot_id'],'lean','equivalence',config,root/'runs',purpose='reference')
        assert (path/'agent.stdout').stat().st_size>1000000
        assert report['transcript']['output_truncated'] is False
        assert report['result']['status']=='rejected'
        print('more than one megabyte of output preserved',flush=True)
        config.write_text(json.dumps({'agent':{'name':'failing-agent','command':['/usr/bin/python3','-c','raise SystemExit(9)']}}))
        _,report=run(meta['pilot_id'],'lean','equivalence',config,root/'runs',purpose='reference')
        assert report['result']['status']=='agent-error' and report['result']['exit_code']==9
        print('agent process failure distinguished from a rejected proof',flush=True)
        try:run(meta['pilot_id'],'lean','counterexample',config,root/'runs',purpose='reference')
        except ValueError:pass
        else:raise AssertionError('unprepared theorem accepted')
    print('Only fake-agent bypasses were submitted; no benchmark theorem proved.')


if __name__=='__main__':main()
