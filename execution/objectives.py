from dataclasses import dataclass
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'prototype'))
from placement_rl import Circuit, Environment, initial_layout

NAMES = ['hpwl', 'regularity', 'timing_proxy', 'overflow_proxy']


def preferences(divisions=4):
    return np.array([[a,b,c,divisions-a-b-c]
                     for a in range(divisions+1)
                     for b in range(divisions-a+1)
                     for c in range(divisions-a-b+1)], dtype=float) / divisions


@dataclass
class ProxyDesign:
    circuit: Circuit
    paths: list
    clock: float = 4.0
    linear_delay: float = 0.06
    quadratic_delay: float = 0.008
    cell_delay: float = 0.2
    capacity: float = 0.65
    blockage_fraction: float = 0.6

    @classmethod
    def synthetic(cls, seed):
        rng = np.random.default_rng(seed)
        c = Circuit.synthetic(seed)
        target = initial_layout(c, seed+20000, 'uniform')
        pins = c.pins(target)
        nets = []
        for i in range(8):
            dist = np.abs(pins-pins[i]).sum(axis=1)
            nearest = np.argsort(dist)[1:5]
            neighbors = rng.choice(nearest, 2, replace=False)
            nets.append([i, int(neighbors[0]), int(neighbors[1])])
        paths = [[6]+rng.choice(6, 3, replace=False).tolist()+[7] for _ in range(3)]
        for path in paths:
            nets.extend([[a,b] for a,b in zip(path[:-1],path[1:])])
        c.nets = nets
        c.weights = np.ones(len(nets))
        return cls(c, paths)

    def pins(self, positions):
        p = np.asarray(positions, dtype=float)
        if p.ndim == 2:
            p = p[None]
        ports = np.broadcast_to([[0,5],[10,5]], (len(p),2,2))
        return np.concatenate([p+self.circuit.sizes[None]/2, ports], axis=1)

    def demand(self, positions):
        pins = self.pins(positions)
        demand = np.zeros((len(pins),10,10))
        edges = np.arange(11, dtype=float)
        for net in self.circuit.nets:
            lower, upper = pins[:,net].min(1), pins[:,net].max(1)
            length = (upper-lower).sum(1)
            center, span = (upper+lower)/2, np.maximum(upper-lower,0.5)
            lower, upper = np.maximum(center-span/2,0), np.minimum(center+span/2,10)
            area = np.prod(upper-lower,axis=1)
            ox = np.maximum(0,np.minimum(edges[None,1:],upper[:,0,None])-np.maximum(edges[None,:-1],lower[:,0,None]))
            oy = np.maximum(0,np.minimum(edges[None,1:],upper[:,1,None])-np.maximum(edges[None,:-1],lower[:,1,None]))
            demand += length[:,None,None]/area[:,None,None]*ox[:,:,None]*oy[:,None,:]
        return demand

    def capacities(self, positions):
        p = np.asarray(positions,dtype=float)
        if p.ndim == 2:
            p = p[None]
        occupied = np.zeros((len(p),10,10))
        edges = np.arange(11,dtype=float)
        for i,size in enumerate(self.circuit.sizes):
            lo, hi = p[:,i], p[:,i]+size
            ox = np.maximum(0,np.minimum(edges[None,1:],hi[:,0,None])-np.maximum(edges[None,:-1],lo[:,0,None]))
            oy = np.maximum(0,np.minimum(edges[None,1:],hi[:,1,None])-np.maximum(edges[None,:-1],lo[:,1,None]))
            occupied += ox[:,:,None]*oy[:,None,:]
        occupied[:,4:6,4:6] += 1
        return self.capacity*(1-self.blockage_fraction*np.clip(occupied,0,1))

    def path_delays(self, positions):
        pins = self.pins(positions)
        delays = []
        for path in self.paths:
            length = np.abs(pins[:,path[:-1]]-pins[:,path[1:]]).sum(2)
            delays.append((self.linear_delay*length+self.quadratic_delay*length**2).sum(1)+self.cell_delay*len(path))
        return np.stack(delays,axis=1)

    def costs(self, positions, timing_mode='path', critical_weights=None):
        p = np.asarray(positions,dtype=float)
        if p.ndim == 2:
            p=p[None]
        pins = self.pins(p)
        lengths = np.stack([np.ptp(pins[:,net],axis=1).sum(1) for net in self.circuit.nets],axis=1)
        hpwl = lengths @ self.circuit.weights
        reg = np.minimum(p,10-self.circuit.sizes[None]-p).sum((1,2))
        if timing_mode == 'path':
            timing = np.maximum(0,self.path_delays(p)-0.95*self.clock).sum(1)
        elif timing_mode == 'critical_net':
            if critical_weights is None:
                raise ValueError('Critical-net weights must be frozen from the episode start')
            timing = lengths @ critical_weights
        else:
            raise ValueError(timing_mode)
        overflow = np.maximum(0,self.demand(p)-self.capacities(p)).sum((1,2))
        return np.stack([hpwl,reg,timing,overflow],axis=1)

    def critical_weights(self, start):
        weights = np.zeros(len(self.circuit.nets))
        critical = self.path_delays(start)[0] >= 0.95*self.clock
        for path,active in zip(self.paths,critical):
            if active:
                for a,b in zip(path[:-1],path[1:]):
                    for j,net in enumerate(self.circuit.nets):
                        if a in net and b in net:
                            weights[j] += 1
        return weights


