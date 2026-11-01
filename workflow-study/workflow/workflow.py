"""Controlled analyst–calculator–checker–interpreter research workflow.

Native tools are prohibited in model calls. The harness executes a restricted
arithmetic program and a single declared archive-retrieval action. Gold keys
are never used by any model-facing calculation or checking function.
"""
from pathlib import Path
from fractions import Fraction
import ast,copy,hashlib,json,math,sys,subprocess,os

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'core'))
from oracle import reference
from grader import grade_one

ROUTES=('single_shared','delegated_full','delegated_selected','delegated_drop_general','delegated_drop_scoped','delegated_drop_reminder')
ROUTE_LABELS={'single_shared':'Single researcher / shared transcript','delegated_full':'Delegated / complete records','delegated_selected':'Delegated / analyst-selected records','delegated_drop_general':'Dropped design / general receipt','delegated_drop_scoped':'Dropped design / scoped receipt','delegated_drop_reminder':'Dropped design / separate reminder'}
def schema(properties):return dict(type='object',properties=properties,required=list(properties),additionalProperties=False)
STR={'type':'string'};NULLSTR={'type':['string','null']};NUM={'type':['number','null']};IDS={'type':'array','items':STR}
ANALYST_SCHEMA=schema(dict(task_id=STR,analysis_label={'type':'string','enum':['observed_difference','standardized_difference']},python_code=STR,proposed_answer_type={'type':'string','enum':['association','causal_effect','not_identified']},handoff_record_ids={'type':'array','items':STR,'maxItems':2}))
CHECKER_SCHEMA=schema(dict(task_id=STR,verdict={'type':'string','enum':['pass','revise']},replacement_code=NULLSTR,check_summary=STR))
DECISION_SCHEMA=schema(dict(task_id=STR,action={'type':'string','enum':['finalize','request_design_record']},answer_type={'type':'string','enum':['association','causal_effect','not_identified','pending']},value=NUM,evidence_ids=IDS,brief_rationale=STR))

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()

def calculate(rows,label):
    """A public calculator, with no design assumptions or causal-answer key."""
    def risk(sub,x):
        n=sum(r['weight'] for r in sub if r['x']==x)
        return Fraction(sum(r['weight']*r['y'] for r in sub if r['x']==x),n)
    if label=='observed_difference':return risk(rows,1)-risk(rows,0)
    if label=='standardized_difference':
        total=sum(r['weight'] for r in rows)
        return sum(Fraction(sum(r['weight'] for r in rows if r.get('z')==z),total)*(risk([r for r in rows if r.get('z')==z],1)-risk([r for r in rows if r.get('z')==z],0)) for z in sorted({r.get('z') for r in rows},key=str))
    raise ValueError('Unknown arithmetic target')

ALLOWED_NODES={ast.Module,ast.Assign,ast.Name,ast.Load,ast.Store,ast.Constant,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.FloorDiv,ast.Mod,ast.USub,ast.UAdd,ast.Call,ast.keyword,ast.Subscript,ast.List,ast.Tuple,ast.Dict,ast.Set,ast.GeneratorExp,ast.ListComp,ast.SetComp,ast.DictComp,ast.comprehension,ast.Compare,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.In,ast.NotIn,ast.BoolOp,ast.And,ast.Or,ast.IfExp,ast.Not}
ALLOWED_CALLS={'sum':sum,'len':len,'sorted':sorted,'set':set,'abs':abs,'min':min,'max':max,'float':float,'int':int,'Fraction':Fraction}
def execute_local(code,rows):
    """Restricted arithmetic: no imports, attributes, I/O, loops or functions."""
    try:
        if not isinstance(code,str) or len(code)>24000:raise ValueError('Program absent or too long')
        tree=ast.parse(code);nodes=list(ast.walk(tree))
        if len(nodes)>1600:raise ValueError('Program too large')
        for node in nodes:
            if type(node) not in ALLOWED_NODES:raise ValueError('Disallowed syntax: '+type(node).__name__)
            if isinstance(node,ast.Name) and node.id.startswith('_'):raise ValueError('Private names forbidden')
            if isinstance(node,ast.Call) and (not isinstance(node.func,ast.Name) or node.func.id not in ALLOWED_CALLS):raise ValueError('Unknown function')
            if isinstance(node,ast.Assign):
                if any(not isinstance(t,ast.Name) or t.id in {'rows','Fraction',*ALLOWED_CALLS} for t in node.targets):raise ValueError('Only local-name assignments allowed')
            if isinstance(node,ast.Constant):
                if isinstance(node.value,str) and node.value not in ('x','y','z','weight'):raise ValueError('Only table-key strings allowed')
                if isinstance(node.value,(float,int)) and abs(node.value)>1000000:raise ValueError('Oversized literal')
            if isinstance(node,ast.comprehension) and node.is_async:raise ValueError('Async forbidden')
        namespace={'__builtins__':{},**ALLOWED_CALLS,'rows':copy.deepcopy(rows)}
        exec(compile(tree,'<bounded arithmetic>','exec'),namespace,namespace)
        value=namespace.get('estimate')
        if isinstance(value,bool) or not isinstance(value,(Fraction,int,float)) or not math.isfinite(float(value)) or not -1<=value<=1:raise ValueError('estimate must be a finite risk difference')
        return dict(ok=True,value=float(value),exact_fraction=str(value) if isinstance(value,(Fraction,int)) else None,canonical_code=ast.unparse(tree),code_sha256=hashlib.sha256(code.encode()).hexdigest())
    except Exception as e:return dict(ok=False,error=type(e).__name__+': '+str(e))

