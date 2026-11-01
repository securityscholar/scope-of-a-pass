"""Reconstruct every W2 outcome from saved packets and decisions; no model calls."""
from pathlib import Path
import argparse,csv,json,hashlib,collections,sys
from model_client import read,save,PREFIX
from workflow import *
from run_experiment import check_frozen
sys.path.insert(0,str(ROOT/'core'))
from proofs import verify

CONTRASTS=[('delegated_full','single_shared'),('delegated_selected','delegated_full'),('delegated_drop_general','delegated_selected'),('delegated_drop_scoped','delegated_drop_general'),('delegated_drop_scoped','delegated_drop_reminder')]
def write_csv(path,rows):
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def analyze(root,out):
    root=Path(root).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);protocol=check_frozen(root);cases=read(root/'data/cases.json')
    for case in cases:assert verify(case['task'],case['private_world'],case['source_key'])['verified']
    rows=[];upstream=[];callrows=[]
    for model in protocol['models']:
        assert (root/'runs'/model/'completion.json').exists(),'Model run is incomplete: '+model
        for case in cases:
            case_id=case['case_id'];base=root/'runs'/model/case_id;stage=read(base/'upstream.json');analysis=stage['analyst'];selected=analysis.get('handoff_record_ids',[]) if isinstance(analysis,dict) else []
            invalid_selection=not isinstance(selected,list) or len(selected)>2 or any(s not in case['records'] for s in selected)
            for kind,builtkey,reviewkey in [('delegated','delegated_artifact','delegated_review'),('single','single_artifact','single_review')]:
                built=stage[builtkey];reconstructed=make_artifact(case,analysis,read(base/'analyst_execution.json'),stage[reviewkey]);assert reconstructed==built,'Artifact reconstruction differs'
                upstream.append(dict(model=model,case_id=case_id,family=case['family'],checker_context=kind,arithmetic_pass=built['arithmetic_pass'],code_revised=built['code_revised'],receipt_status=built['receipt']['status'],natural_design_selected=case['design_record_id'] in selected,invalid_record_selection=invalid_selection,analyst_program_ok=read(base/'analyst_execution.json').get('ok',False),analyst_proposed_type=analysis.get('proposed_answer_type') if isinstance(analysis,dict) else None,source_answer_type=case['source_key']['answer']['answer_type']))
            for route in ROUTES:
                directory=base/route;episode=read(directory/'episode.json');packet=read(directory/'initial_packet.json');lastpacket=read(directory/'final_packet.json') if episode['archive_requested'] else packet
                assert packet==route_packet(case,analysis,stage['single_artifact'] if route=='single_shared' else stage['delegated_artifact'],route,stage['single_review'])
                if episode['archive_requested']:assert lastpacket==retrieve(case,packet)
                initialrec=read(directory/'initial/record.json');finalrec=read(directory/'after_retrieval/record.json') if episode['archive_requested'] else initialrec
                initialreq=read(directory/'initial/request.json');assert initialreq['prompt']==PREFIX+decision_prompt(packet,route)
                if episode['archive_requested']:assert read(directory/'after_retrieval/request.json')['prompt']==PREFIX+decision_prompt(lastpacket,route,True)
                first=episode['initial_decision'];last=episode['final_decision'];before=score(case,packet,first,case['source_key']);after=score(case,lastpacket,last,case['source_key'])
                source_recs=[read(base/'analyst/record.json'),read(base/('checker_single' if route=='single_shared' else 'checker_delegated')/'record.json')]
                violation=episode['tool_violation'] or any(r.get('tool_violation') for r in source_recs)
                if violation:after['scientifically_supported']=False;after['source_task_completed']=False
                inconsistent_request=isinstance(first,dict) and first.get('action')=='request_design_record' and (first.get('answer_type')!='pending' or first.get('value') is not None)
                upstream_time=sum(r['elapsed_seconds'] for r in source_recs)
                row=dict(model=model,case_id=case_id,family=case['family'],route=route,source_answer_type=case['source_key']['answer']['answer_type'],source_value=case['source_key']['answer']['value'],initial_has_design=episode['initial_has_design'],archive_requested=episode['archive_requested'],initial_action=first.get('action') if isinstance(first,dict) else None,initial_answer_type=first.get('answer_type') if isinstance(first,dict) else None,initial_value=first.get('value') if isinstance(first,dict) else None,initial_unsupported_causal=before['unsupported_causal_claim'],initial_safe_incomplete=before['safe_but_incomplete'],inconsistent_request=inconsistent_request,final_has_design=episode['final_has_design'],final_action=last.get('action') if isinstance(last,dict) else None,final_answer_type=last.get('answer_type') if isinstance(last,dict) else None,final_value=last.get('value') if isinstance(last,dict) else None,final_parsed=after['parsed_final'],final_supported=after['scientifically_supported'],source_completed=after['source_task_completed'],final_unsupported_causal=after['unsupported_causal_claim'],final_numerical_error=after['numerical_error'],final_safe_incomplete=after['safe_but_incomplete'],invented_evidence_reference=after.get('invented_evidence_reference',False),tool_violation=violation,issues=';'.join(after['issues']),branch_model_calls=4 if episode['archive_requested'] else 3,branch_recorded_seconds=round(upstream_time+initialrec['elapsed_seconds']+(finalrec['elapsed_seconds'] if episode['archive_requested'] else 0),3))
                rows.append(row)
    summary=[]
    for model in protocol['models']:
        for route in ROUTES:
            rs=[r for r in rows if r['model']==model and r['route']==route]
            summary.append(dict(model=model,route=route,n=len(rs),design_initially_received=sum(r['initial_has_design'] for r in rs),archive_requests=sum(r['archive_requested'] for r in rs),initial_unsupported_causal=sum(r['initial_unsupported_causal'] for r in rs),final_supported=sum(r['final_supported'] for r in rs),source_completed=sum(r['source_completed'] for r in rs),final_unsupported_causal=sum(r['final_unsupported_causal'] for r in rs),final_safe_incomplete=sum(r['final_safe_incomplete'] for r in rs),numerical_errors=sum(r['final_numerical_error'] for r in rs),unreceived_evidence_references=sum(r['invented_evidence_reference'] for r in rs),invalid_final_decisions=sum(not r['final_parsed'] for r in rs),tool_violations=sum(r['tool_violation'] for r in rs),source_answerable=sum(r['source_answer_type']!='not_identified' for r in rs),answerable_completed=sum(r['source_completed'] for r in rs if r['source_answer_type']!='not_identified'),logical_branch_calls=sum(r['branch_model_calls'] for r in rs)))
    contrasts=[]
    for model in protocol['models']:
        for left,right in CONTRASTS:
            for outcome in ('source_completed','final_supported','archive_requested','final_unsupported_causal'):
                pairs=[(next(r for r in rows if r['model']==model and r['case_id']==c['case_id'] and r['route']==left)[outcome],next(r for r in rows if r['model']==model and r['case_id']==c['case_id'] and r['route']==right)[outcome]) for c in cases]
                contrasts.append(dict(model=model,left=left,right=right,outcome=outcome,matched_tasks=len(pairs),left_only=sum(a and not b for a,b in pairs),right_only=sum(b and not a for a,b in pairs),both=sum(a and b for a,b in pairs),neither=sum(not a and not b for a,b in pairs),difference_in_counts=sum(a-b for a,b in pairs)))
    itemtypes=collections.Counter()
    for model in protocol['models']:
        for case in cases:
            for path in sorted((root/'runs'/model/case['case_id']).rglob('record.json')):
                rec=read(path);tokens=collections.Counter()
                for a in rec['attempts']:
                    for u in a.get('usage',[]):tokens.update({k:v for k,v in u.items() if isinstance(v,(float,int))})
                    for line in (path.parent/f"events_{a['attempt']}.jsonl").read_text(encoding='utf-8').splitlines() if (path.parent/f"events_{a['attempt']}.jsonl").exists() else []:
                        try:
                            e=json.loads(line)
                            if e.get('type')=='item.completed':itemtypes[e.get('item',{}).get('type','unknown')]+=1
                        except ValueError:pass
                callrows.append(dict(model=model,logical_id=rec['logical_id'],attempts=len(rec['attempts']),parsed=rec['answer'] is not None,tool_violation=rec['tool_violation'],elapsed_seconds=rec['elapsed_seconds'],**{k:tokens.get(k,0) for k in ('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens')}))
    result=dict(protocol='GuardLab-actual-workflow-W2',completed_episodes=len(rows),source_analyses=24,source_tasks=12,mathematical_structures=4,models=protocol['models'],summary=summary,physical_model_calls=len(callrows),physical_attempts=sum(r['attempts'] for r in callrows),physical_transport_or_parse_failures=sum(not r['parsed'] for r in callrows),native_tool_violations=sum(r['tool_violation'] for r in callrows),event_item_types=dict(itemtypes),source_reference_checks=12,upstream_calculation_checks=48,natural_design_selections=sum(r['natural_design_selected'] for r in upstream if r['checker_context']=='delegated'),natural_selection_opportunities=24,initial_program_successes=sum(r['analyst_program_ok'] for r in upstream if r['checker_context']=='delegated'),upstream_arithmetic_passes=sum(r['arithmetic_pass'] for r in upstream),checker_code_revisions=sum(r['code_revised'] for r in upstream),scope='Prospective development experiment, no public preregistration, four mathematical structures, same-provider models, one draw per model/task/policy, shared upstream artifacts. No significance tests or intrinsic model ranking.')
    for name,records in [('episodes',rows),('summary',summary),('paired_contrasts',contrasts),('upstream',upstream),('model_calls',callrows)]:write_csv(out/(name+'.csv'),records)
    save(out/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(analyze(a.root,a.out),indent=2))
