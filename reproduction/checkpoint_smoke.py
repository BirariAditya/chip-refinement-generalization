"""Run the unmodified official PPOAgent/checkpoint on a diagnostic mask state.

This validates native checkpoint execution, not circuit placement or paper metrics.
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    cli = parser.parse_args()
    source = cli.source.resolve()
    sys.path[:0] = [str(source / 'src'), str(source)]
    import numpy as np
    import torch
    import torchvision
    import yaml
    from agent import PPOAgent
    from utils.state_parsing import StateParsing

    with (source / 'config/default.yaml').open() as stream:
        config = yaml.safe_load(stream)
    config['device'] = 'cpu'
    config['use_cuda'] = False
    args = SimpleNamespace(**config)
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    checkpoint = source / 'policy/pretrained_model.pkl'
    print('Constructing original PPOAgent, including its original ImageNet ResNet initializer.', flush=True)
    agent = PPOAgent(args)
    agent.load_model(str(checkpoint))
    agent.eval()
    grid = args.grid
    zeros = np.zeros((grid, grid), dtype=np.float64)
    position = np.ones_like(zeros)
    position[5:195, 5:195] = 0
    state = StateParsing(args).get_state(
        place_idx=0, old_canvas=zeros.copy(), new_canvas=zeros.copy(),
        regular_mask=zeros.copy(), position_mask=position, wire_mask=zeros.copy(),
        next_regular_mask=zeros.copy(), next_position_mask=position.copy(),
        next_wire_mask=zeros.copy(), size_x=8, size_y=12)
    inputs = torch.from_numpy(state).float().unsqueeze(0)
    start = time.perf_counter()
    with torch.no_grad():
        probabilities = agent.actor(inputs)
        value = agent.critic(inputs)
    first_forward_seconds = time.perf_counter() - start
    action, log_probability = agent.select_action(state)
    repeat_action, _ = agent.select_action(state)
    x, y = divmod(action, grid)
    mask_mass = probabilities[0].reshape(grid, grid)[torch.from_numpy(position.astype(bool))].sum().item()
    assert torch.isfinite(probabilities).all().item()
    assert abs(probabilities.sum().item() - 1.0) < 1e-9
    assert position[x, y] == 0
    assert mask_mass == 0.0
    assert action == repeat_action
    result = {
        'scope': 'official_checkpoint_component_smoke_only',
        'input': 'synthetic diagnostic mask; no circuit benchmark',
        'upstream_url': 'https://github.com/lamda-bbo/macro-regulator',
        'source_commit': subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_diff': subprocess.check_output(['git', '-C', str(source), 'diff', '--stat'], text=True).strip(),
        'python': platform.python_version(), 'torch': torch.__version__,
        'torchvision': torchvision.__version__, 'numpy': np.__version__,
        'device': 'cpu', 'cuda_available': torch.cuda.is_available(),
        'cpu_threads': torch.get_num_threads(), 'seed': args.seed,
        'checkpoint_sha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        'checkpoint_bytes': checkpoint.stat().st_size,
        'strict_checkpoint_load': True, 'grid': grid, 'state_entries': state.size,
        'action_count': probabilities.numel(), 'probability_sum': probabilities.sum().item(),
        'probabilities_finite': True, 'masked_probability_mass': mask_mass,
        'selected_action': action, 'selected_grid_xy': [x, y],
        'selected_action_is_mask_legal': True, 'repeat_action_matches': True,
        'selected_action_log_probability': log_probability,
        'critic_value': value.item(), 'first_forward_seconds': first_forward_seconds,
        'placement_quality_measured': False, 'training_performed': False,
        'global_hpwl': None, 'routed_ppa': None,
    }
    cli.output.parent.mkdir(parents=True, exist_ok=True)
    cli.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
