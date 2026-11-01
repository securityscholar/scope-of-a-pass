"""Freeze a prospective development comparison before experimental responses."""
from pathlib import Path
import copy,datetime,hashlib,json,random,sys
from workflow import ROUTES,digest,source_packet
from model_client import save
sys.path.insert(0,str(Path(__file__).resolve().parent/'core'))
from tasks import make_case,FAMILIES,DOMAINS
from oracle import reference
from proofs import verify

ROOT=Path(__file__).resolve().parent
def build_cases():
    cases=[]
    for f,family in enumerate(FAMILIES):
        for j in range(3):
            seed=730129+100003*f+j*79
            task,private=make_case(family,seed,False)
            domain=DOMAINS[(f+j)%len(DOMAINS)];task['context'].update(x=domain[0],y=domain[1])
            target='the exact descriptive difference P(Y=1|X=1) minus P(Y=1|X=0)' if family=='descriptive' else 'the average causal risk difference E[Y(1)] minus E[Y(0)], if identified by the supplied evidence'
            commission=f'Assess {domain[0]} (X) and {domain[1]} (Y) in this synthetic organizational population. The requested quantity is {target}. If the requested causal effect is not uniquely identified, report not_identified without a point estimate. Positive values mean higher probability of Y under X=1.'
            if family=='randomized':design='Training/exposure access X was assigned by lottery independently of both potential outcomes, with full compliance, both exposure levels possible, consistency and no interference. The displayed weights describe the exact population law.'
            elif family=='observational_adjusted':design='X was observed in ordinary operations. Z is measured before exposure. Within each Z stratum, assignment is independent of Y(0) and Y(1). Consistency, no interference and positivity within each Z stratum hold. The target is the entire displayed population, using its population distribution of Z.'
            else:design='X was observed in ordinary operations. Consistency and no interference hold. No random assignment, conditional exchangeability, instrumental-variable restriction or other condition identifying a causal effect is supplied. The table nevertheless identifies a descriptive conditional-risk difference.'
            rng=random.Random(seed+43);ids=['R'+str(seed%10000)+'-'+str(i) for i in (1,2,3)];rng.shuffle(ids)
            records={ids[0]:dict(kind='design_record',text=design),ids[1]:dict(kind='organizational_context',text='The binary exposure and outcome definitions refer to the same organizational population and period. The data are constructed, not observations about any actual organization.'),ids[2]:dict(kind='data_quality_record',text='Every displayed binary cell has positive integer probability weight. There are no duplicate displayed cells. The population table is complete for the displayed variables.')}
            order=list(records);rng.shuffle(order);records={k:records[k] for k in order}
            key=reference(task);proof=verify(task,private,key)
            cases.append(dict(case_id=task['task_id'],family=family,seed=seed,task=task,commission=commission,records=records,design_record_id=ids[0],source_key=key,private_world=private,reference_proof=proof))
    return cases

def main():
    assert not (ROOT/'protocol_W2.json').exists(),'Freeze already exists; preserve it'
    cases=build_cases();random.Random(20411).shuffle(cases)
    order={c['case_id']:random.Random(4951+i).sample(list(ROUTES),len(ROUTES)) for i,c in enumerate(cases)}
    save(ROOT/'data/cases.json',cases)
    frozen=[]
    for pattern in ('*.py','core/*.py','tests/*.py'):
        frozen.extend(ROOT.glob(pattern))
    frozen.append(ROOT/'data/cases.json')
    protocol=dict(protocol_id='GuardLab-actual-workflow-W2',frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='Locally frozen prospective DEVELOPMENT experiment, not public preregistration. Designed after pilot 1 and H1; no W2 model outputs observed at freeze.',models=['gpt-6-astra','gpt-6.1-sol'],reasoning_effort='high',client='Codex CLI 0.165.0 with existing sign-in, same harness and effort for both models',cases=12,mathematical_structures=4,instances_per_structure=3,routes=list(ROUTES),receiver_episodes=144,source_analyses=24,route_order=order,task_order=[c['case_id'] for c in cases],concurrency='Two cloud-call workers total, one per model; arithmetic workers time-limited to three seconds; no GPU or private corpus.',source_selection='Fixed seeds, no showcased examples, no outcome-based filtering. Domains rotate across task families.',single_agent='Cumulative transcript replay: one researcher plans, executes, checks and interprets with the complete source retained. CLI calls are fresh; prior context is replayed explicitly.',delegated='Fresh role contexts; analyst-generated computation, harness execution, numerical peer review, interpreter decision and at most one archive retrieval.',natural_handoff='Analyst selects up to two of three supporting records. Commission and table always travel. Selected records are transferred verbatim; no manual or LLM coding of summary semantics.',stress_handoff='Separate intentional removal of the design record from the selected set; not classified as an endogenous omission.',message_controls='General receipt; numerical-scope receipt; general receipt plus the identical caution as a separate methodological reminder. All retain the same true numerical receipt and data.',primary_outcomes=['final scientific support relative to actually received evidence','supported completion relative to full source task','initial/final unsupported causal claims','safe but incomplete answers','archive retrieval','arithmetic failure and repair','model and tool failures'],primary_contrasts=['single_shared vs delegated_full: organization/context representation comparison','delegated_selected vs delegated_full: natural record-selection policy','delegated_drop_general vs delegated_selected: deliberately lost design evidence','delegated_drop_scoped vs delegated_drop_general: scope communication','delegated_drop_scoped vs delegated_drop_reminder: receipt anchoring versus separate caution'],accounting='All 144 planned episodes remain in denominators. Upstream stages shared within model/task for matched route comparisons. Cases/seeds/role calls do not create independent mathematical structures. Report models separately; no significance search or pooled intrinsic capability ranking.',stopping='Complete every planned episode once. One archive retrieval maximum. Up to two transport attempts per logical stage; never regenerate a malformed/scientifically incorrect response. Preserve all records. No prompt changes after first W2 output.',sampling_limits='Twelve synthetic tasks and four structures; no population-level causal claim about organizations, no general claim about all frontier models. Source-identification formulas established mathematics. No independent human audit yet.',model_access_check='Sol access check on unrelated READY task completed before freeze, with no tools. Astra access established in prior development pilot.',frozen_files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(frozen))})
    save(ROOT/'protocol_W2.json',protocol)
    print(json.dumps(dict(frozen=protocol['frozen_utc'],cases=len(cases),episodes=144,all_source_answers_verified=all(c['reference_proof']['verified'] for c in cases),source_keys=[(c['family'],c['source_key']['answer']['value']) for c in cases]),indent=2))
if __name__=='__main__':main()
