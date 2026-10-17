"""Execute official parser, masks, environment steps and policy on superblue18.

This component experiment skips unavailable DREAMPlace initialization/evaluation.
It is not a reproduction of the paper's global HPWL or routed PPA experiment.
No vendor source is edited. A fail-fast import shim isolates the unused backend.
"""
import argparse
import copy
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
import types
from pathlib import Path
from types import SimpleNamespace


def json_text(value):
    return json.dumps(value, indent=2, default=lambda x: x.item())+'\n'


def geometry(positions, grid):
    entries = list(positions.items())
    overlaps = []
    outside = []
    area = 0
    for i, (name, (x, y, w, h)) in enumerate(entries):
        area += w*h
        if x < 0 or y < 0 or x+w > grid or y+h > grid:
            outside.append(name)
        for other, (u, v, a, b) in entries[i+1:]:
            if max(x, u) < min(x+w, u+a) and max(y, v) < min(y+h, v+b):
                overlaps.append([name, other])
    return {'out_of_bounds_count': len(outside), 'overlap_pair_count': len(overlaps),
            'rectangle_area_fraction': area/(grid*grid),
            'legal_rectangle_geometry': not outside and not overlaps}


def independent_hpwl(problem, positions):
    total = 0.0
    for net in problem.net_info.values():
        pins = []
        for name, offset in net['nodes'].items():
            if name in positions:
                x, y, _, _ = positions[name]
                pins.append((x*problem.ratio_x + problem.node_info[name]['x']/2 + offset['x_offset'],
                             y*problem.ratio_y + problem.node_info[name]['y']/2 + offset['y_offset']))
        for name in net['ports']:
            pins.append((problem.port_info[name]['x'], problem.port_info[name]['y']))
        if len(pins) > 1:
            total += net.get('weight', 1.0) * (
                max(p[0] for p in pins)-min(p[0] for p in pins)
                + max(p[1] for p in pins)-min(p[1] for p in pins))
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--benchmark', default='superblue18')
    parser.add_argument('--canvas-mode', choices=['native', 'full'], default='native')
    cli = parser.parse_args()
    source = cli.source.resolve()
    output = cli.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(source/'src'), str(source)]
    import gym
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import numpy as np
    import torch
    import yaml

    # This shim deliberately cannot run a backend. It only permits importing
    # the unchanged ProblemInstance class to run its original parser/setup.
    unavailable = types.ModuleType('place_env.dmp_caller')
    class UnavailableDMPcaller:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('DREAMPlace deliberately unavailable in component experiment')
    unavailable.DMPcaller = UnavailableDMPcaller
    sys.modules['place_env.dmp_caller'] = unavailable
    from problem_instance import ProblemInstance
    from place_env.place_env import PlaceEnv
    from agent import PPOAgent
    from utils.state_parsing import StateParsing
    from utils.comp_res import comp_res

    config = yaml.safe_load((source/'config/default.yaml').read_text())
    config.update(device='cpu', use_cuda=False, ROOT_DIR=str(source),
                  BENCHMARK_DIR=str(source/'benchmark'), use_reward_scaling=False)
    args = SimpleNamespace(**config)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(4)
    parse_start = time.perf_counter()
    print('Parsing authentic benchmark with unmodified ProblemInstance...', flush=True)
    problem = ProblemInstance(args, cli.benchmark)
    parse_seconds = time.perf_counter()-parse_start
    original_place_grid = problem.place_grid
    # Native is the paper implementation's compressed canvas. Full is a
    # separately labeled diagnostic, never silently substituted for native.
    canvas = original_place_grid if cli.canvas_mode == 'native' else args.grid
    problem.place_grid = canvas
    reference = copy.deepcopy(problem.macro_pos)
    print('Parsed', problem.node_cnt, 'selected modules,', problem.net_cnt, 'selected nets;',
          'compressed/full grid:', original_place_grid, args.grid, flush=True)

    # Reproduce the native environment fields used by reset/step, while
    # bypassing __init__'s mandatory DREAMPlace initialization and file copying.
    env = PlaceEnv.__new__(PlaceEnv)
    env.args = args
    env.grid = args.grid
    env.place_grid = canvas
    env.action_space = gym.spaces.Discrete(args.grid*args.grid)
    env.observation_space = gym.spaces.Discrete(3+8*args.grid*args.grid)
    env.problem_train = [problem]
    env.problem_eval = [problem]
    env.n_macro = args.n_macro
    env.place_idx = 0
    env.old_macro_pos = {}
    env.new_macro_pos = {}
    env.macro_to_place = []
    env.macro_placed = []
    env.state_parsing = StateParsing(args)
    env.test_mode = False
    env.wire_reward_max, env.wire_reward_min = -1e12, 1e12
    env.regular_reward_max, env.regular_reward_min = -1e12, 1e12
    env.reward_scaling_flag = False

    # Greedy nearest-reference legalizer is explicit new harness preprocessing,
    # not a substitute claimed to reproduce DREAMPlace's starting placement.
    repair_start = time.perf_counter()
    xx, yy = np.indices((args.grid, args.grid))
    for name in problem.node_id_to_name:
        x, y, w, h = reference[name]
        mask = env.get_position_mask(w, h)
        cost = abs(xx-x)+abs(yy-y)
        cost = np.where(mask == 0, cost, np.inf)
        if not np.isfinite(cost).any():
            raise RuntimeError('Nearest-site reference repair failed: no legal site')
        a = int(np.argmin(cost))
        u, v = divmod(a, args.grid)
        env.new_macro_pos[name] = (u, v, w, h)
        env.macro_placed.append(name)
    start_positions = copy.deepcopy(env.new_macro_pos)
    repair_seconds = time.perf_counter()-repair_start
    assert geometry(start_positions, canvas)['legal_rectangle_geometry']
    problem.macro_pos = copy.deepcopy(start_positions)
    agent = PPOAgent(args)
    checkpoint = source/'policy/pretrained_model.pkl'
    agent.load_model(str(checkpoint))
    agent.eval()

    def metrics(positions):
        h, regularity = comp_res(problem, positions, problem.ratio_x, problem.ratio_y, canvas)
        independent = independent_hpwl(problem, positions)
        return dict(geometry(positions, canvas), upstream_macro_hpwl=h,
                    independent_macro_hpwl=independent,
                    hpwl_implementations_agree=abs(h-independent) <= 1e-7*max(1.,abs(h)),
                    upstream_regularity=regularity)

    def rollout(mode):
        problem.macro_pos = copy.deepcopy(start_positions)
        state = env.reset(test_mode=False, benchmark=cli.benchmark, reward_scaling_flag=False)
        # Native test_mode=False skips DREAMPlace on episode completion;
        # the neural policy remains in evaluation mode with frozen weights.
        rows, total_reward = [], 0.0
        started = time.perf_counter()
        for step in range(len(start_positions)):
            if mode == 'official_pretrained':
                action, _ = agent.select_action(state)
            else:
                wire = env.state_parsing.state2wire_mask(state)
                regular = env.state_parsing.state2regular_mask(state)
                legal = env.state_parsing.state2position_mask(state) == 0
                cost = args.wire_coeff*wire+(1-args.wire_coeff)*regular
                action = int(np.argmin(np.where(legal, cost, np.inf)))
            next_state, reward, done, info = env.step(action)
            total_reward += float(reward)
            rows.append({'step': step, 'action': action, 'reward': float(reward),
                         'legal_penalty': float(info['legal_reward'])})
            state = next_state
            if step % 64 == 0 or done:
                print(mode, 'step', step+1, 'elapsed', round(time.perf_counter()-started,2), flush=True)
            if done:
                break
        elapsed = time.perf_counter()-started
        positions = copy.deepcopy(env.new_macro_pos)
        result = metrics(positions)
        result.update(steps=len(rows), complete_pass=bool(done),
                      pass_seconds=elapsed, total_raw_proxy_reward=total_reward,
                      illegal_action_penalties=sum(r['legal_penalty'] != 0 for r in rows))
        assert result['complete_pass']
        assert result['legal_rectangle_geometry']
        assert result['illegal_action_penalties'] == 0
        (output/(mode+'_actions.json')).write_text(json_text(rows))
        (output/(mode+'_result.json')).write_text(json_text(result))
        (output/(mode+'_positions.json')).write_text(json_text(positions))
        return result, positions

    reference_metrics = metrics(reference)
    initial_metrics = metrics(start_positions)
    (output/'initial_metrics.json').write_text(json_text({
        'canvas_mode': cli.canvas_mode, 'place_grid': canvas,
        'raw_reference_grid': reference_metrics, 'legal_start': initial_metrics}))
    learned_metrics, learned_positions = rollout('official_pretrained')
    greedy_metrics, greedy_positions = rollout('matched_mask_greedy')
    for m in (learned_metrics, greedy_metrics):
        m['macro_hpwl_gain_percent_vs_legal_start'] = 100*(
            initial_metrics['independent_macro_hpwl']-m['independent_macro_hpwl'])/initial_metrics['independent_macro_hpwl']
    result = {
        'scope': 'real_circuit_original_policy_and_environment_component_experiment',
        'not_full_paper_reproduction': True,
        'source_commit': subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),
        'source_tracked_diff': subprocess.check_output(['git','-C',str(source),'diff','--stat'],text=True).strip(),
        'benchmark': cli.benchmark, 'selected_modules': problem.node_cnt,
        'selected_macro_nets': problem.net_cnt, 'full_def_instances': len(problem.database['nodes']),
        'selected_module_definition': 'upstream largest 512 instances by area',
        'checkpoint_training_designs': ['superblue1','superblue3','superblue4','superblue5'],
        'checkpoint_sha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        'seed': args.seed, 'pythonhashseed': os.environ.get('PYTHONHASHSEED'),
        'device': 'cpu', 'torch_threads': torch.get_num_threads(),
        'python': platform.python_version(), 'torch': torch.__version__,
        'parse_seconds': parse_seconds, 'repair_seconds': repair_seconds,
        'original_compressed_place_grid': original_place_grid,
        'component_place_grid': canvas, 'canvas_mode': cli.canvas_mode,
        'hpwl_units': 'upstream scaled coordinates; macro/port subgraph only, not global HPWL',
        'deviations': [
            'DREAMPlace import isolated with a fail-fast shim; backend never called',
            'PlaceEnv constructor backend work bypassed; original reset/step/masks are unchanged',
            ('Native compressed outline retained' if cli.canvas_mode == 'native' else
             'Diagnostic full 224-grid outline instead of native compressed outline'),
            'Nearest-reference grid legalization replaces unavailable DREAMPlace initialization',
            'Reward scaling disabled; no policy update, action masks retain original normalization',
            'Environment test_mode=False only to suppress backend evaluation; agent.eval() remains frozen',
        ],
        'raw_reference_grid': reference_metrics, 'legal_start': initial_metrics,
        'official_pretrained': learned_metrics, 'matched_mask_greedy': greedy_metrics,
        'training_performed': False, 'global_hpwl': None, 'congestion': None, 'routed_ppa': None,
        'rectangle_legality_only': True,
    }
    (output/'real_circuit_component.json').write_text(json_text(result))
    (output/'real_circuit_positions.json').write_text(json_text({
        'raw_reference': reference, 'legal_start': start_positions,
        'official_pretrained': learned_positions, 'matched_mask_greedy': greedy_positions}))
    fig, axes = plt.subplots(1,3,figsize=(13,4.6))
    for ax, positions, title in zip(axes,[start_positions,learned_positions,greedy_positions],
                                   ['Legalized reference start','Official frozen policy','Matched-mask greedy']):
        for x,y,w,h in positions.values():
            ax.add_patch(Rectangle((x,y),w,h,facecolor='#2c6eab',edgecolor='#123450',linewidth=.2,alpha=.75))
        ax.set(xlim=(0,canvas),ylim=(0,canvas),aspect='equal',title=title,xlabel='Grid x',ylabel='Grid y')
    fig.suptitle('superblue18: original mask/policy component execution; no DREAMPlace or routing',fontsize=11)
    fig.tight_layout()
    fig.savefig(str(output/'real_circuit_macro_pass.png'),dpi=140)
    print(json_text(result),flush=True)


if __name__ == '__main__':
    main()
