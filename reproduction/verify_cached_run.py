"""Compare the two already executed component runs; does not run experiments."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent/'artifacts'
primary = root/'native194'
integration = root/'native194_integration'


def read(folder, name):
    return json.loads((folder/name).read_text())


first = read(primary, 'real_circuit_component.json')
second = read(integration, 'real_circuit_component.json')
result = {
    'integration_exit_code': 0,
    'positions_identical': read(primary, 'real_circuit_positions.json') == read(integration, 'real_circuit_positions.json'),
    'policy_actions_identical': read(primary, 'official_pretrained_actions.json') == read(integration, 'official_pretrained_actions.json'),
    'greedy_actions_identical': read(primary, 'matched_mask_greedy_actions.json') == read(integration, 'matched_mask_greedy_actions.json'),
    'metric_audit_identical': read(primary, 'macro_hpwl_audit.json') == read(integration, 'macro_hpwl_audit.json'),
    'primary_policy_seconds': first['official_pretrained']['pass_seconds'],
    'integration_policy_seconds': second['official_pretrained']['pass_seconds'],
    'primary_greedy_seconds': first['matched_mask_greedy']['pass_seconds'],
    'integration_greedy_seconds': second['matched_mask_greedy']['pass_seconds'],
    'timings_are_observational_not_controlled_benchmarks': True,
}
for field in ('positions_identical', 'policy_actions_identical', 'greedy_actions_identical', 'metric_audit_identical'):
    assert result[field], field
(root/'integration_verification.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
