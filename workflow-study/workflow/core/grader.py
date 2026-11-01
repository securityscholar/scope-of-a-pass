"""Strict automatic grading. Does not import generator, oracle or proof code."""
import math

KINDS={'association','causal_effect','not_identified'}

def grade_one(response,key):
    expected=key['answer'];issues=[]
    if not isinstance(response,dict):return dict(correct=False,issues=['invalid_format'],unsupported_causal_claim=False,unnecessary_abstention=False,numerical_error=False)
    if set(response)!={'task_id','answer_type','value'}:issues.append('invalid_fields')
    if response.get('task_id')!=expected['task_id']:issues.append('wrong_task_id')
    kind=response.get('answer_type');value=response.get('value')
    if not isinstance(kind,str) or kind not in KINDS:issues.append('invalid_answer_type')
    numeric=type(value) in (int,float) and -1<=value<=1 and math.isfinite(value)
    if value is not None and not numeric:issues.append('invalid_value')
    unsupported=(kind=='causal_effect' and expected['answer_type']=='not_identified')
    unnecessary=(kind=='not_identified' and expected['answer_type']!='not_identified')
    if unsupported:issues.append('unsupported_causal_claim')
    if unnecessary:issues.append('unnecessary_abstention')
    if kind!=expected['answer_type']:issues.append('wrong_claim_type')
    number_error=False
    if expected['value'] is None:
        if value is not None:issues.append('point_estimate_where_not_identified')
    elif not numeric:
        issues.append('missing_or_invalid_estimate')
    elif not math.isclose(value,expected['value'],rel_tol=0,abs_tol=1e-8):
        issues.append('incorrect_numeric_value');number_error=True
    return dict(correct=not issues,issues=issues,unsupported_causal_claim=unsupported,unnecessary_abstention=unnecessary,numerical_error=number_error)

def grade_all(responses,keys):
    grouped={};invalid_records=[];unknown=[]
    for i,response in enumerate(responses):
        if not isinstance(response,dict) or not isinstance(response.get('task_id'),str):invalid_records.append(i);continue
        task_id=response['task_id']
        if task_id not in keys:unknown.append(task_id);continue
        grouped.setdefault(task_id,[]).append(response)
    rows=[]
    for task_id,key in keys.items():
        candidates=grouped.get(task_id,[])
        if len(candidates)!=1:
            row=dict(correct=False,issues=['missing_response' if not candidates else 'duplicate_responses'],unsupported_causal_claim=False,unnecessary_abstention=False,numerical_error=False)
        else:row=grade_one(candidates[0],key)
        row.update(task_id=task_id,expected_answer_type=key['answer']['answer_type'])
        rows.append(row)
    total=len(rows)
    summary=dict(tasks_total=total,correct=sum(r['correct'] for r in rows),missing=sum('missing_response' in r['issues'] for r in rows),duplicate_task_ids=sum('duplicate_responses' in r['issues'] for r in rows),unsupported_causal_claims=sum(r['unsupported_causal_claim'] for r in rows),unnecessary_abstentions=sum(r['unnecessary_abstention'] for r in rows),numerical_errors=sum(r['numerical_error'] for r in rows),nonidentified_tasks=sum(r['expected_answer_type']=='not_identified' for r in rows),identified_or_descriptive_tasks=sum(r['expected_answer_type']!='not_identified' for r in rows),invalid_record_indices=invalid_records,unknown_task_ids=unknown,protocol_valid=not invalid_records and not unknown and not any('duplicate_responses' in r['issues'] for r in rows))
    summary['accuracy']=summary['correct']/total if total else None
    return dict(summary=summary,cases=rows)
