"""Post-run citation audit: keep frozen scores, separately recognize visible fields.

The frozen record-ID contract admits supporting-record IDs only. Ten saved
answers instead name the actually received population_table field. This layer
retains every strict flag and never excuses an unsupported causal answer.
"""
from pathlib import Path
import argparse,csv,copy,json,datetime
from workflow import ROOT,available_key,scientific_answer,grade_one,score
from model_client import read,save
from analyze_workflow import write_csv,CONTRASTS

def audit_one(case,packet,decision):
    strict=score(case,packet,decision,case['source_key']);answer=scientific_answer(decision)
    ids=decision.get('evidence_ids',[]) if isinstance(decision,dict) else []
    # Exact field-name match only; no semantic model or discretionary alias list.
    visible_aliases=[x for x in ids if x=='population_table' and x in packet]
    unknown=[x for x in ids if x not in packet['received_supporting_records'] and x not in visible_aliases]
    current=grade_one(answer,available_key(case,packet)[0]) if answer else {'correct':False}
    source=grade_one(answer,case['source_key']) if answer else {'correct':False}
    supported=bool(current['correct'] and not unknown)
    return dict(strict_supported=strict['scientifically_supported'],strict_source_completed=strict['source_task_completed'],strict_id_flag=strict.get('invented_evidence_reference',False),visible_population_table_alias=bool(visible_aliases),unreceived_references=unknown,answer_type_and_value_supported=bool(current['correct']),audited_supported=supported,audited_source_completed=bool(supported and source['correct']),audited_safe_incomplete=bool(supported and not source['correct']))

def audit(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True);cases={x['case_id']:x for x in read(root/'data/cases.json')}
    frozen=read(root/'results/results.json');rows=list(csv.DictReader((root/'results/episodes.csv').open(encoding='utf-8')));audits=[]
    for row in rows:
        directory=root/'runs'/row['model']/row['case_id']/row['route'];episode=read(directory/'episode.json');packet=read(directory/('final_packet.json' if episode['archive_requested'] else 'initial_packet.json'))
        result=audit_one(cases[row['case_id']],packet,episode['final_decision'])
        if row['tool_violation']=='True':result['audited_supported']=False;result['audited_source_completed']=False
        audits.append(dict(model=row['model'],case_id=row['case_id'],route=row['route'],**result))
    report=copy.deepcopy(frozen);newsummary=[]
    for s in frozen['summary']:
        a=[x for x in audits if x['model']==s['model'] and x['route']==s['route']];n=dict(s)
        n.update(strict_final_supported=s['final_supported'],strict_source_completed=s['source_completed'],strict_record_id_flags=s['unreceived_evidence_references'],final_supported=sum(x['audited_supported'] for x in a),source_completed=sum(x['audited_source_completed'] for x in a),final_safe_incomplete=sum(x['audited_safe_incomplete'] for x in a),unreceived_evidence_references=sum(bool(x['unreceived_references']) for x in a),visible_field_aliases=sum(x['visible_population_table_alias'] for x in a))
        # Full-source answerable completion, applying the same transparent audit.
        n['answerable_completed']=sum(x['audited_source_completed'] for x in a if cases[x['case_id']]['source_key']['answer']['answer_type']!='not_identified')
        newsummary.append(n)
    report['summary']=newsummary
    report['citation_audit']=dict(status='Post-run sensitivity/reporting audit; frozen strict results remain unchanged in results.json and episodes.csv.',strict_record_id_flags=sum(x['strict_id_flag'] for x in audits),references_to_actually_received_population_table=sum(x['visible_population_table_alias'] for x in audits if x['strict_id_flag']),remaining_unreceived_reference_episodes=sum(bool(x['unreceived_references']) for x in audits),answer_type_and_value_supported=sum(x['answer_type_and_value_supported'] for x in audits),audited_supported=sum(x['audited_supported'] for x in audits),rule='Recognize only the exact population_table field name when that field was present in the saved recipient packet. All unknown record IDs remain invalid. Scientific type/value checks and identifying-evidence rules are unchanged.')
    flat=[{**x,'unreceived_references':';'.join(x['unreceived_references'])} for x in audits]
    write_csv(out/'citation_audit.csv',flat);write_csv(out/'scientific_summary.csv',newsummary);save(out/'reporting_results.json',report)
    contrasts=[]
    for model in frozen['models']:
        for left,right in CONTRASTS:
            for outcome in ('audited_source_completed','audited_supported'):
                pairs=[(next(x for x in audits if x['model']==model and x['case_id']==cid and x['route']==left)[outcome],next(x for x in audits if x['model']==model and x['case_id']==cid and x['route']==right)[outcome]) for cid in cases]
                contrasts.append(dict(model=model,left=left,right=right,outcome=outcome,matched_tasks=len(pairs),left_only=sum(a and not b for a,b in pairs),right_only=sum(b and not a for a,b in pairs),both=sum(a and b for a,b in pairs),neither=sum(not a and not b for a,b in pairs),difference_in_counts=sum(a-b for a,b in pairs)))
    write_csv(out/'scientific_paired_contrasts.csv',contrasts)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);a=p.parse_args();r=audit(a.root,a.out);print(json.dumps(r['citation_audit'],indent=2))
