import unittest
import itertools
import numpy as np
import torch
from objectives import ProxyDesign, RegulationEnv, initial_layout, preferences, hypervolume, nondominated
from ppo import Policy, rollout, train


class ObjectivesTest(unittest.TestCase):
    def setUp(self):
        self.design=ProxyDesign.synthetic(101)
        self.start=initial_layout(self.design.circuit,42,'uniform')

    def test_demand_integral(self):
        pins=self.design.pins(self.start)[0]
        hpwl=sum(np.ptp(pins[net],axis=0).sum() for net in self.design.circuit.nets)
        self.assertAlmostEqual(self.design.demand(self.start).sum(),hpwl)
        self.design.circuit.nets=[[6,7],[6,6]]
        self.assertAlmostEqual(self.design.demand(self.start).sum(),10.)

    def test_candidate_masks_against_scalar(self):
        for timing in ['path','critical_net']:
            env=RegulationEnv(self.design,self.start,np.ones(4)/4,timing)
            masks,legal=env.observe()
            for action in np.flatnonzero(legal)[::7]:
                candidate=self.start.copy()
                candidate[env.order[0]]=env.geometry.grid[action]
                scalar=env.costs(candidate)[0]
                np.testing.assert_allclose(env.candidate_values[action],scalar)
                np.testing.assert_allclose(masks[1:].reshape(4,100)[:,action],(env.initial-scalar)/env.scale,atol=1e-6)
            with self.assertRaises(ValueError):
                env.step(int(np.flatnonzero(~legal)[0]))

    def test_reward_telescopes(self):
        _,result=rollout(None,self.design,self.start,np.ones(4)/4,control='greedy')
        self.assertTrue(result['legal'])
        _,result=rollout(None,self.design,self.start,np.ones(4)/4,chebyshev=True,control='greedy')
        self.assertAlmostEqual(result['reward_sum'],-max(np.array(result['normalized'])/4))

    def test_preferences_and_pareto(self):
        p=preferences()
        self.assertEqual(p.shape,(35,4))
        np.testing.assert_allclose(p.sum(1),1)
        for e in np.eye(4):
            self.assertTrue(np.any(np.all(p==e,axis=1)))
        self.assertEqual(nondominated([[1,3],[2,2],[3,1],[4,4],[1,3]]),[0,1,2])

    def test_hypervolume_independent_inclusion_exclusion(self):
        p=np.array([[.2,.4,.3,.5],[.4,.2,.5,.3],[.3,.3,.3,.3]])
        expected=0.
        for size in range(1,4):
            for subset in itertools.combinations(p,size):
                expected+=(-1)**(size+1)*np.prod(1-np.max(subset,axis=0))
        self.assertAlmostEqual(hypervolume(p,np.ones(4)),expected)
        self.assertEqual(hypervolume([[2,2,2,2]],np.ones(4)),0.)

    def test_overflow_capacity_and_demand_update(self):
        self.assertTrue(np.all(self.design.capacities(self.start)>=0))
        env=RegulationEnv(self.design,self.start,np.ones(4)/4)
        _,legal=env.observe()
        candidate=self.start.copy()
        candidate[env.order[0]]=env.geometry.grid[np.flatnonzero(legal)[0]]
        self.assertFalse(np.allclose(self.design.demand(candidate),self.design.demand(self.start)))
        self.assertFalse(np.allclose(self.design.capacities(candidate),self.design.capacities(self.start)))

    def test_timing_formula(self):
        pins=self.design.pins(self.start)[0]
        expected=[]
        for path in self.design.paths:
            total=self.design.cell_delay*len(path)
            for a,b in zip(path[:-1],path[1:]):
                length=abs(pins[a]-pins[b]).sum()
                total+=self.design.linear_delay*length+self.design.quadratic_delay*length**2
            expected.append(total)
        np.testing.assert_allclose(self.design.path_delays(self.start)[0],expected)

    def test_policy_mask_and_updates(self):
        torch.set_num_threads(1)
        env=RegulationEnv(self.design,self.start,np.ones(4)/4)
        mask,legal=env.observe()
        dist,value=Policy()(torch.tensor(mask[None]),torch.ones((1,4))/4,torch.tensor(legal[None]))
        self.assertTrue(torch.isfinite(value).all())
        self.assertTrue(torch.all(dist.probs[0,~torch.tensor(legal)]==0))
        _,meta=train(7,8,fixed=np.array([.7,.3,0,0]))
        self.assertGreater(meta['parameter_l1_change'],0)


if __name__=='__main__':
    unittest.main(verbosity=2)
