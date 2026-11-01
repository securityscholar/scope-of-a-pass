"""Generate finite probability tables; no imports from the answer oracle."""
import hashlib
import random

FAMILIES=('descriptive','randomized','observational_unidentified','observational_adjusted')
DOMAINS=(('training access','high productivity'),('remote-work eligibility','high retention'),('mentoring access','promotion'),('process adoption','project completion'))

def _table(weights,propensities,risks):
    rows=[]
    for z,w in enumerate(weights):
        for x in (0,1):
            nx=propensities[z] if x else 5-propensities[z]
            for y in (0,1):
                ny=risks[z][x] if y else 10-risks[z][x]
                row=dict(x=x,y=y,weight=w*nx*ny)
                if len(weights)>1:row['z']=z
                rows.append(row)
    return rows

def _world(weights,propensities,risks):
    """A separate latent population with both potential outcomes specified."""
    rows=[]
    for z,w in enumerate(weights):
        for x in (0,1):
            for y0 in (0,1):
                for y1 in (0,1):
                    px=propensities[z] if x else 5-propensities[z]
                    p0=risks[z][0] if y0 else 10-risks[z][0]
                    p1=risks[z][1] if y1 else 10-risks[z][1]
                    rows.append(dict(z=z if len(weights)>1 else None,x=x,y0=y0,y1=y1,weight=w*px*p0*p1))
    return rows

def make_case(family,seed,showcase=False):
    if family not in FAMILIES:raise ValueError('Unsupported family')
    rng=random.Random(seed)
    adjusted=family=='observational_adjusted'
    if showcase:
        weights,propensities,risks=([1,1],[1,4],[(2,1),(8,7)]) if adjusted else ([1],[2],[(2,7)])
    else:
        count=2 if adjusted else 1
        weights=[rng.randint(1,5) for _ in range(count)]
        propensities=[rng.randint(1,4) for _ in range(count)]
        risks=[(rng.randint(1,9),rng.randint(1,9)) for _ in range(count)]
    design='randomized' if family=='randomized' else ('observational_adjusted' if adjusted else 'observational')
    target='observed_risk_difference' if family=='descriptive' else 'average_causal_risk_difference'
    case_id=hashlib.sha256(('answer-lab-v1:'+family+':'+str(seed)+':'+str(showcase)).encode()).hexdigest()[:16]
    domain=DOMAINS[FAMILIES.index(family)]
    assumptions=dict(consistency=True,no_interference=True,exchangeability='unconditional' if design=='randomized' else ('given_z' if adjusted else 'not_assumed'))
    task=dict(task_id=case_id,context=dict(x=domain[0],y=domain[1],z='pre-existing organizational context' if adjusted else None),table=_table(weights,propensities,risks),table_meaning='Exact population probability weights, not a finite sample. Divide weights by their sum to obtain the joint population distribution. There is no sampling-error or confidence-interval question.',design=design,assumptions=assumptions,target=target)
    if target=='observed_risk_difference':
        task['question']='Compute P(Y=1 | X=1) minus P(Y=1 | X=0). This question asks only for a descriptive association.'
    else:
        task['question']='Determine whether E[Y(1)] minus E[Y(0)] is uniquely identified by the supplied population distribution and assumptions. Return its value if identified; otherwise report not_identified without a point estimate.'
    if design=='randomized':
        task['design_detail']='X is randomly assigned independently of both potential outcomes, with full compliance. Consistency and no interference hold.'
    elif adjusted:
        task['design_detail']='The potential outcomes Y(0), Y(1) are independent of X conditional on the observed pre-treatment Z. Consistency, no interference, and positivity within each Z stratum hold. The target population includes all Z strata with their displayed population weights.'
    else:
        task['design_detail']='X is observed, not randomized. No exchangeability or other restrictions identifying a causal effect are supplied. This does not prevent calculating a descriptive association.'
    private=dict(family=family,seed=seed,showcase=showcase,generating_world=_world(weights,propensities,risks) if family in ('randomized','observational_adjusted') else None)
    return task,private

def suite(seed=20261028,per_family=10):
    if type(per_family) is not int or not 1<=per_family<=10000:raise ValueError('per_family must be an integer between 1 and 10000')
    cases=[]
    for k,family in enumerate(FAMILIES):
        for i in range(per_family):
            cases.append(make_case(family,seed+100003*k+i,showcase=i==0))
    return cases
