---
title: "ROCKET-3: Scalable Multi-Task RL for Generalizable Spatial Intelligence in Visuomotor Agents"
authors: ["Shaofei Cai*", "Zhancun Mu*", "Haiwen Xia", "Bowei Zhang", "Anji Liu", "Yitao Liang"]
venue: "arXiv preprint"
year: 2025
publishDate: 2025-07-18
type: preprint
abstract: "We introduce ROCKET-3, a scalable reinforcement learning framework for training visuomotor agents in Minecraft. ROCKET-3 leverages large-scale automated task synthesis, a distributed RL framework, and cross-view goal specification to achieve powerful zero-shot generalization in unseen 3D worlds."
teaser: "/images/ROCKET-3.png"
links:
  paper: "https://arxiv.org/abs/2507.23698"
  code: "https://github.com/CraftJarvis/ROCKET-3"
  project: "https://craftjarvis.github.io/ROCKET-3/"
tags: ["Minecraft", "Agent", "Goal Conditioned Policy", "Pre-training", "Reinforcement Learning"]
---

## Abstract

We present ROCKET-3, a scalable multi-task reinforcement learning framework for generalizable spatial intelligence in visuomotor agents. Built on large-scale automated task synthesis and a distributed RL framework, ROCKET-3 enables agents to generalize to unseen worlds via cross-view goal specification.

## Key Contributions

1. **Large-Scale Task Synthesis**: Automated generation of over 100,000 Minecraft training tasks, supporting robust multi-task RL.
2. **Efficient Distributed RL Framework**: Stable and scalable RL training for long-sequence visuomotor policies using a memory-efficient, fragment-based storage system.
3. **Cross-View Goal Specification**: Unified task space that enables generalization across domains and supports curriculum learning.
4. **Powerful Generalization**: Empirical evidence of 4x improvement in interaction success rates and compelling zero-shot transfer to DMLab, Unreal Engine, and real-world robots.

## Methodology

ROCKET-3 employs a "Foundation-to-Finesse" pipeline:
- **Imitation Learning Pre-Training**: Learning from large-scale expert trajectories for foundational skills.
- **RL Fine-Tuning**: PPO-based RL with KL-divergence constraint for stable policy refinement.
- **Cross-View Goal Specification (CVGS)**: Task representation enabling spatial reasoning and transferability.
- **Distributed Training**: Parallelized data collection (72 Minecraft instances, ~1000 FPS) and memory-efficient storage.

## Results

ROCKET-3 achieves state-of-the-art performance in Minecraft, with:
- 4x increase in average success rate (7% → 28%) across diverse tasks.
- Zero-shot generalization to unseen 3D environments, including simulated and real-world settings.
- Robust curriculum learning and spatial reasoning capabilities.

## Future Work

We aim to extend RL training to more diverse 3D environments and action spaces, further bridging the sim-to-real gap for embodied AI and robotics.