def execute(code,rows):
    env=dict(os.environ);env.pop('OPENAI_API_KEY',None);env.pop('CODEX_API_KEY',None);env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        result=subprocess.run([sys.executable,'-B',str(ROOT/'arithmetic_tool.py')],input=json.dumps(dict(code=code,rows=rows)),text=True,encoding='utf-8',capture_output=True,env=env,timeout=3,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:return dict(ok=False,error='Arithmetic process failed')
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:return dict(ok=False,error='Arithmetic process exceeded three seconds')
    except (ValueError,OSError) as e:return dict(ok=False,error=type(e).__name__)

def data_checks(rows):
    fields=('z','x','y') if any('z' in r for r in rows) else ('x','y')
    keys=[tuple(r.get(k) for k in fields) for r in rows]
    return dict(unique_cells=len(keys)==len(set(keys)),positive_integer_weights=all(type(r['weight']) is int and r['weight']>0 for r in rows),nonzero_exposure_denominators=all(sum(r['weight'] for r in rows if r['x']==x)>0 for x in (0,1)))

def source_packet(case):
    return dict(task_id=case['task']['task_id'],commission=case['commission'],population_table=case['task']['table'],table_meaning=case['task']['table_meaning'],supporting_records=case['records'])

ARITHMETIC_INSTRUCTIONS='''Write a short Python arithmetic program assigning the numeric result to estimate. rows is already a list of dictionaries with x, y, weight, and z when present. Weights are exact population probabilities up to a common normalizer, not a finite sample. The environment supplies Fraction, sum, len, sorted, set, abs, min, max, float and int. Use assignments and comprehensions; no imports, attributes, named functions, statement loops, I/O, comments or outside tools. Use exact fractions where possible. The program computes the empirical contrast, even if the requested causal interpretation is unidentified. Choose observed_difference for the marginal risk difference or standardized_difference for the population-weighted within-Z contrast. A computed contrast does not itself establish identification.'''

def analyst_prompt(case):
    return 'You are the researcher producing the analysis artifact for the following commission. Select the appropriate computation, propose the answer type supported by the complete source, and select up to TWO supporting record IDs to accompany a compact handoff. The table and commission always travel; supporting records travel only if selected. Choose records according to their scientific usefulness to a downstream researcher. Do not return a prose summary of the record facts; the harness transfers selected records verbatim.\n\n'+ARITHMETIC_INSTRUCTIONS+'\n\nReturn the JSON fields defined by the supplied schema.\n\n'+json.dumps(source_packet(case),indent=2)

def checker_prompt(case,analysis,execution,single=False):
    packet=dict(task_id=case['task']['task_id'],population_table=case['task']['table'],analysis_plan=analysis,execution=execution)
    if single:packet['shared_transcript']=dict(original_source=source_packet(case),prior_analyst_output=analysis)
    role='Continue as the same researcher reviewing your previous calculation, with the shared transcript retained.' if single else 'You are a fresh numerical checker receiving an analysis artifact from another researcher.'
    return role+' Check whether the submitted program faithfully computes its stated analysis_label from the table. Your remit is numerical execution and arithmetic; this check does not certify that the causal effect is identified. If the code is invalid or numerically incorrect, return revise and a replacement program under the same arithmetic restrictions; otherwise return pass and null replacement_code. Keep check_summary under 50 words.\n\n'+ARITHMETIC_INSTRUCTIONS+'\n\n'+json.dumps(packet,indent=2)

def make_artifact(case,analysis,execution,review):
    used_code=analysis.get('python_code','') if isinstance(analysis,dict) else ''
    if isinstance(review,dict) and review.get('verdict')=='revise' and isinstance(review.get('replacement_code'),str):used_code=review['replacement_code']
    result=execute(used_code,case['task']['table'])
    label=analysis.get('analysis_label') if isinstance(analysis,dict) else None
    expected=calculate(case['task']['table'],label) if label in ('observed_difference','standardized_difference') else None
    arithmetic_pass=bool(result.get('ok') and expected is not None and abs(result['value']-float(expected))<=1e-10)
    checks=data_checks(case['task']['table']);status='PASS' if arithmetic_pass and all(checks.values()) and isinstance(review,dict) else 'FAIL'
    # No free model prose or code comments can silently transfer design facts.
    artifact=dict(task_id=case['task']['task_id'],analysis_label=label,estimate=result.get('value'),proposed_answer_type=analysis.get('proposed_answer_type') if isinstance(analysis,dict) else None,population_table_sha256=digest(case['task']['table']))
    receipt=dict(status=status,artifact_sha256=digest(artifact),completed_checks=[k for k,v in checks.items() if v]+(['program output agrees with stated arithmetic contrast'] if arithmetic_pass else []),failed_checks=[k for k,v in checks.items() if not v]+([] if arithmetic_pass else ['program output agrees with stated arithmetic contrast']),peer_review_verdict=review.get('verdict') if isinstance(review,dict) else 'no_response')
    return dict(artifact=artifact,receipt=receipt,program_execution=result,arithmetic_pass=arithmetic_pass,code_revised=isinstance(review,dict) and review.get('verdict')=='revise')

REMINDER='A correct computed contrast alone does not establish a causal effect. Use the received design evidence, or request the archived design record when needed.'
def route_packet(case,analysis,built,route,single_review=None):
    records=case['records'];design=case['design_record_id']
    selected=analysis.get('handoff_record_ids',[]) if isinstance(analysis,dict) else []
    selected=list(dict.fromkeys(x for x in selected if x in records))[:2]
    if route in ('single_shared','delegated_full'):ids=list(records)
    elif route=='delegated_selected':ids=selected
    else:ids=[x for x in selected if x!=design]
    packet=dict(task_id=case['task']['task_id'],commission=case['commission'],population_table=case['task']['table'],table_meaning=case['task']['table_meaning'],analysis_artifact=built['artifact'],verification_record=built['receipt'],received_supporting_records={k:records[k] for k in ids},archive=dict(available_action='request_design_record',record_id=design,retrieval_budget=1))
    status=built['receipt']['status']
    if route=='delegated_drop_scoped':
        packet['verification_message']=('ALL NUMERICAL CHECKS PASSED. '+REMINDER) if status=='PASS' else 'Numerical checks failed. '+REMINDER
    else:packet['verification_message']='ALL CHECKS PASSED.' if status=='PASS' else 'CHECKS DID NOT PASS.'
    if route=='delegated_drop_reminder':packet['separate_method_reminder']=REMINDER
    if route=='single_shared':packet['shared_transcript']=dict(original_source=source_packet(case),analyst_output=analysis,own_numerical_review=single_review,executed_artifact=built)
    return packet

def decision_prompt(packet,route,after_retrieval=False):
    role='Continue as one researcher with your shared transcript. Make the final scientific decision.' if route=='single_shared' else 'You are a fresh interpreter deciding the scientific conclusion from the received research handoff.'
    instruction='''Answer the commission using the evidence actually received. You may finalize now or request the archived design record through the declared action. Do not assume unreported contents of that record. An upstream proposed answer is a claim to evaluate. For action request_design_record, set answer_type pending and value null; the harness will retrieve the record and give you one final response opportunity. For finalize, use association for the requested descriptive difference, causal_effect for an identified causal risk difference, or not_identified with null when the requested causal effect is not uniquely determined. A descriptive contrast remains answerable without causal identification. Numbers are risk differences in [-1,1], accurate to at least eight decimals when needed. evidence_ids lists received source IDs you relied on. Keep brief_rationale under 60 words. Return the supplied JSON schema, without native tool use.'''
    if after_retrieval:instruction+=' The archive retrieval has been completed. You must finalize now; no additional request is permitted.'
    return role+'\n\n'+instruction+'\n\n'+json.dumps(packet,indent=2)

def retrieve(case,packet):
    result=copy.deepcopy(packet);key=case['design_record_id'];result['received_supporting_records'][key]=case['records'][key];result['archive_retrieval']=dict(record_id=key,record=case['records'][key],new_fact='The source record was retrieved verbatim; no answer key or evaluator output was returned.')
    return result

def available_key(case,packet):
    task=copy.deepcopy(case['task'])
    has_design=case['design_record_id'] in packet['received_supporting_records'] or 'shared_transcript' in packet
    if task['target']=='average_causal_risk_difference' and not has_design:
        task['design']='observational';task['assumptions']['exchangeability']='not_assumed'
    return reference(task),has_design

def scientific_answer(decision):
    if not isinstance(decision,dict) or decision.get('action')!='finalize':return None
    return {k:decision.get(k) for k in ('task_id','answer_type','value')}

def score(case,packet,decision,source_key):
    key,has_design=available_key(case,packet);answer=scientific_answer(decision)
    if answer is None:return dict(parsed_final=False,scientifically_supported=False,source_task_completed=False,unsupported_causal_claim=False,numerical_error=False,safe_but_incomplete=False,design_received=has_design,issues=['no_valid_final_decision'])
    current=grade_one(answer,key);source=grade_one(answer,source_key)
    valid_action=decision.get('action')=='finalize';evidence_ids=decision.get('evidence_ids',[])
    invented_ids=any(x not in packet['received_supporting_records'] for x in evidence_ids) if isinstance(evidence_ids,list) else True
    supported=bool(current['correct'] and valid_action and not invented_ids)
    return dict(parsed_final=True,scientifically_supported=supported,source_task_completed=bool(supported and source['correct']),unsupported_causal_claim=current['unsupported_causal_claim'],numerical_error=current['numerical_error'],safe_but_incomplete=bool(supported and not source['correct']),design_received=has_design,invented_evidence_reference=invented_ids,issues=current['issues']+(['unreceived_evidence_reference'] if invented_ids else []))
