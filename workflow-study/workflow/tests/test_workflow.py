from pathlib import Path
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from workflow import *
from prepare_experiment import build_cases

OBS="n1 = sum(r['weight'] for r in rows if r['x'] == 1)\nn0 = sum(r['weight'] for r in rows if r['x'] == 0)\nestimate = Fraction(sum(r['weight']*r['y'] for r in rows if r['x']==1),n1)-Fraction(sum(r['weight']*r['y'] for r in rows if r['x']==0),n0)"
STD="zs = sorted(set(r['z'] for r in rows))\ntotal = sum(r['weight'] for r in rows)\nestimate = sum(Fraction(sum(r['weight'] for r in rows if r['z']==z),total)*(Fraction(sum(r['weight']*r['y'] for r in rows if r['z']==z and r['x']==1),sum(r['weight'] for r in rows if r['z']==z and r['x']==1))-Fraction(sum(r['weight']*r['y'] for r in rows if r['z']==z and r['x']==0),sum(r['weight'] for r in rows if r['z']==z and r['x']==0))) for z in zs)"

class Arithmetic(unittest.TestCase):
    def test_generated_programs_agree_with_separate_public_calculator(self):
        for c in build_cases():
            label='standardized_difference' if c['family']=='observational_adjusted' else 'observed_difference';r=execute(STD if label.startswith('standard') else OBS,c['task']['table']);self.assertTrue(r['ok'],r);self.assertAlmostEqual(float(calculate(c['task']['table'],label)),r['value'],places=12)
    def test_io_attributes_imports_and_statement_loops_are_rejected(self):
        for code in ["import os\nestimate=0", "estimate=open('x')", "estimate=rows.__class__",'while True: pass','estimate=2**1000000','rows[0]=0\nestimate=0']:
            self.assertFalse(execute(code,[dict(x=0,y=0,weight=1)])['ok'])
    def test_bad_numbers_and_bools_rejected(self):
        for code in ['estimate=True','estimate=2','estimate=Fraction(1,0)']:
            self.assertFalse(execute(code,[])['ok'])
    def test_checker_repairs_are_executed_not_just_described(self):
        c=build_cases()[0];a=dict(python_code='estimate=0',analysis_label='observed_difference',proposed_answer_type='association');built=make_artifact(c,a,{},dict(verdict='revise',replacement_code=OBS));self.assertTrue(built['arithmetic_pass']);self.assertTrue(built['code_revised'])
    def test_checker_cannot_pass_incorrect_arithmetic_by_assertion(self):
        c=next(c for c in build_cases() if c['source_key']['answer']['value'] not in (None,0));built=make_artifact(c,dict(python_code='estimate=0',analysis_label='observed_difference'),{},dict(verdict='pass',replacement_code=None));self.assertEqual('FAIL',built['receipt']['status'])

class InformationAccounting(unittest.TestCase):
    def setup_case(self,family='randomized'):
        c=next(c for c in build_cases() if c['family']==family);a=dict(handoff_record_ids=[c['design_record_id']],python_code=OBS,analysis_label='observed_difference',proposed_answer_type=c['source_key']['answer']['answer_type']);built=make_artifact(c,a,{},dict(verdict='pass',replacement_code=None));return c,a,built
    def test_natural_selection_transfers_record_verbatim(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_selected');self.assertEqual(c['records'][c['design_record_id']],p['received_supporting_records'][c['design_record_id']])
    def test_stress_removes_only_design_not_table_or_receipt(self):
        c,a,b=self.setup_case();natural=route_packet(c,a,b,'delegated_selected');stress=route_packet(c,a,b,'delegated_drop_general');self.assertNotIn(c['design_record_id'],stress['received_supporting_records']);self.assertEqual(natural['population_table'],stress['population_table']);self.assertEqual(natural['verification_record'],stress['verification_record'])
    def test_correct_source_value_is_unsupported_without_design(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_drop_general');answer=dict(c['source_key']['answer'],action='finalize',evidence_ids=[],brief_rationale='');s=score(c,p,answer,c['source_key']);self.assertTrue(s['unsupported_causal_claim']);self.assertFalse(s['source_task_completed'])
    def test_safe_incomplete_answer_is_not_called_unsupported(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_drop_general');d=dict(task_id=c['case_id'],action='finalize',answer_type='not_identified',value=None,evidence_ids=[],brief_rationale='');s=score(c,p,d,c['source_key']);self.assertTrue(s['scientifically_supported']);self.assertTrue(s['safe_but_incomplete']);self.assertFalse(s['unsupported_causal_claim'])
    def test_retrieval_restores_premise_but_returns_no_key(self):
        c,a,b=self.setup_case();p=retrieve(c,route_packet(c,a,b,'delegated_drop_general'));self.assertEqual(c['source_key']['answer'],available_key(c,p)[0]['answer']);self.assertNotIn('source_key',json.dumps(p));self.assertNotIn('compatible_worlds',json.dumps(p))
    def test_missing_design_does_not_block_descriptive_answer(self):
        c,a,b=self.setup_case('descriptive');p=route_packet(c,a,b,'delegated_drop_general');self.assertEqual('association',available_key(c,p)[0]['answer']['answer_type'])
    def test_retrieval_does_not_manufacture_identification(self):
        c,a,b=self.setup_case('observational_unidentified');p=retrieve(c,route_packet(c,a,b,'delegated_drop_general'));self.assertEqual('not_identified',available_key(c,p)[0]['answer']['answer_type'])
    def test_scoped_and_separate_reminder_share_exact_guidance(self):
        c,a,b=self.setup_case();s=route_packet(c,a,b,'delegated_drop_scoped');r=route_packet(c,a,b,'delegated_drop_reminder');self.assertIn(r['separate_method_reminder'],s['verification_message']);self.assertEqual(s['received_supporting_records'],r['received_supporting_records'])
    def test_model_inputs_do_not_contain_latent_worlds_or_answer_key(self):
        c,a,b=self.setup_case();alltext=analyst_prompt(c)+checker_prompt(c,a,{},False)+decision_prompt(route_packet(c,a,b,'single_shared'), 'single_shared');self.assertNotIn('source_key',alltext);self.assertNotIn('generating_world',alltext);self.assertNotIn('compatible_worlds',alltext)
    def test_shared_transcript_keeps_source(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'single_shared');self.assertEqual(source_packet(c),p['shared_transcript']['original_source'])
    def test_unsupported_evidence_reference_is_not_silently_accepted(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_full');d=dict(c['source_key']['answer'],action='finalize',evidence_ids=['invented'],brief_rationale='');self.assertFalse(score(c,p,d,c['source_key'])['scientifically_supported'])
if __name__=='__main__':unittest.main()
