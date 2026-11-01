"""Independent enumeration checks on the oracle and latent populations.

Does not import the generator, oracle, or grader.
"""
from collections import defaultdict
from fractions import Fraction

def _law(rows,world=False):
    result=defaultdict(Fraction);total=sum(r['weight'] for r in rows)
    for r in rows:
        y=(r['y1'] if r['x'] else r['y0']) if world else r['y']
        result[(r.get('z'),r['x'],y)]+=Fraction(r['weight'],total)
    return dict(result)

def _effect(world):
    denominator=sum(r['weight'] for r in world)
    return sum((Fraction(r['weight']*(r['y1']-r['y0']),denominator) for r in world),Fraction(0))

def _exchangeable(world,conditional):
    groups=defaultdict(list)
    for r in world:groups[r['z'] if conditional else None].append(r)
    for rows in groups.values():
        total=sum(r['weight'] for r in rows);x_counts=defaultdict(int);y_counts=defaultdict(int);joint=defaultdict(int)
        for r in rows:
            pair=(r['y0'],r['y1']);x_counts[r['x']]+=r['weight'];y_counts[pair]+=r['weight'];joint[(r['x'],pair)]+=r['weight']
        for x in (0,1):
            for pair,count in y_counts.items():
                if joint[(x,pair)]*total != x_counts[x]*count:return False
    return True

def verify(task,private,record):
    expected=record['answer'];out=dict(task_id=task['task_id'],verified=False)
    if expected['task_id']!=task['task_id']:raise AssertionError('Wrong task identity in the answer')
    if task['target']=='observed_risk_difference':required='association'
    elif task['target']=='average_causal_risk_difference' and task['design'] in ('randomized','observational_adjusted'):required='causal_effect'
    elif task['target']=='average_causal_risk_difference' and task['design']=='observational':required='not_identified'
    else:raise AssertionError('Unsupported target/design')
    if expected['answer_type']!=required:raise AssertionError('Answer type contradicts the requested question and supplied design')
    law=_law(task['table'])
    if expected['answer_type']=='not_identified':
        worlds=record['proof']['compatible_worlds']
        if len(worlds)!=2:raise AssertionError('Need two counterexample worlds')
        if any(_law(w,True)!=law for w in worlds):raise AssertionError('Counterexample does not reproduce the data')
        effects=[_effect(w) for w in worlds]
        if effects[0]==effects[1]:raise AssertionError('Counterexamples do not establish non-identification')
        if expected['value'] is not None:raise AssertionError('A nonidentified answer cannot contain a point value')
        out.update(verified=True,method='Directly enumerate both compatible observed laws and both intervention effects.',compatible_effects=[str(x) for x in effects],difference=str(effects[1]-effects[0]))
    elif expected['answer_type']=='causal_effect':
        world=private['generating_world']
        if _law(world,True)!=law:raise AssertionError('Latent population does not reproduce the table')
        conditional=task['design']=='observational_adjusted'
        if not _exchangeable(world,conditional):raise AssertionError('Generated world violates its asserted exchangeability')
        effect=_effect(world)
        if effect!=Fraction(record['proof']['exact_fraction']):raise AssertionError('Oracle differs from direct intervention enumeration')
        if type(expected['value']) not in (int,float) or expected['value']!=float(effect):raise AssertionError('Answer payload differs from the intervention result')
        out.update(verified=True,method='Enumerate interventions in the separately generated latent population; check exchangeability and the observed law.',intervention_effect=str(effect))
    else:
        # Compute conditional expectations directly from normalized probability law.
        mean=[]
        for x in (0,1):
            mass=sum(p for (z,xx,y),p in law.items() if xx==x)
            success=sum(p for (z,xx,y),p in law.items() if xx==x and y==1)
            mean.append(success/mass)
        diff=mean[1]-mean[0]
        if diff!=Fraction(record['proof']['exact_fraction']):raise AssertionError('Descriptive oracle disagrees')
        if type(expected['value']) not in (int,float) or expected['value']!=float(diff):raise AssertionError('Answer payload differs from the observed contrast')
        out.update(verified=True,method='Recompute conditional expectations from normalized joint probabilities.',observed_difference=str(diff))
    return out
