"""Exact answer oracle using visible tables and explicitly supplied assumptions.

Does not import the task generator or grader. Does not infer assumptions from data.
"""
from collections import defaultdict
from fractions import Fraction as F

def mechanical_checks(task):
    rows=task['table'];seen=set()
    if not isinstance(rows,list) or not rows:raise ValueError('Population table must be nonempty')
    for r in rows:
        if type(r.get('x')) is not int or r['x'] not in (0,1) or type(r.get('y')) is not int or r['y'] not in (0,1):raise ValueError('X and Y must be binary integers')
        if type(r.get('weight')) is not int or r['weight']<=0:raise ValueError('Weights must be positive integers')
        z=r.get('z')
        if z is not None and (type(z) is not int or z<0):raise ValueError('Z must be a nonnegative integer')
        key=(z,r['x'],r['y'])
        if key in seen:raise ValueError('Duplicate cell')
        seen.add(key)
    strata={r.get('z') for r in rows}
    if any((z,x,y) not in seen for z in strata for x in (0,1) for y in (0,1)):raise ValueError('Incomplete binary cells')
    return dict(status='PASS',checks=['unique table cells','positive integer probability weights','complete binary cells within every displayed stratum','nonzero conditioning denominators'],scope='These are table-integrity checks; they do not verify causal identifying assumptions.')

def marginal_difference(task):
    num=defaultdict(int);den=defaultdict(int)
    for r in task['table']:
        den[r['x']]+=r['weight'];num[r['x']]+=r['weight']*r['y']
    return F(num[1],den[1])-F(num[0],den[0])

def standardized_difference(task):
    total=sum(r['weight'] for r in task['table'])
    strata=defaultdict(list)
    for r in task['table']:strata[r['z']].append(r)
    effect=F(0)
    for z,rows in strata.items():
        numerators={x:sum(r['weight']*r['y'] for r in rows if r['x']==x) for x in (0,1)}
        denominators={x:sum(r['weight'] for r in rows if r['x']==x) for x in (0,1)}
        effect+=F(sum(r['weight'] for r in rows),total)*(F(numerators[1],denominators[1])-F(numerators[0],denominators[0]))
    return effect

def witnesses(task):
    """Two potential-outcome populations reproduce exactly the observed law."""
    worlds=[]
    for endpoint in ('lower','upper'):
        world=[]
        for r in task['table']:
            y0=r['y'] if r['x']==0 else (1 if endpoint=='lower' else 0)
            y1=r['y'] if r['x']==1 else (0 if endpoint=='lower' else 1)
            world.append(dict(z=r.get('z'),x=r['x'],y0=y0,y1=y1,weight=r['weight']))
        worlds.append(world)
    return worlds

def reference(task):
    mechanical_checks(task)
    target=task['target'];assumptions=task['assumptions'];design=task['design']
    if target=='observed_risk_difference':
        kind='association';value=marginal_difference(task);method='Observed conditional-risk difference; no causal interpretation is requested.'
    elif target=='average_causal_risk_difference':
        if assumptions.get('consistency') is not True or assumptions.get('no_interference') is not True:raise ValueError('Unsupported causal-assumption regime')
        if design=='randomized' and assumptions.get('exchangeability')=='unconditional':
            kind='causal_effect';value=marginal_difference(task);method='Random assignment, consistency and positivity identify the population causal risk difference.'
        elif design=='observational_adjusted' and assumptions.get('exchangeability')=='given_z':
            if any('z' not in r for r in task['table']):raise ValueError('Required Z strata are missing')
            kind='causal_effect';value=standardized_difference(task);method='Standardize stratum-specific causal contrasts over the displayed population distribution of Z under the supplied conditional exchangeability assumptions.'
        elif design=='observational' and assumptions.get('exchangeability')=='not_assumed':
            kind='not_identified';value=None;method='Two compatible potential-outcome populations have the same observed probability table and different intervention effects.'
        else:raise ValueError('Unsupported or inconsistent design/assumption regime')
    else:raise ValueError('Unsupported estimand')
    answer=dict(task_id=task['task_id'],answer_type=kind,value=float(value) if value is not None else None)
    proof=dict(method=method,exact_fraction=str(value) if value is not None else None,observed_difference_fraction=str(marginal_difference(task)))
    if kind=='not_identified':proof['compatible_worlds']=witnesses(task)
    return dict(answer=answer,proof=proof)
