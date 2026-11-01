"""Enumerate both full-source and missing-design reference regimes per case."""
from pathlib import Path
import argparse,copy,json,sys
from workflow import ROOT,reference,available_key
from model_client import read,save
from proofs import verify

def validate(root,out):
    records=[]
    for case in read(Path(root)/'data/cases.json'):
        for has_design in (True,False):
            task=copy.deepcopy(case['task'])
            if task['target']=='average_causal_risk_difference' and not has_design:
                task['design']='observational';task['assumptions']['exchangeability']='not_assumed'
            key=reference(task);proof=verify(task,case['private_world'],key)
            packet={'received_supporting_records':{case['design_record_id']:case['records'][case['design_record_id']]} if has_design else {}}
            assert available_key(case,packet)[0]==key
            records.append(dict(case_id=case['case_id'],design_received=has_design,reference=key,enumeration=proof))
    save(out,dict(reference_regimes=len(records),all_verified=all(r['enumeration']['verified'] for r in records),records=records))
    return len(records)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(dict(verified_information_sets=validate(a.root,a.out))))
