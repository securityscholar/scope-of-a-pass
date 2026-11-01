from pathlib import Path
import json,csv,sys
from content_v2 import TITLE,SUBTITLE,REFERENCES,make_content
from supplement_content import appendix
from doc_tools import document,references,table,figure

def render(root):
    root=Path(root);r=json.loads((root/'workflow/results/reporting_results.json').read_text());proposal,reading=make_content(r);app=appendix(r,reading)
    words=len(' '.join(h+' '+' '.join(ps) for h,ps in proposal).split());assert 1500<=words<=2000,words
    d=document('Anonymous Stage 1 proposal · AI-Enabled Frontiers',TITLE)
    d.add_paragraph(TITLE,style='Title');d.add_paragraph(SUBTITLE,style='Subtitle')
    for h,ps in proposal:
        d.add_heading(h,level=1)
        for p in ps:d.add_paragraph(p)
    references(d,REFERENCES);d.save(root/'Proposal.docx')
    md=['# '+TITLE,'',SUBTITLE,'']
    for h,ps in proposal:md+=['## '+h,'']+sum(([p,''] for p in ps),[])
    md+=['## References','']+[t+' [Source]('+u+')\n' for t,u in REFERENCES]
    (root/'Proposal.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    d=document('Anonymous technical supplement · Workflow experiment W2',TITLE,11)
    d.add_paragraph('Technical supplement',style='Title');d.add_paragraph(TITLE+' · Executed workflow experiment W2',style='Subtitle')
    d.add_paragraph('Release: October 28, 2026. All data are synthetic. Prior development pilots remain separate and are preserved in the historical review object.')
    route_labels={'single_shared':'Single / shared transcript','delegated_full':'Delegated / complete records','delegated_selected':'Delegated / selected records','delegated_drop_general':'Dropped design / general','delegated_drop_scoped':'Dropped design / scoped','delegated_drop_reminder':'Dropped design / reminder'}
    for i,(h,ps) in enumerate(app):
        d.add_heading(h,level=1)
        for p in ps:d.add_paragraph(p)
        if i==3:
            table(d,'Table S1. Implemented workflow policies',['Policy','Information reaching interpreter','Verification communication'],[
            ['Single / shared transcript','Full original source, prior analysis and self-check','True numerical receipt; general heading'],
            ['Delegated / complete records','Full source, computed artifact and checker receipt','Same true numerical receipt'],
            ['Delegated / selected records','Commission, table, artifact, up to two analyst-selected records','Same true numerical receipt'],
            ['Dropped design / general','Selected record set after deliberate design-record removal','General pass heading'],
            ['Dropped design / scoped','Identical deliberate-removal packet','Numerical scope plus inferential caution'],
            ['Dropped design / reminder','Identical deliberate-removal packet','General heading plus identical separate caution']
            ],'Every policy permits one archive request. A failed computation is not labeled PASS. Natural record selection and deliberate removal are different interventions. The last two conditions share the same caution text; placement and heading differ.',[1.5,2.9,2.2])
        if i==6:
            for j,model in enumerate(r['models']):
                rs=[x for x in r['summary'] if x['model']==model]
                table(d,f'Table S{j+2}. Completed W2 receiver episodes: {model}, high reasoning',['Policy','N','Supported\nanswer','Source\ncompleted','Archive\nrequests','Unsupported\ncausal','Strict ID\nflags'],[[route_labels[x['route']],x['n'],x['final_supported'],x['source_completed'],x['archive_requests'],x['final_unsupported_causal'],x['strict_record_id_flags']] for x in rs],
                'Each row contains the same twelve source tasks: three per mathematical structure. The answer columns report scientific type/value support, with the disclosed post-run recognition of the received population_table field. Strict ID flags remain visible; the original composite counts are in workflow/results/summary.csv and the audit is in citation_audit.csv. All flags concern a supplied table field, not an unseen premise. Counts describe one trajectory per task/policy; no significance or token-budget equality is claimed.',[2.05,.35,.7,.8,.75,.95,1.0])
            calls=list(csv.DictReader((root/'workflow/results/model_calls.csv').open(encoding='utf-8')))
            upstream=list(csv.DictReader((root/'workflow/results/upstream.csv').open(encoding='utf-8')))
            rows=[]
            for m in r['models']:
                us=[x for x in upstream if x['model']==m];an=[x for x in us if x['checker_context']=='delegated'];cs=[x for x in calls if x['model']==m]
                rows.append([m,len(an),sum(x['analyst_program_ok']=='True' for x in an),sum(x['natural_design_selected']=='True' for x in an),sum(x['arithmetic_pass']=='True' for x in us),sum(x['code_revised']=='True' for x in us),len(cs)])
            table(d,'Table S4. Source analyses, numerical checks and physical model calls',['Configuration','Source\nanalyses','Programs\nexecuted','Design\nselected','Arithmetic\npassed','Code\nrevisions','Logical\ncalls'],rows,'Program and selection denominators are twelve per model. Arithmetic checks and possible code revisions have 24 checker-context opportunities per model. Calls count distinct executed logical stages; upstream stages are reused for the paired receiver policies. The READY access check and prior experiments are excluded.',[1.8,.6,.7,.7,.9,.7,.7])
        if i==8:
            table(d,'Table S5. Nearest alternatives and the specific contribution boundary',['Prior capability','Existing contribution','Focus of this instrument'],[
            ['CLadder','Formal causal questions and reference answers','Identification indexed to information received during a research workflow'],
            ['Scientific gates and verifier benchmarks','Output-release controls and research-error detection','Correct numerical artifacts whose inferential support can change'],
            ['MAST; architecture comparisons','Multi-agent failure analysis and single-agent baselines','Separate scientific support, task completion and evidence requests'],
            ['ClaimArena-LLM','Structured causal propositions, provenance and adversarial influence','Exact effects and nonidentification witnesses; methodological-record retrieval'],
            ['Coordinated scientific-inference workflows','Scientific evidence integration with explicit comparators','Generated boundaries whose mathematical answers and non-answers are inspectable']
            ],'This mapping states the proposed distinction; it does not establish firstness or a general empirical advantage. See the references and the machine-readable paired contrasts.',[1.35,2.45,2.8])
    p=d.add_heading('Figures',level=1);p.paragraph_format.page_break_before=True
    figure(d,'Figure 1. Executed workflow, record policies and evidence recovery',root/'figures/Figure_1_Workflow.png','Models generate the arithmetic program, numerical review, record selection and scientific decision. The host executes arithmetic, constructs the actual receipt, transfers the assigned records and returns a source record on request. Gold answers are used only by the external evaluator. Shared upstream artifacts support matched policy comparisons; they do not create independent source studies.')
    figure(d,'Figure 2. Supported completion and archive requests in the fixed W2 task set',root/'figures/Figure_2_Results.png','Cells report counts out of twelve tasks per model/policy, recognizing the actually received table field in the disclosed post-run audit. Strict identifier flags remain in Tables S2–S3 and the original result files. The policies share source analyses within model–case blocks. Retrieval is an observed action; a final correct answer does not imply the identifying evidence was received initially. Natural record choice and intentional removal remain separate. The figure does not establish population-level reliability or equivalence.')
    references(d,REFERENCES);d.save(root/'Technical_Supplement.docx')
    md=['# Technical supplement','',TITLE+' · Workflow experiment W2','']
    for h,ps in app:md+=['## '+h,'']+sum(([p,''] for p in ps),[])
    md+=['## Tables and figures','','Formatted DOCX/PDF includes Tables S1–S5 and Figures 1–2. All episode-level and paired counts are available in workflow/results/.','','## References','']+[t+' [Source]('+u+')\n' for t,u in REFERENCES]
    (root/'Technical_Supplement.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    abstract=('A correct computational result can reach an AI interpreter without the evidence that licenses its scientific use. We propose Guard Lab, an executable laboratory that separately evaluates support for a conclusion under received information and completion of the original research task. Exact population estimands and observationally equivalent potential-outcome populations make both point answers and justified non-answers inspectable. An executed workflow experiment uses two capable model configurations, generated arithmetic programs, numerical peer review, record selection and optional source retrieval. Its 144 receiver episodes compare a shared-transcript researcher, complete delegated records, analyst-selected records and three deliberate-loss policies. Both configurations preserved the design record in every natural handoff and retrieved it for every causal question after deliberate removal. All final scientific answers were warranted; scoped verification supplied no observed advantage. Ten literal citation-ID mismatches remain separately reported with a disclosed post-run audit. The development program will extend the mathematical structures and research environments to identify which information and verification policies preserve useful, warranted inference across AI research production.')
    (root/'Portal_Abstract.txt').write_text(abstract+'\n',encoding='utf-8')
    (root/'BUILD_INVENTORY.json').write_text(json.dumps(dict(proposal_words_including_headings=words,abstract_words=len(abstract.split()),technical_tables=5,figures=2,workflow_receiver_episodes=144,model_calls=r['physical_model_calls'],independent_human_audit_completed=False),indent=2)+'\n')
    print(json.dumps(dict(proposal_words=words,abstract_words=len(abstract.split()))))

if __name__=='__main__':render(Path(__file__).resolve().parents[1])
