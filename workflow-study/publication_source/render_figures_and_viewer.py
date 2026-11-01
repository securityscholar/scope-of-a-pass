from pathlib import Path
import json,csv,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

LABELS={'single_shared':'Shared\ntranscript','delegated_full':'Delegated\ncomplete','delegated_selected':'Analyst\nselected','delegated_drop_general':'Dropped\ngeneral','delegated_drop_scoped':'Dropped\nscoped','delegated_drop_reminder':'Dropped\nreminder'}
def render(root):
    root=Path(root);figs=root/'figures';figs.mkdir(exist_ok=True);w=root/'workflow';r=json.loads((w/'results/reporting_results.json').read_text());cases=json.loads((w/'data/cases.json').read_text());summary=r['summary'];routes=list(LABELS)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
    fig,ax=plt.subplots(figsize=(9.5,4.7));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    def box(x,y,ww,hh,text,color='#17364b'):
        ax.add_patch(FancyBboxPatch((x,y),ww,hh,boxstyle='round,pad=.009',facecolor='#f4f8f9',edgecolor=color,lw=1.3));ax.text(x+ww/2,y+hh/2,text,ha='center',va='center',color=color,fontsize=9,linespacing=1.4)
    box(.01,.71,.21,.2,'Complete source\nCommission + population\ntable + source records')
    box(.275,.71,.20,.2,'AI analyst\nWrites arithmetic program\nSelects supporting records')
    box(.53,.71,.20,.2,'Execution + AI check\nProgram actually runs\nReceipt names tested scope')
    box(.785,.71,.20,.2,'AI interpreter\nCommits a claim or\nrequests source evidence')
    for start,end in [((.22,.81),(.275,.81)),((.475,.81),(.53,.81)),((.73,.81),(.785,.81))]:ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color='#536570',lw=1.5))
    box(.06,.29,.44,.25,'Information policies\nShared transcript · Complete delegated records\nAnalyst-selected records\nDeliberate loss: general / scoped / reminder')
    box(.64,.29,.31,.25,'Controlled archive retrieval\nOriginal design record returned verbatim\nOne final decision opportunity','#147d80')
    ax.annotate('',xy=(.885,.54),xytext=(.885,.71),arrowprops=dict(arrowstyle='<->',color='#147d80',lw=1.4))
    ax.annotate('',xy=(.79,.71),xytext=(.49,.52),arrowprops=dict(arrowstyle='->',color='#536570',lw=1.3))
    box(.18,.02,.64,.15,'External evaluation: support under received evidence + source-task completion\nExact effects and compatible-world nonidentification witnesses','#b75c3b')
    fig.tight_layout(pad=.5)
    for ext in ('png','pdf','svg'):fig.savefig(figs/f'Figure_1_Workflow.{ext}',dpi=240,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(9.6,4.8),layout='constrained')
    models=r['models']
    for ax,field,title,cmap in [(axes[0],'source_completed','A. Supported source-task completion (of 12)','Blues'),(axes[1],'archive_requests','B. Archive requests (of 12)','YlGnBu')]:
        matrix=[[next(s[field] for s in summary if s['model']==m and s['route']==route) for route in routes] for m in models]
        ax.imshow(matrix,cmap=cmap,vmin=0,vmax=12,aspect='auto');ax.set_yticks(range(2),['Astra / high','Sol / high']);ax.set_xticks(range(6),[LABELS[x] for x in routes]);ax.tick_params(length=0,labelsize=9);ax.set_title(title,loc='left',fontsize=11,pad=10)
        for i,row in enumerate(matrix):
            for j,v in enumerate(row):ax.text(j,i,str(v)+'/12',ha='center',va='center',color='white' if v>=8 else '#17364b',fontsize=11,fontweight='bold')
        for spine in ax.spines.values():spine.set_visible(False)
    for ext in ('png','pdf','svg'):fig.savefig(figs/f'Figure_2_Results.{ext}',dpi=240,bbox_inches='tight')
    plt.close(fig)

    episodes=list(csv.DictReader((w/'results/episodes.csv').open(encoding='utf-8')));audit=list(csv.DictReader((w/'results/citation_audit.csv').open(encoding='utf-8')));traces={}
    for m in models:
        for c in cases:
            base=w/'runs'/m/c['case_id'];up=json.loads((base/'upstream.json').read_text());policies={}
            for route in routes:
                directory=base/route;ep=json.loads((directory/'episode.json').read_text());packet=json.loads((directory/'initial_packet.json').read_text());scores=next(x for x in episodes if x['model']==m and x['case_id']==c['case_id'] and x['route']==route)
                correction=next(x for x in audit if x['model']==m and x['case_id']==c['case_id'] and x['route']==route)
                scores={**scores,'frozen_final_supported':scores['final_supported'],'frozen_source_completed':scores['source_completed'],'final_supported':correction['audited_supported'],'source_completed':correction['audited_source_completed'],'citation_audit':correction}
                policies[route]=dict(episode=ep,initial_records=packet['received_supporting_records'],receipt=packet['verification_record'],retrieval=json.loads((directory/'retrieval.json').read_text()) if ep['archive_requested'] else None,scores=scores,raw_path=f"workflow/runs/{m}/{c['case_id']}/{route}/episode.json")
            traces[m+'|'+c['case_id']]=dict(upstream=up,policies=policies)
    payload=json.dumps(dict(result=r,cases=cases,traces=traces,labels=LABELS),ensure_ascii=False).replace('</','<\/')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Scope of a Pass · Executed workflow</title><style>
