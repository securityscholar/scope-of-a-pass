import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_experiment import build_cases
from workflow import route_packet,make_artifact,retrieve
from audit_citations import audit_one

class CitationAudit(unittest.TestCase):
    def setup_case(self):
        c=next(c for c in build_cases() if c['family']=='randomized');a=dict(handoff_record_ids=[c['design_record_id']],python_code='estimate=0',analysis_label='observed_difference',proposed_answer_type='causal_effect');b=make_artifact(c,a,{},dict(verdict='pass',replacement_code=None));return c,a,b
    def test_visible_table_alias_keeps_strict_flag_and_recovers_valid_answer(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_full');d=dict(c['source_key']['answer'],action='finalize',evidence_ids=[c['design_record_id'],'population_table']);r=audit_one(c,p,d);self.assertTrue(r['strict_id_flag']);self.assertFalse(r['strict_supported']);self.assertTrue(r['audited_supported'])
    def test_unknown_source_identifier_is_never_forgiven(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_full');d=dict(c['source_key']['answer'],action='finalize',evidence_ids=['invented','population_table']);self.assertFalse(audit_one(c,p,d)['audited_supported'])
    def test_alias_does_not_supply_missing_identification(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_drop_general');d=dict(c['source_key']['answer'],action='finalize',evidence_ids=['population_table']);self.assertFalse(audit_one(c,p,d)['audited_supported'])
    def test_unreceived_real_record_is_not_a_valid_alias(self):
        c,a,b=self.setup_case();p=route_packet(c,a,b,'delegated_drop_general');d=dict(c['source_key']['answer'],action='finalize',evidence_ids=[c['design_record_id']]);r=audit_one(c,p,d);self.assertIn(c['design_record_id'],r['unreceived_references']);self.assertFalse(r['audited_source_completed'])
if __name__=='__main__':unittest.main()
