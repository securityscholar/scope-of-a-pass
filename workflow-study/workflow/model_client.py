"""Checkpointed text-only Codex calls; authentication never enters the records."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,time

CLI=Path(r'LOCAL_CODEX_CLI/codex.cmd')
PREFIX='This is a controlled synthetic research workflow. Use only the text and arithmetic environment described in this message. Do not call native tools, inspect files, browse, or access any other data. Return only the requested JSON object.\n\n'
def sha(value):return hashlib.sha256(value).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8');tmp.replace(path)

def call(root,model,logical_id,prompt,schema):
    directory=Path(root)/'runs'/model/logical_id;directory.mkdir(parents=True,exist_ok=True)
    fingerprint=sha(json.dumps(dict(model=model,effort='high',prompt=PREFIX+prompt,schema=schema),sort_keys=True).encode())
    checkpoint=directory/'record.json'
    if checkpoint.exists():
        rec=read(checkpoint);assert rec['input_sha256']==fingerprint,'Resume prompt changed: '+logical_id
        return rec
    save(directory/'request.json',dict(requested_model=model,reasoning_effort='high',prompt=PREFIX+prompt,schema=schema,input_sha256=fingerprint))
    schema_path=directory/'schema.json';save(schema_path,schema)
    scratch=Path('LOCAL_RUN_SCRATCH')/model;scratch.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ);env.pop('OPENAI_API_KEY',None);env.pop('CODEX_API_KEY',None);env['TEMP']=str(scratch);env['TMP']=str(scratch)
    rec=dict(logical_id=logical_id,requested_model=model,reasoning_effort='high',input_sha256=fingerprint,started_utc=now(),attempts=[],answer=None)
    total_start=time.monotonic()
    for attempt in range(1,3):
        final=directory/f'final_{attempt}.json'
        cmd=[str(CLI),'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--output-schema',str(schema_path),'-o',str(final),'-m',model,'-c','model_reasoning_effort="high"','-']
        started=time.monotonic();entry=dict(attempt=attempt,started_utc=now());events=[]
        try:
            proc=subprocess.run(cmd,input=PREFIX+prompt,encoding='utf-8',errors='replace',capture_output=True,cwd=scratch,env=env,timeout=480,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            (directory/f'events_{attempt}.jsonl').write_text(proc.stdout,encoding='utf-8');(directory/f'stderr_{attempt}.txt').write_text(proc.stderr,encoding='utf-8');entry['exit_code']=proc.returncode
            for line in proc.stdout.splitlines():
                try:events.append(json.loads(line))
                except ValueError:pass
            entry['tool_events']=[e for e in events if e.get('item',{}).get('type') in ('command_execution','file_change','mcp_tool_call','web_search')]
            entry['usage']=[e['usage'] for e in events if e.get('type')=='turn.completed' and 'usage' in e]
            if final.exists():
                entry['output_text']=final.read_text(encoding='utf-8')
                try:rec['answer']=json.loads(entry['output_text'])
                except ValueError:entry['parse_error']=True
            entry['events_reported_errors']=[e for e in events if e.get('type') in ('error','turn.failed')]
        except subprocess.TimeoutExpired:entry['timeout']=True
        entry['elapsed_seconds']=round(time.monotonic()-started,3);rec['attempts'].append(entry)
        # Never regenerate a malformed or scientifically incorrect model answer.
        if final.exists() or entry.get('tool_events'):break
        if attempt<2:time.sleep(3)
    rec['elapsed_seconds']=round(time.monotonic()-total_start,3);rec['tool_violation']=any(e.get('tool_events') for e in rec['attempts']);rec['completed_utc']=now();save(checkpoint,rec)
    print(json.dumps(dict(model=model,stage=logical_id,parsed=rec['answer'] is not None,seconds=rec['elapsed_seconds'],tool_violation=rec['tool_violation'])),flush=True)
    return rec

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    result=call(root,'gpt-6.1-sol','access_check','Return {"ready":true}. This is an access check only.',{'type':'object','properties':{'ready':{'type':'boolean'}},'required':['ready'],'additionalProperties':False})
    print(json.dumps(dict(access_check_ready=result.get('answer'))))