:root{--ink:#17364b;--muted:#536672;--line:#d6e1e5;--teal:#147d80}*{box-sizing:border-box}body{margin:0;background:#f4f7f8;color:var(--ink);font:16px/1.55 system-ui,Segoe UI,sans-serif}header,main,footer{max-width:1180px;margin:auto;padding:28px}header{padding-top:38px}h1{font:600 44px/1.1 Georgia,serif;margin:10px 0 16px}h2{font:600 28px/1.2 Georgia,serif}h3{font-size:17px}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--teal)}section{padding:26px;background:white;border:1px solid var(--line);border-radius:10px;margin:0 0 18px}nav,.controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}select,button{padding:9px 12px;max-width:100%;border:1px solid var(--line);border-radius:6px;color:var(--ink);background:white;font:inherit;cursor:pointer}button[aria-selected=true]{background:var(--ink);color:white}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.note{color:var(--muted);font-size:14px}pre{background:#f4f7f8;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:400px;overflow:auto;font:12px/1.55 Consolas,monospace}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:9px;border-bottom:1px solid var(--line)}th{font-size:11px;text-transform:uppercase;letter-spacing:.04em}.scroll{overflow:auto}a{color:var(--teal)}img{width:100%;height:auto}details{margin:12px 0}summary{cursor:pointer;color:var(--teal)}.result{padding:14px;border-left:4px solid var(--teal);background:#eef8f6}[hidden]{display:none!important}@media(max-width:700px){header,main,footer,section{padding:18px}.grid{grid-template-columns:1fr}h1{font-size:34px}}
</style><header><span class="eyebrow">Anonymous Stage 1 research object · Workflow experiment W2</span><h1>The Scope of a Pass</h1><p>Inspect the complete path from a model-generated calculation to a scientific decision, including the source evidence an interpreter receives or requests.</p><nav><button onclick="tab('overview',this)" aria-selected="true">Completed results</button><button onclick="tab('trace',this)" aria-selected="false">Inspect a workflow</button><button onclick="tab('answers',this)" aria-selected="false">Check the reference answers</button></nav></header><main>
<section id="overview"><h2>Every planned receiver episode retained</h2><p id="counts"></p><img src="figures/Figure_2_Results.svg" alt="Counts of supported source-task completion and archive requests for the two models and six policies."><div id="overviewtable" class="scroll"></div><p class="note">Twelve source tasks represent four mathematical structures. Six policies share upstream work within each model–task block. These are paired development comparisons, not 144 independent research studies or a general model ranking.</p></section>
<section id="trace" hidden><h2>Follow one actual research workflow</h2><div class="controls"><label>Model <select id="model" onchange="trace()"></select></label><label>Source task <select id="case" onchange="trace()"></select></label><label>Policy <select id="route" onchange="trace()"></select></label></div><div id="tracebody"></div></section>
<section id="answers" hidden><h2>Inspect answers and their mathematical limits</h2><p>Each source includes explicit assumptions and an exact population probability table. For a causal question with no identifying restriction, compatible worlds have the same observed probabilities but different causal effects.</p><label>Source task <select id="answercase" onchange="answer()"></select></label><div id="answerbody"></div></section>
<section><h2>Read and reproduce</h2><p><a href="Proposal.pdf">Revised proposal</a> · <a href="Technical_Supplement.pdf">Technical supplement</a> · <a href="README.md">Instructions</a> · <a href="workflow/results/episodes.csv">All 144 receiver episodes</a> · <a href="workflow/results/paired_contrasts.csv">Paired contrasts</a></p><p>From the extracted package: <code>python -B reproduce.py --out ../guardlab_workflow_reproduction_01</code>. No model account, network, private corpus, GPU or external Python package is required.</p><p class="note">This viewer contains reference answers for human review. Evaluated models must receive only their assigned packets. The original development pilots and their nulls remain in the historical release.</p></section></main><footer class="note">Synthetic data only · Model-generated programs were executed · Exact saved outputs are retained · Independent human methodological validation remains future work.</footer><script>
const D=__DATA__;
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function tab(id,b){for(let s of ['overview','trace','answers'])document.getElementById(s).hidden=s!==id;for(let x of document.querySelectorAll('nav button'))x.setAttribute('aria-selected',x===b?'true':'false')}
function opts(id,rows){let s=document.getElementById(id);rows.forEach(([v,t])=>{let o=document.createElement('option');o.value=v;o.textContent=t;s.appendChild(o)})}
opts('model',D.result.models.map(x=>[x,x]));opts('case',D.cases.map(c=>[c.case_id,c.case_id+' · '+c.family]));opts('answercase',D.cases.map(c=>[c.case_id,c.case_id+' · '+c.family]));opts('route',Object.entries(D.labels).map(([v,t])=>[v,t.split(String.fromCharCode(10)).join(' ')]));
function pre(x){return '<pre>'+esc(typeof x==='string'?x:JSON.stringify(x,null,2))+'</pre>'}
function trace(){let m=document.getElementById('model').value,id=document.getElementById('case').value,route=document.getElementById('route').value,t=D.traces[m+'|'+id],p=t.policies[route],up=t.upstream,c=D.cases.find(x=>x.case_id===id);document.getElementById('tracebody').innerHTML='<p>'+esc(c.commission)+'</p><div class="grid"><div><h3>1 · Analyst-generated program</h3>'+pre(up.analyst.python_code)+'<h3>2 · Execution and numerical review</h3>'+pre(route==='single_shared'?up.single_artifact:up.delegated_artifact)+'</div><div><h3>3 · Received supporting records</h3>'+pre(p.initial_records)+'<h3>4 · Initial interpreter action</h3>'+pre(p.episode.initial_decision)+(p.retrieval?'<h3>5 · Actual archive response</h3>'+pre(p.retrieval):'<p class="note">No archive record requested.</p>')+'<h3>Final scientific decision</h3>'+pre(p.episode.final_decision)+'</div></div><div class="result">Supported by received evidence: '+esc(p.scores.final_supported)+' · Supported source-task completion: '+esc(p.scores.source_completed)+'</div><details><summary>Inspect every score field</summary>'+pre(p.scores)+'</details><p><a href="'+esc(p.raw_path)+'">Open the exact saved episode</a></p>'}
function answer(){let c=D.cases.find(x=>x.case_id===document.getElementById('answercase').value);document.getElementById('answerbody').innerHTML='<h3>'+esc(c.commission)+'</h3><div class="grid"><div><h3>Exact population table</h3>'+pre(c.task.table)+'<h3>Design record</h3>'+pre(c.records[c.design_record_id])+'</div><div><h3>Full-source answer</h3>'+pre(c.source_key)+'<h3>Separate enumeration</h3>'+pre(c.reference_proof)+'</div></div><p><a href="workflow/evaluator/information_sets.json">Inspect all 24 full-source and missing-design reference regimes</a></p>'}
document.getElementById('counts').textContent=D.result.completed_episodes+' receiver episodes · '+D.result.source_analyses+' generated source analyses · '+D.result.physical_model_calls+' model calls · '+D.result.native_tool_violations+' native-tool violations.';
let fields=['model','route','n','final_supported','source_completed','archive_requests','final_unsupported_causal','final_safe_incomplete'];document.getElementById('overviewtable').innerHTML='<table><thead><tr>'+['Model','Policy','N','Supported','Completed','Requests','Unsupported causal','Safe incomplete'].map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+D.result.summary.map(r=>'<tr>'+fields.map(k=>'<td>'+esc(k==='route'?D.labels[r[k]].split(String.fromCharCode(10)).join(' '):r[k])+'</td>').join('')+'</tr>').join('')+'</tbody></table>';trace();answer();
</script></html>'''
    page=page.replace('workflow/results/paired_contrasts.csv','workflow/results/scientific_paired_contrasts.csv')
    page=page.replace('</style>','.grid>div{min-width:0}.controls label{min-width:0;max-width:100%}.controls select{display:block;width:100%}</style>')
    page=page.replace('<p class="note">Twelve source tasks represent four mathematical structures.','<p class="note">Scientific-answer counts recognize the actually received table field in a disclosed post-run audit. The frozen literal record-ID contract flagged ten population_table references; all ten flags and the original 134/144 composite result remain preserved. <a href="workflow/results/citation_audit.csv">Inspect the citation audit</a> · <a href="workflow/results/summary.csv">Inspect the original strict counts</a>.</p><p class="note">Twelve source tasks represent four mathematical structures.')
    (root/'index.html').write_text(page.replace('__DATA__',payload),encoding='utf-8')
    print('Workflow figures and offline viewer built.')

if __name__=='__main__':render(Path(__file__).resolve().parents[1])
