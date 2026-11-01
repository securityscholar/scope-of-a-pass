"""Run the frozen workflow comparison; resume by reusing exact checkpoints."""
from pathlib import Path
import argparse,hashlib,json,sys
from model_client import call,read,save,now
from workflow import *

def check_frozen(root):
    protocol=read(root/'protocol_W2.json')
    for rel,want in protocol['frozen_files'].items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==want,'Frozen file changed: '+rel
    return protocol

def usable(record):return record.get('answer') if not record.get('tool_violation') else None

def run(model):
    root=Path(__file__).resolve().parent;protocol=check_frozen(root);assert model in protocol['models'];cases={c['case_id']:c for c in read(root/'data/cases.json')}
    for k,case_id in enumerate(protocol['task_order'],1):
        case=cases[case_id];base=f'{case_id}'
        print(f'CASE {k}/{len(cases)} {model} {case_id}',flush=True)
        if (root/'runs'/model/base/'case_complete.json').exists():
            print('Resuming after already completed case.',flush=True)
            continue
        analyst_record=call(root,model,base+'/analyst',analyst_prompt(case),ANALYST_SCHEMA);analysis=usable(analyst_record)
        original_execution=execute(analysis.get('python_code','') if isinstance(analysis,dict) else '',case['task']['table'])
        save(root/'runs'/model/base/'analyst_execution.json',original_execution)
        checker_record=call(root,model,base+'/checker_delegated',checker_prompt(case,analysis,original_execution,False),CHECKER_SCHEMA);review=usable(checker_record)
        single_checker_record=call(root,model,base+'/checker_single',checker_prompt(case,analysis,original_execution,True),CHECKER_SCHEMA);single_review=usable(single_checker_record)
        built=make_artifact(case,analysis,original_execution,review);single_built=make_artifact(case,analysis,original_execution,single_review)
        save(root/'runs'/model/base/'upstream.json',dict(analyst=analysis,delegated_review=review,single_review=single_review,delegated_artifact=built,single_artifact=single_built))
        for route in protocol['route_order'][case_id]:
            directory=root/'runs'/model/base/route
            packet=route_packet(case,analysis,single_built if route=='single_shared' else built,route,single_review)
            save(directory/'initial_packet.json',packet)
            first_record=call(root,model,base+'/'+route+'/initial',decision_prompt(packet,route),DECISION_SCHEMA);first=usable(first_record)
            retrieved=isinstance(first,dict) and first.get('action')=='request_design_record'
            final_packet=retrieve(case,packet) if retrieved else packet
            if retrieved:
                save(directory/'retrieval.json',final_packet['archive_retrieval']);save(directory/'final_packet.json',final_packet)
                final_record=call(root,model,base+'/'+route+'/after_retrieval',decision_prompt(final_packet,route,True),DECISION_SCHEMA);final=usable(final_record)
            else:final=first;final_record=first_record
            save(directory/'episode.json',dict(case_id=case_id,model=model,route=route,initial_decision=first,final_decision=final,archive_requested=retrieved,initial_has_design=case['design_record_id'] in packet['received_supporting_records'],final_has_design=case['design_record_id'] in final_packet['received_supporting_records'],initial_input_sha256=first_record['input_sha256'],final_input_sha256=final_record['input_sha256'],tool_violation=bool(first_record.get('tool_violation') or final_record.get('tool_violation')),completed_utc=now()))
        save(root/'runs'/model/'progress.json',dict(cases_finished=k,planned_cases=len(cases),last_case_id=case_id,updated_utc=now()))
        save(root/'runs'/model/base/'case_complete.json',dict(completed_utc=now(),episodes=len(protocol['routes']),protocol_sha256=hashlib.sha256((root/'protocol_W2.json').read_bytes()).hexdigest()))
    save(root/'runs'/model/'completion.json',dict(completed_utc=now(),cases=12,receiver_episodes=72,all_planned_slots_attempted=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);a=p.parse_args();run(a.model)