class RegulationEnv:
    def __init__(self, design, start, preference, timing_mode='path', chebyshev=False):
        self.design=design
        self.geometry=Environment(design.circuit,start,passes=1)
        self.positions=np.array(start,dtype=float).copy()
        self.preference=np.array(preference,dtype=float)
        if self.preference.shape != (4,) or np.any(self.preference<0) or not np.isclose(self.preference.sum(),1):
            raise ValueError('Preference must be a four-element simplex vector')
        self.timing_mode=timing_mode
        self.critical_weights=design.critical_weights(start)
        self.chebyshev=chebyshev
        self.order=np.argsort(-np.prod(design.circuit.sizes,axis=1),kind='stable')
        self.index=0
        self.initial=self.costs(self.positions)[0]
        self.current=self.initial.copy()
        self.scale=np.maximum(self.initial,[1,1,0.1,0.1])
        self.evaluations=1

    def costs(self, positions):
        return self.design.costs(positions,self.timing_mode,self.critical_weights)

    def observe(self):
        macro=self.order[self.index]
        legal=self.geometry.legal_mask(macro,self.positions)
        candidates=np.repeat(self.positions[None],100,axis=0)
        candidates[:,macro]=self.geometry.grid
        values=np.repeat(self.current[None],100,axis=0)
        values[legal]=self.costs(candidates[legal])
        self.evaluations+=int(legal.sum())
        delta=(self.current-values)/self.scale
        self.candidate_values=values
        self.legal=legal
        mask=np.concatenate([legal[None],delta.T],axis=0).reshape(5,10,10)
        mask[1:] *= (self.preference>0)[:,None,None]
        return mask.astype(np.float32),legal

    def step(self, action):
        if not self.legal[action]:
            raise ValueError('Illegal placement action')
        old=self.current.copy()
        self.positions[self.order[self.index]]=self.geometry.grid[action]
        self.current=self.candidate_values[action].copy()
        self.index+=1
        done=self.index==len(self.order)
        if self.chebyshev:
            reward=-float(np.max(self.preference*self.current/self.scale)) if done else 0.
        else:
            reward=float(self.preference@((old-self.current)/self.scale))
        return reward,done


def nondominated(values):
    values=np.asarray(values,dtype=float)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError('Expected a finite matrix')
    keep=[]
    for i,v in enumerate(values):
        if np.any(np.all(values<=v,axis=1)&np.any(values<v,axis=1)):
            continue
        if not any(np.array_equal(v,values[j]) for j in keep):
            keep.append(i)
    return keep


def hypervolume(values, reference):
    ref=np.asarray(reference,dtype=float)
    points=np.asarray(values,dtype=float).reshape(-1,len(ref))
    if not np.isfinite(points).all() or not np.isfinite(ref).all():
        raise ValueError('Nonfinite hypervolume input')
    points=points[np.all(points<ref,axis=1)]
    if len(points)==0:
        return 0.
    points=points[nondominated(points)]
    if len(ref)==1:
        return float(ref[0]-points[:,0].min())
    levels=np.unique(np.append(points[:,0],ref[0]))
    return float(sum((b-a)*hypervolume(points[points[:,0]<=a,1:],ref[1:]) for a,b in zip(levels[:-1],levels[1:])))
