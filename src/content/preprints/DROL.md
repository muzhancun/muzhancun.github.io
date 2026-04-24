---
title: "Preserve Support, Not Correspondence: Dynamic Routing for Offline Reinforcement Learning"
authors: ["Zhancun Mu", "Guangyu Zhao", "Yiwu Zhong", "Chi Zhang"]
venue: "Preprint"
year: 2026
publishDate: 2026-04-24
type: preprint
abstract: >-
  One-step offline RL actors are attractive because they avoid backpropagating through long iterative samplers and keep inference cheap, but they still have to improve under a critic without drifting away from actions that the dataset can support. We propose DROL, a latent-conditioned one-step actor trained with top-1 dynamic routing. For each state, the actor samples K candidate actions from a bounded latent prior, assigns each dataset action to its nearest candidate, and updates only that winner with behavior cloning and critic guidance. Because the routing is recomputed from the current candidate geometry, ownership of a supported region can shift across candidates over the course of learning. On OGBench and D4RL, DROL is competitive with the one-step FQL baseline, improving many OGBench task groups while remaining strong on both AntMaze and Adroit.
teaser: "/images/drol.png"
links:
  code: "https://github.com/muzhancun/DROL"
  project: "https://muzhancun.github.io/DROL"
tags: ["Offline RL", "Reinforcement Learning"]
slug: DROL
---

## Introduction

Offline reinforcement learning needs to improve a policy while staying within action regions supported by a fixed dataset. This becomes difficult on multimodal benchmarks such as OGBench [@ogbench_park2025], where nearby states can admit several distinct but reasonable actions.

Many strong generative offline RL methods rely on iterative sampling during training, inference, or both. A one-step actor avoids that cost, but pointwise extraction methods such as Flow Q-Learning (FQL) [@fql_park2025] can force the same sampled output to both move toward higher value and stay close to its paired teacher endpoint. When those directions disagree, the update becomes a compromise on that sample.

DROL argues that the useful constraint is local support, not fixed latent-to-teacher correspondence. If responsibility for a supported region can transfer across candidates during training, one candidate can move toward a better local action while another retains the old neighborhood.

## Method

DROL keeps a latent-conditioned one-step actor, but changes how behavior support is regularized during training. For each state, it samples a candidate set:

$$
A_\theta(s) = \{\hat a^1, \dots, \hat a^K\}, \qquad \hat a^k = f_\theta(s, z_k).
$$

Each dataset action is routed to its nearest current candidate:

$$
k^*(s,a)=\arg\min_{k \in [K]} \|\hat a^k-a\|_2^2.
$$

Only the routed winner receives the behavior cloning and critic-guided actor update. Because routing is recomputed at every gradient step, candidate ownership can change as the actor geometry evolves. At test time, DROL uses a single latent sample, so deployment remains in the plain one-step setting.

## Theory

DROL is motivated by three local observations about routed actor updates. The goal is not to prove global offline RL convergence, but to explain why winner-only routing can preserve support while still allowing critic-guided improvement.

### Separated Neighborhoods Avoid Collapse

In a local state neighborhood with several separated action regions, routed behavior cloning behaves like a local quantization objective. If two candidates serve the same supported region while another region has none, the average reconstruction distance increases. A simple one-dimensional separated-interval model shows that, when the number of candidates matches the number of separated regions, every global minimizer places one prototype in each interval. This explains why winner-only updates do not necessarily collapse all candidates to one mean action.

### Routing Replaces a Persistent Tether

Pointwise extraction keeps a fixed pullback term between a sampled output and its paired teacher endpoint. For a single candidate $x$ and target $a$, the local objective

$$
\ell_{\mathrm{fix}}(x;a)=\|x-a\|_2^2-\alpha Q_\phi(s,x)
$$

always contains the same tether $2(x-a)$. Under routing, the behavior cloning term is attached only to the nearest candidate. If another candidate becomes closer to the same target, the pullback transfers to that new winner. This lets one candidate move toward a higher-value action while another takes over the old supported neighborhood.

### Larger K Improves Handoff Availability

The routing budget $K$ controls how many local actions are visible during a training update. If a reachable modal neighborhood has probability $p_m(s)$ of being hit by one latent sample, then the probability that a $K$-candidate set covers all reachable neighborhoods is lower bounded by

$$
1-\sum_m (1-p_m(s))^K.
$$

Increasing $K$ does not create new supported actions; it makes it less likely that the current candidate set misses a reachable local mode. This is why large or highly multimodal task families can benefit from a larger routing budget.

## Experiments

DROL is evaluated on OGBench [@ogbench_park2025] and D4RL [@d4rl_fu2020]. The experiments ask whether routed training can make a plain one-step actor competitive with stronger generative offline RL baselines, whether candidate sets actually avoid collapse, and how the routing budget $K$ affects performance.

### Benchmark Results

`DROL(16)` uses a fixed default routing budget of $K=16$. `DROL*` keeps the rest of the training setup unchanged and selects $K$ once for each benchmark family.

![Offline RL results on OGBench and D4RL](/images/research/drol/offline_results_table.png)

With the fixed default configuration, DROL matches or improves over the one-step FQL baseline on most OGBench groups, including clear gains on antmaze-large, humanoidmaze-medium, antsoccer, cube-single, and puzzle-3x3. With benchmark-family K selection, DROL* improves or matches FQL on 9 of the 10 OGBench groups and remains close on D4RL.

### Mechanism Visualizations

![Voronoi evolution during routed training](/images/research/drol/voronoi_evolution.png)

The Voronoi visualization shows how the candidate set induces local responsibility regions. Early in training, candidates spread rather than collapse. Later, two common regimes appear: one candidate can hand off responsibility to another, or the same candidate can keep responsibility while making a stable local improvement.

![Candidate scaling metrics](/images/research/drol/k_training_metrics_examples.png)

The candidate-scaling curves show that larger $K$ increases candidate spread and lowers routed behavior-cloning loss. This is consistent with the theory: larger candidate sets provide finer local coverage of supported action neighborhoods rather than simply duplicating the same action.

![Training and inference runtime](/images/research/drol/manual_runtime_plot_rerender.png)

The runtime comparison separates training-time candidate evaluation from deployment. Training cost grows with $K$, but inference remains cheap because the final policy still uses a single latent sample and one actor pass.

![Representative K sweeps](/images/research/drol/k_sweep_representative.png)

The K-sweep results show that $K$ is a routing-capacity parameter, not a monotone performance knob. Large multimodal navigation families often benefit from higher $K$, while other environments saturate earlier or prefer intermediate values.

## Conclusion

DROL studies one-step actor learning in multimodal offline RL from a geometric perspective. Instead of preserving a fixed pointwise correspondence between each latent sample and a teacher endpoint, it preserves support through a routed candidate set. This lets responsibility transfer as optimization progresses: one candidate can follow the critic toward a better local action while another remains available to cover the old supported region.

The method keeps deployment close to standard one-step baselines because multiple candidates are used only during training. Its limitations are also clear: the theory is local rather than a full convergence proof, the method depends on a fixed routing budget $K$, Euclidean nearest-neighbor matching, and extra training-time candidate evaluations. Natural next steps include learned routing metrics, adaptive candidate budgets, softer responsibility sharing, and region-level support regularization.

## Citations
