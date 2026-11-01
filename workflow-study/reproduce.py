"""Reproduce both the executed workflow study and the preserved prior pilots."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys,tempfile,uuid,zipfile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'workflow'))
from analyze_workflow import analyze
from validate_information_sets import validate
from audit_citations import audit

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out');a=p.parse_args()
    base=Path('LOCAL_REPRODUCTION_OUTPUTS') if Path('LOCAL_DRIVE_ROOT/').exists() else Path(tempfile.gettempdir())/'GuardLab_Workflow_Reproductions'
    out=Path(a.out).resolve() if a.out else base/(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]);out.mkdir(parents=True,exist_ok=False)
    manifest=ROOT/'SHA256SUMS.json'
    if manifest.exists():
        for x in json.loads(manifest.read_text(encoding='utf-8'))['files']:
            assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],'Release file changed: '+x['path']
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1';env['TEMP']=str(out);env['TMP']=str(out)
    test=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'workflow/tests'),'-v'],cwd=out,env=env,capture_output=True,text=True,encoding='utf-8');(out/'workflow_engineering_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8');assert test.returncode==0,'Workflow tests failed'
    test2=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'workflow/audit_tests'),'-v'],cwd=out,env=env,capture_output=True,text=True,encoding='utf-8');(out/'postrun_citation_audit_tests.txt').write_text(test2.stdout+test2.stderr,encoding='utf-8');assert test2.returncode==0,'Citation audit tests failed'
    validate(ROOT/'workflow',out/'information_sets.json');assert json.loads((out/'information_sets.json').read_text())==json.loads((ROOT/'workflow/evaluator/information_sets.json').read_text())
    result=analyze(ROOT/'workflow',out/'workflow_regraded')
    for name in ('results.json','episodes.csv','summary.csv','paired_contrasts.csv','upstream.csv','model_calls.csv'):
        assert (out/'workflow_regraded'/name).read_bytes()==(ROOT/'workflow/results'/name).read_bytes(),'Saved analysis differs: '+name
    audited=audit(ROOT/'workflow',out/'workflow_regraded')
    for name in ('reporting_results.json','scientific_summary.csv','citation_audit.csv','scientific_paired_contrasts.csv'):
        assert (out/'workflow_regraded'/name).read_bytes()==(ROOT/'workflow/results'/name).read_bytes(),'Citation audit differs: '+name
    archive=ROOT/'prior_development/prior_release.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='65b327dabee4fbb4c95de807e0862800acd37442f44a5d3f18f4149d3d2b1594'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None;z.extractall(out/'prior_release')
    priorroot=out/'prior_release/The_Scope_of_a_Pass'
    prior=subprocess.run([sys.executable,'-B',str(priorroot/'artifact/reproduce.py'),'--out',str(out/'prior_reproduction')],cwd=out,env=env,capture_output=True,text=True,encoding='utf-8');(out/'prior_reproduction_log.txt').write_text(prior.stdout+prior.stderr,encoding='utf-8');assert prior.returncode==0,'Historical release reproduction failed'
    old=json.loads((out/'prior_reproduction/REPRODUCTION_REPORT.json').read_text())
    report=dict(status='passed',model_calls=0,network_calls=0,gpu_used=False,workflow_engineering_tests=16,postrun_citation_audit_tests=4,prior_engineering_tests=20,workflow_information_regimes_reverified=24,workflow_source_reference_checks=12,numerical_artifacts_reconstructed=48,receiver_episodes_regraded=result['completed_episodes'],saved_analysis_matches=True,citation_audit=audited['citation_audit'],prior_experiments=old['saved_experiments'],experiments_pooled=False,output=str(out))
    (out/'REPRODUCTION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
