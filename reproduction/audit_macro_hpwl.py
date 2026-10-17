"""Diagnose upstream macro-HPWL versus direct extrema on saved real placements.

This concerns utils.comp_res only, not DREAMPlace global HPWL or paper PPA.
"""
import argparse
import csv
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--artifact-dir', type=Path, required=True)
    cli = p.parse_args()
    source = cli.source.resolve()
    sys.path[:0] = [str(source/'src'), str(source)]
    import yaml
    backend = types.ModuleType('place_env.dmp_caller')
    class UnavailableBackend:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('No backend is available in this metric audit')
    backend.DMPcaller = UnavailableBackend
    sys.modules['place_env.dmp_caller'] = backend
    from problem_instance import ProblemInstance
    from utils.comp_res import comp_res

    config = yaml.safe_load((source/'config/default.yaml').read_text())
    config.update(BENCHMARK_DIR=str(source/'benchmark'))
    problem = ProblemInstance(SimpleNamespace(**config), 'superblue18')
    phases = json.loads((cli.artifact_dir/'real_circuit_positions.json').read_text())
    summary, rows = {}, []
    for phase, positions in phases.items():
        independent_total, native_total, omitted_total = 0., 0., 0.
        omitted, mismatched, negative = 0, 0, 0
        for name, net in problem.net_info.items():
            points = []
            for node, offset in net['nodes'].items():
                x,y,_,_ = positions[node]
                points.append((x*problem.ratio_x+problem.node_info[node]['x']/2+offset['x_offset'],
                               y*problem.ratio_y+problem.node_info[node]['y']/2+offset['y_offset']))
            for port in net['ports']:
                points.append((problem.port_info[port]['x'],problem.port_info[port]['y']))
            xs, ys = [v[0] for v in points], [v[1] for v in points]
            weight = net.get('weight',1.)
            exact = weight*(max(xs)-min(xs)+max(ys)-min(ys))
            native_min_x = min([problem.max_height*1.1]+xs)
            included = native_min_x <= problem.max_height
            native = weight*(max([0.]+xs)-native_min_x
                +max([0.]+ys)-min([problem.max_height*1.1]+ys)) if included else 0.
            independent_total += exact
            native_total += native
            if not included:
                omitted += 1
                omitted_total += exact
            mismatched += abs(native-exact) > 1e-8
            negative += any(v < 0 for v in xs+ys)
            rows.append(dict(phase=phase,net=name,true_hpwl=exact,native_hpwl=native,
                             dropped_by_native_x_threshold=not included,min_x=min(xs),
                             max_x=max(xs),min_y=min(ys),max_y=max(ys)))
        official_h, _ = comp_res(problem, positions, problem.ratio_x, problem.ratio_y, problem.place_grid)
        summary[phase] = {
            'independent_true_extrema_hpwl': independent_total,
            'upstream_comp_res_hpwl': float(official_h),
            'recomputed_native_formula_hpwl': native_total,
            'native_formula_reproduction_agrees': abs(native_total-official_h)<1e-6,
            'nets_dropped_by_x_threshold': omitted,
            'dropped_net_true_hpwl_sum': omitted_total,
            'nets_with_differing_hpwl': mismatched,
            'nets_with_negative_coordinates': negative,
            'total_difference': independent_total-native_total,
            'difference_explained_by_dropped_nets': abs(independent_total-native_total-omitted_total)<1e-6,
        }
    result = {
        'scope':'macro-subgraph reporting metric only; not DREAMPlace global HPWL',
        'max_width':problem.max_width,'max_height':problem.max_height,
        'selected_nets':problem.net_cnt,
        'cause':'comp_res initializes min_x from max_height and includes a net only if min_x <= max_height',
        'policy_algorithm_modified':False,'phases':summary,
    }
    serialized = json.dumps(result,indent=2,default=lambda x:x.item())
    (cli.artifact_dir/'macro_hpwl_audit.json').write_text(serialized+'\n')
    with (cli.artifact_dir/'macro_hpwl_per_net.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(serialized,flush=True)


if __name__ == '__main__':
    main()
