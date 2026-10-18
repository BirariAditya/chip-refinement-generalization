import copy
import time
import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical
from objectives import ProxyDesign, RegulationEnv, initial_layout, preferences


class Policy(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Conv2d(5,16,3,padding=1),nn.Tanh(),nn.Conv2d(16,16,1),nn.Tanh())
        self.film=nn.Linear(4,32)
        self.actor=nn.Conv2d(16,1,1)
        self.critic=nn.Sequential(nn.Linear(20,32),nn.Tanh(),nn.Linear(32,1))

    def forward(self, masks, prefs, legal):
        hidden=self.encoder(masks)
        scale,bias=self.film(prefs).chunk(2,dim=1)
        hidden=torch.tanh(hidden*(1+scale[:,:,None,None])+bias[:,:,None,None])
        logits=self.actor(hidden).flatten(1).masked_fill(~legal,-1e9)
        value=self.critic(torch.cat([hidden.mean((2,3)),prefs],dim=1)).squeeze(1)
        return Categorical(logits=logits),value


def rollout(policy,design,start,pref,training=False,timing_mode='path',chebyshev=False,control=None):
    env=RegulationEnv(design,start,pref,timing_mode,chebyshev)
    trajectory=[]
    reward_sum=0.
    begin=time.perf_counter()
    while env.index<len(env.order):
        mask,legal=env.observe()
        if control=='greedy':
            score=env.candidate_values/env.scale
            score=np.max(score*pref,axis=1) if chebyshev else score@pref
            action=int(np.argmin(np.where(legal,score,np.inf)))
        elif control=='identity':
            pos=env.positions[env.order[env.index]]
            action=int(pos[0]*10+pos[1])
        else:
            with torch.no_grad():
                dist,value=policy(torch.from_numpy(mask[None]),torch.tensor(pref[None],dtype=torch.float32),torch.from_numpy(legal[None]))
                chosen=dist.sample() if training else dist.probs.argmax(1)
                logp=float(dist.log_prob(chosen))
                action=int(chosen)
        reward,done=env.step(action)
        reward_sum+=reward
        if training:
            trajectory.append([mask,np.array(pref,dtype=np.float32),legal.copy(),action,logp,float(value),reward])
    assert env.geometry.is_legal(env.positions)
    if not chebyshev:
        assert np.isclose(reward_sum,pref@((env.initial-env.current)/env.scale))
    actual=design.costs(env.positions)[0]
    baseline=design.costs(start)[0]
    return trajectory, {'objectives':actual.tolist(),'initial':baseline.tolist(),
                        'normalized':(actual/np.maximum(baseline,[1,1,.1,.1])).tolist(),
                        'legal':True,'reward_sum':reward_sum,'positions':env.positions.tolist(),
                        'objective_candidates':env.evaluations,'seconds':time.perf_counter()-begin}


def train(seed,episodes,fixed=None,timing_mode='path',chebyshev=False):
    torch.manual_seed(seed)
    rng=np.random.default_rng(seed)
    policy=Policy()
    initial=copy.deepcopy(policy.state_dict())
    optimizer=torch.optim.Adam(policy.parameters(),lr=3e-4)
    circuits=[ProxyDesign.synthetic(s) for s in range(101,109)]
    lattice=preferences()
    logs=[]
    begin=time.perf_counter()
    for offset in range(0,episodes,8):
        if fixed is not None:
            pref=np.asarray(fixed)
        else:
            pref=lattice[int(rng.integers(len(lattice)))] if rng.random()<.5 else rng.dirichlet(np.ones(4))
        batch=[]
        for _ in range(min(8,episodes-offset)):
            design=circuits[int(rng.integers(len(circuits)))]
            start=initial_layout(design.circuit,int(rng.integers(10000000)),'uniform')
            trajectory,_=rollout(policy,design,start,pref,True,timing_mode,chebyshev)
            advantage=0.
            next_value=0.
            rows=[]
            for row in trajectory[::-1]:
                delta=row[6]+next_value-row[5]
                advantage=delta+.95*advantage
                rows.append(row[:6]+[advantage,advantage+row[5]])
                next_value=row[5]
            batch.extend(rows[::-1])
        masks=torch.tensor(np.stack([r[0] for r in batch]))
        prefs=torch.tensor(np.stack([r[1] for r in batch]))
        legal=torch.tensor(np.stack([r[2] for r in batch]))
        actions=torch.tensor([r[3] for r in batch])
        old_logp=torch.tensor([r[4] for r in batch])
        advantages=torch.tensor([r[6] for r in batch],dtype=torch.float32)
        returns=torch.tensor([r[7] for r in batch],dtype=torch.float32)
        advantages=(advantages-advantages.mean())/(advantages.std(unbiased=False)+1e-8)
        for _ in range(4):
            dist,value=policy(masks,prefs,legal)
            ratio=(dist.log_prob(actions)-old_logp).exp()
            clipped=torch.clamp(ratio,.8,1.2)*advantages
            policy_loss=-torch.min(ratio*advantages,clipped).mean()
            value_loss=(value-returns).pow(2).mean()
            entropy=dist.entropy().mean()
            loss=policy_loss+.5*value_loss-.01*entropy
            if not torch.isfinite(loss):
                raise RuntimeError('Nonfinite PPO loss')
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(),.5)
            optimizer.step()
        logs.append({'episode':min(offset+8,episodes),'loss':float(loss),'value_loss':float(value_loss),
                     'entropy':float(entropy),'approx_kl':float((old_logp-dist.log_prob(actions)).mean())})
    delta=sum(float((policy.state_dict()[k]-v).abs().sum()) for k,v in initial.items())
    return policy,{'seed':seed,'episodes':episodes,'transitions':episodes*6,'seconds':time.perf_counter()-begin,
                   'parameter_l1_change':delta,'timing_mode':timing_mode,'chebyshev':chebyshev,
                   'fixed_preference':None if fixed is None else list(fixed),'updates':logs}
