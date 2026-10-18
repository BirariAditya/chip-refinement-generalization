import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
import torch
from objectives import NAMES, ProxyDesign, initial_layout, preferences, hypervolume, nondominated
from ppo import Policy, train, rollout


def write_json(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'results'/'submission_pilot')
    parser.add_argument('--specialist-episodes',type=int,default=16)
    parser.add_argument('--ablation-episodes',type=int,default=64)
    parser.add_argument('--seeds',type=int,nargs='+',default=[17,29,43])
    args=parser.parse_args()
    if args.specialist_episodes<1 or args.ablation_episodes<1:
        raise ValueError('Positive episode budgets required')
    out=args.output
    out.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(1)
    weights=preferences()
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    protocol={'label':'synthetic CPU pilot, not industrial E1-E7 completion',
              'training_designs':list(range(101,109)),'held_out_designs':[301,302,303,304],
              'test_start_seeds':[8001,8002],'test_initializers':['uniform'],
              'objectives':NAMES,'preferences':weights.tolist(),'seeds':args.seeds,
              'specialist_episodes_each':args.specialist_episodes,
              'conditioned_episodes':len(weights)*args.specialist_episodes,
              'ablation_episodes':args.ablation_episodes,'gamma':1,'gae_lambda':.95,
              'ppo_clip':.2,'ppo_epochs':4,'batch_episodes':8,'learning_rate':.0003,
              'hypervolume_reference':[2,2,2,2],'normalization_floor':[1,1,.1,.1],
              'checkpoint_selection':'last fixed-budget checkpoint; no test-based selection',
              'budget_match':'35-specialist union and each conditioned model have equal total training transitions',
              'missing_metrics':{'WNS':None,'TNS':None,'violating_paths':None,'routed_wirelength':None,'routing_overflow':None},
              'source_sha256':source_hashes,'python':platform.python_version(),'torch':torch.__version__,
              'numpy':np.__version__,'platform':platform.platform()}
    protocol_file=out/'protocol.json'
    if protocol_file.exists() and json.loads(protocol_file.read_text())!=protocol:
        raise RuntimeError('Output contains a different protocol. Use a new output directory.')
    write_json(protocol_file,protocol)
    metadata=[]
    records=[]
    cases=[(s,k,ProxyDesign.synthetic(s)) for s in protocol['held_out_designs'] for k in protocol['test_start_seeds']]
    begin=time.perf_counter()
    for seed in args.seeds:
        specs=[('base',args.ablation_episodes,[.7,.3,0,0],'path',False),
               ('timing',args.ablation_episodes,[.5,.2,.3,0],'path',False),
               ('critical_net',args.ablation_episodes,[.5,.2,.3,0],'critical_net',False),
               ('congestion',args.ablation_episodes,[.5,.2,0,.3],'path',False),
               ('conditioned',len(weights)*args.specialist_episodes,None,'path',False),
               ('chebyshev',len(weights)*args.specialist_episodes,None,'path',True)]
        specs += [('specialist_%02d'%i,args.specialist_episodes,w.tolist(),'path',False) for i,w in enumerate(weights)]
        for name,episodes,fixed,timing,cheb in specs:
            folder=out/('seed_%d'%seed)
            folder.mkdir(exist_ok=True)
            checkpoint=folder/(name+'.pt')
            meta_file=folder/(name+'.json')
            if checkpoint.exists() and meta_file.exists():
                policy=Policy()
                policy.load_state_dict(torch.load(str(checkpoint),map_location='cpu'))
                meta=json.loads(meta_file.read_text())
            else:
                print('TRAIN seed=%d model=%s episodes=%d'%(seed,name,episodes),flush=True)
                policy,meta=train(seed,episodes,fixed,timing,cheb)
                torch.save(policy.state_dict(),str(checkpoint))
                write_json(meta_file,meta)
            policy.eval()
            meta=dict(meta,model=name,checkpoint=str(checkpoint.resolve()))
            metadata.append(meta)
            eval_weights=weights if fixed is None else np.asarray([fixed])
            for design_seed,start_seed,design in cases:
                start=initial_layout(design.circuit,start_seed,'uniform')
                for wi,w in enumerate(eval_weights):
                    _,record=rollout(policy,design,start,w,timing_mode=timing,chebyshev=cheb)
                    record.update(model=name,seed=seed,design_seed=design_seed,start_seed=start_seed,preference=w.tolist())
                    records.append(record)
            write_json(out/'training.json',metadata)
            write_json(out/'runs.json',records)
            print('DONE seed=%d model=%s training=%.2fs evals=%d'%(seed,name,meta['seconds'],len(cases)*len(eval_weights)),flush=True)
    for method in ['identity','greedy']:
        for design_seed,start_seed,design in cases:
            start=initial_layout(design.circuit,start_seed,'uniform')
            for w in weights:
                _,record=rollout(None,design,start,w,control=method)
                record.update(model=method,seed=None,design_seed=design_seed,start_seed=start_seed,preference=w.tolist())
                records.append(record)
    write_json(out/'runs.json',records)
    set_rows=[]
    for seed in args.seeds+[None]:
        methods=['conditioned','chebyshev','specialists'] if seed is not None else ['identity','greedy']
        for method in methods:
            for design_seed,start_seed,_ in cases:
                subset=[r for r in records if r['seed']==seed and r['design_seed']==design_seed and r['start_seed']==start_seed
                        and ((r['model'].startswith('specialist_')) if method=='specialists' else r['model']==method)]
                values=np.array([r['normalized'] for r in subset])
                set_rows.append({'model':method,'seed':seed,'design_seed':design_seed,'start_seed':start_seed,
                                 'candidates':len(subset),'nondominated':len(nondominated(values)),
                                 'outside_reference':int(np.any(values>=2,axis=1).sum()),
                                 'hypervolume':hypervolume(values,[2,2,2,2])})
    write_json(out/'sets.json',set_rows)
    with (out/'sets.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(set_rows[0]))
        writer.writeheader();writer.writerows(set_rows)
    summary={}
    for method in ['identity','greedy','specialists','conditioned','chebyshev']:
        subset=[r for r in set_rows if r['model']==method]
        means=[float(np.mean([r['hypervolume'] for r in subset if r['design_seed']==s])) for s in protocol['held_out_designs']]
        summary[method]={'mean_hypervolume':float(np.mean(means)),
                         'std_across_four_design_means':float(np.std(means,ddof=1)),
                         'mean_nondominated':float(np.mean([r['nondominated'] for r in subset])),
                         'outside_reference_count':sum(r['outside_reference'] for r in subset)}
    ablations={}
    for method in ['base','timing','critical_net','congestion']:
        subset=[r for r in records if r['model']==method]
        ablations[method]=dict(zip(NAMES,np.mean([r['normalized'] for r in subset],axis=0).tolist()))
    summary['ablations_normalized_to_start']=ablations
    summary['total_training_seconds']=sum(r['seconds'] for r in metadata)
    summary['total_training_episodes']=sum(r['episodes'] for r in metadata)
    summary['trained_models']=len(metadata)
    summary['evaluated_episodes']=len(records)
    summary['all_rectangles_legal']=all(r['legal'] for r in records)
    summary['execution_seconds']=time.perf_counter()-begin
    write_json(out/'summary.json',summary)
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    main()
